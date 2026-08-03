#!/usr/local/bin/av inject +APPLE_PASSWORD -- /bin/bash
# --- automic-vault
# capabilities:
#   aws: full
# ---

set -euo pipefail

use_color=false
if [[ -t 2 && -z "${NO_COLOR:-}" && "${TERM:-}" != "dumb" ]]; then
  use_color=true
fi

if [[ "${use_color}" == true ]]; then
  bold=$'\033[1m'
  dim=$'\033[2m'
  red=$'\033[31m'
  green=$'\033[32m'
  blue=$'\033[34m'
  yellow=$'\033[33m'
  reset=$'\033[0m'
  glyph_step="◆"
  glyph_ok="✓"
  glyph_warn="!"
  glyph_error="✗"
else
  bold=""
  dim=""
  red=""
  green=""
  blue=""
  yellow=""
  reset=""
  glyph_step=">"
  glyph_ok="OK"
  glyph_warn="WARN"
  glyph_error="ERROR"
fi

log() {
  printf '%s\n' "$*" >&2
}

log_header() {
  log "${bold}Deploying ${WWW_DOMAIN:-www}${reset}"
  if [[ "${prepare_only:-false}" == true ]]; then
    log "${dim}Static site preparation only${reset}"
  elif [[ "${static_only:-false}" == true ]]; then
    log "${dim}Static site -> S3${reset}"
  else
    log "${dim}Static site -> S3 -> CloudFront${reset}"
  fi
}

log_step() {
  log "${blue}${glyph_step}${reset} ${bold}$*${reset}"
}

log_ok() {
  log "  ${green}${glyph_ok}${reset} $*"
}

log_warn() {
  log "  ${yellow}${glyph_warn}${reset} $*"
}

log_error() {
  log "${red}${glyph_error}${reset} $*"
}

die() {
  log_error "$*"
  exit 1
}

on_error() {
  local line="$1"
  log_error "Deployment failed near line ${line}."
  log "${dim}Deployment modes also require AWS CLI credentials and .envrc values.${reset}"
}

trap 'on_error "$LINENO"' ERR

static_only=false
prepare_only=false

usage() {
  cat >&2 <<'EOF'
Usage: deploy-www.sh [--static-only] [--prepare-only]

Options:
  --static-only  Sync prepared website files to S3 without changing CloudFront,
                 bucket policy, redirects, or certificates.
  --prepare-only Prepare and validate deploy-time website content without AWS
                 changes.
  -h, --help     Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --static-only)
      static_only=true
      shift
      ;;
    --prepare-only)
      prepare_only=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      die "Unknown option: $1"
      ;;
  esac
done

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    die "Set ${name} in .envrc."
  fi
}

required_tools=(node python3)
if [[ "${prepare_only}" != true ]]; then
  required_tools+=(aws)
fi
if [[ "${prepare_only}" != true && "${static_only}" != true ]]; then
  required_tools+=(jq zip)
fi

for tool in "${required_tools[@]}"; do
  command -v "$tool" >/dev/null 2>&1 || {
    die "Missing required tool: ${tool}."
  }
done

WWW_EMERGENCY_INVALIDATE="${WWW_EMERGENCY_INVALIDATE:-false}"

script_dir="$(cd "$(dirname "${AV_SCRIPT_PATH:-$0}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
site_dir="${repo_root}/www"
llms_full_generator="${repo_root}/scripts/generate-llms-full.mjs"
www_i18n_generator="${repo_root}/scripts/generate-www-i18n.py"
release_redirect_source="${repo_root}/lambda/release-redirect/index.mjs"
prepared_site_dir=""
temp_paths=()

if [[ ! -d "${site_dir}" ]]; then
  die "Missing site directory: ${site_dir}"
fi

if [[ "${prepare_only}" != true ]]; then
  require_env AWS_REGION
  require_env WWW_DOMAIN

  export WWW_WWW_DOMAIN="${WWW_WWW_DOMAIN:-www.${WWW_DOMAIN}}"
  export WWW_CANONICAL_HOST="${WWW_CANONICAL_HOST:-${WWW_WWW_DOMAIN}}"
  export WWW_BUCKET="${WWW_BUCKET:-${WWW_DOMAIN}}"
  export WWW_CLOUDFRONT_PRICE_CLASS="${WWW_CLOUDFRONT_PRICE_CLASS:-PriceClass_100}"
  export WWW_HTML_CACHE_CONTROL="${WWW_HTML_CACHE_CONTROL:-public, max-age=60, must-revalidate}"
  export WWW_CSS_CACHE_CONTROL="${WWW_CSS_CACHE_CONTROL:-public, max-age=3600}"
  export WWW_PREVIEW_CACHE_CONTROL="${WWW_PREVIEW_CACHE_CONTROL:-public, max-age=3600, must-revalidate}"
  export WWW_ASSET_CACHE_CONTROL="${WWW_ASSET_CACHE_CONTROL:-public, max-age=31536000, immutable}"

  for env_name in \
    WWW_BUCKET \
    WWW_HTML_CACHE_CONTROL \
    WWW_CSS_CACHE_CONTROL \
    WWW_PREVIEW_CACHE_CONTROL \
    WWW_ASSET_CACHE_CONTROL
  do
    require_env "${env_name}"
  done

  if [[ "${static_only}" != true ]]; then
    for env_name in \
      WWW_WWW_DOMAIN \
      WWW_CANONICAL_HOST \
      WWW_CERTIFICATE_ARN \
      WWW_CLOUDFRONT_PRICE_CLASS
    do
      require_env "${env_name}"
    done
  fi

  release_redirect_origin_id="${WWW_DOMAIN}-release-redirect-origin"
  distribution_comment="${WWW_DOMAIN} static site"
  oac_name="${WWW_DOMAIN}-s3-oac"
  release_redirect_oac_name="${WWW_DOMAIN//./-}-release-redirect-oac"
  release_redirect_function_name="${WWW_DOMAIN//./-}-release-redirect"
  release_redirect_role_name="${WWW_DOMAIN//./-}-release-redirect-role"
  redirect_function_name="${WWW_DOMAIN//./-}-redirect-to-canonical"
  response_headers_policy_name="${WWW_DOMAIN//./-}-security-headers"
  cache_policy_name="${WWW_DOMAIN//./-}-brotli-cache"
  release_redirect_cache_policy_id="658327ea-f89d-4fab-a63d-7e88639e58f6"
fi

make_temp_file() {
  local target_var="$1"
  local path
  path="$(mktemp)"
  temp_paths+=("${path}")
  printf -v "${target_var}" '%s' "${path}"
}

make_temp_dir() {
  local target_var="$1"
  local path
  path="$(mktemp -d)"
  temp_paths+=("${path}")
  printf -v "${target_var}" '%s' "${path}"
}

cleanup() {
  local path
  if [[ -z "${temp_paths[*]-}" ]]; then
    return
  fi
  for path in "${temp_paths[@]}"; do
    if [[ -d "${path}" && ! -L "${path}" ]]; then
      rm -rf "${path}"
    else
      rm -f "${path}"
    fi
  done
}

trap cleanup EXIT

prepare_site_for_upload() {
  log_step "Preparing site content"
  make_temp_dir prepared_site_dir
  rsync -a "${site_dir}/" "${prepared_site_dir}/"
  node "${llms_full_generator}" "${prepared_site_dir}" "${prepared_site_dir}/llms-full.txt"
  log_ok "Site content prepared"
}

assert_www_i18n_current() {
  log_step "Checking localized website pages"
  if [[ ! -x "${www_i18n_generator}" && ! -f "${www_i18n_generator}" ]]; then
    die "Missing website i18n generator: ${www_i18n_generator}"
  fi
  python3 "${www_i18n_generator}" --check
}

ensure_bucket() {
  log_step "Preparing S3 bucket"
  if ! aws s3api head-bucket --bucket "${WWW_BUCKET}" >/dev/null 2>&1; then
    log "  Creating ${WWW_BUCKET}"
    if [[ "${AWS_REGION}" == "us-east-1" ]]; then
      aws s3api create-bucket --bucket "${WWW_BUCKET}"
    else
      aws s3api create-bucket \
        --bucket "${WWW_BUCKET}" \
        --create-bucket-configuration \
        "LocationConstraint=${AWS_REGION}"
    fi
  else
    log "  Bucket exists: ${WWW_BUCKET}"
  fi

  log "  Blocking public access"
  aws s3api put-public-access-block \
    --bucket "${WWW_BUCKET}" \
    --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

  log "  Enforcing bucket-owner object ownership"
  aws s3api put-bucket-ownership-controls \
    --bucket "${WWW_BUCKET}" \
    --ownership-controls 'Rules=[{ObjectOwnership=BucketOwnerEnforced}]'

  log "  Enabling AES256 server-side encryption"
  aws s3api put-bucket-encryption \
    --bucket "${WWW_BUCKET}" \
    --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
  log_ok "S3 bucket ready"
}

configure_static_origin() {
  local bucket_region
  bucket_region="$(
    aws s3api get-bucket-location \
      --bucket "${WWW_BUCKET}" \
      --query 'LocationConstraint' \
      --output text
  )"
  if [[ -z "${bucket_region}" || "${bucket_region}" == "None" ]]; then
    bucket_region="us-east-1"
  fi

  if [[ "${bucket_region}" == "us-east-1" ]]; then
    origin_domain="${WWW_BUCKET}.s3.amazonaws.com"
  else
    origin_domain="${WWW_BUCKET}.s3.${bucket_region}.amazonaws.com"
  fi
  log_ok "Static origin resolved in ${bucket_region}"
}

ensure_oac() {
  local existing_id
  log_step "Preparing CloudFront origin access control"
  existing_id="$(
    aws cloudfront list-origin-access-controls \
      --query "OriginAccessControlList.Items[?Name==\`${oac_name}\`].Id | [0]" \
      --output text
  )"

  if [[ -n "${existing_id}" && "${existing_id}" != "None" ]]; then
    log_ok "Using existing OAC ${existing_id}"
    printf '%s\n' "${existing_id}"
    return 0
  fi

  local config_file created_id
  make_temp_file config_file
  jq -n \
    --arg name "${oac_name}" \
    '{
      Name: $name,
      Description: "Origin access control for static site bucket",
      OriginAccessControlOriginType: "s3",
      SigningBehavior: "always",
      SigningProtocol: "sigv4"
    }' >"${config_file}"

  created_id="$(
    aws cloudfront create-origin-access-control \
    --origin-access-control-config "file://${config_file}" \
    --query 'OriginAccessControl.Id' \
    --output text
  )"
  log_ok "Created OAC ${created_id}"
  printf '%s\n' "${created_id}"
}

ensure_release_redirect_oac() {
  local existing_id config_file
  log_step "Preparing release redirect origin access control"
  existing_id="$(
    aws cloudfront list-origin-access-controls \
      --query "OriginAccessControlList.Items[?Name==\`${release_redirect_oac_name}\`].Id | [0]" \
      --output text
  )"
  if [[ -n "${existing_id}" && "${existing_id}" != "None" ]]; then
    log_ok "Using existing release redirect OAC ${existing_id}"
    release_redirect_oac_id="${existing_id}"
    return
  fi

  make_temp_file config_file
  jq -n \
    --arg name "${release_redirect_oac_name}" \
    '{
      Name: $name,
      Description: "CloudFront access to the release redirect Lambda",
      OriginAccessControlOriginType: "lambda",
      SigningBehavior: "always",
      SigningProtocol: "sigv4"
    }' >"${config_file}"
  release_redirect_oac_id="$(aws cloudfront create-origin-access-control \
    --origin-access-control-config "file://${config_file}" \
    --query 'OriginAccessControl.Id' \
    --output text)"
  log_ok "Created release redirect OAC ${release_redirect_oac_id}"
}

ensure_release_redirect() {
  local archive_dir function_url log_group role_arn trust_file policy_file role_created=false
  log_step "Deploying GitHub release redirect Lambda"
  [[ -f "${release_redirect_source}" ]] || die "Missing release redirect source: ${release_redirect_source}"

  log_group="/aws/lambda/${release_redirect_function_name}"
  if [[ "$(aws logs describe-log-groups \
    --log-group-name-prefix "${log_group}" \
    --query "length(logGroups[?logGroupName == \`${log_group}\`])" \
    --output text)" == "0" ]]; then
    aws logs create-log-group --log-group-name "${log_group}"
  fi
  aws logs put-retention-policy --log-group-name "${log_group}" --retention-in-days 30

  make_temp_file trust_file
  jq -n '{
    Version: "2012-10-17",
    Statement: [{
      Effect: "Allow",
      Principal: {Service: "lambda.amazonaws.com"},
      Action: "sts:AssumeRole"
    }]
  }' >"${trust_file}"
  if aws iam get-role --role-name "${release_redirect_role_name}" >/dev/null 2>&1; then
    aws iam update-assume-role-policy \
      --role-name "${release_redirect_role_name}" \
      --policy-document "file://${trust_file}"
  else
    aws iam create-role \
      --role-name "${release_redirect_role_name}" \
      --assume-role-policy-document "file://${trust_file}" >/dev/null
    role_created=true
  fi
  role_arn="$(aws iam get-role --role-name "${release_redirect_role_name}" --query Role.Arn --output text)"

  make_temp_file policy_file
  jq -n \
    --arg log_arn "arn:aws:logs:${AWS_REGION}:${AWS_ACCOUNT_ID}:log-group:${log_group}:*" \
    '{
      Version: "2012-10-17",
      Statement: [{
        Effect: "Allow",
        Action: ["logs:CreateLogStream", "logs:PutLogEvents"],
        Resource: $log_arn
      }]
    }' >"${policy_file}"
  aws iam put-role-policy \
    --role-name "${release_redirect_role_name}" \
    --policy-name logs \
    --policy-document "file://${policy_file}"
  if [[ "${role_created}" == true ]]; then
    sleep 5
  fi

  make_temp_dir archive_dir
  cp "${release_redirect_source}" "${archive_dir}/index.mjs"
  (cd "${archive_dir}" && zip -q release-redirect.zip index.mjs)
  if aws lambda get-function --function-name "${release_redirect_function_name}" >/dev/null 2>&1; then
    aws lambda update-function-configuration \
      --function-name "${release_redirect_function_name}" \
      --runtime nodejs24.x \
      --handler index.handler \
      --role "${role_arn}" \
      --timeout 10 \
      --memory-size 128 >/dev/null
    aws lambda wait function-updated --function-name "${release_redirect_function_name}"
    aws lambda update-function-code \
      --function-name "${release_redirect_function_name}" \
      --architectures arm64 \
      --zip-file "fileb://${archive_dir}/release-redirect.zip" >/dev/null
  else
    aws lambda create-function \
      --function-name "${release_redirect_function_name}" \
      --runtime nodejs24.x \
      --handler index.handler \
      --role "${role_arn}" \
      --architectures arm64 \
      --timeout 10 \
      --memory-size 128 \
      --zip-file "fileb://${archive_dir}/release-redirect.zip" >/dev/null
  fi
  aws lambda wait function-updated --function-name "${release_redirect_function_name}"

  if aws lambda get-function-url-config --function-name "${release_redirect_function_name}" >/dev/null 2>&1; then
    aws lambda update-function-url-config \
      --function-name "${release_redirect_function_name}" \
      --auth-type AWS_IAM >/dev/null
  else
    aws lambda create-function-url-config \
      --function-name "${release_redirect_function_name}" \
      --auth-type AWS_IAM >/dev/null
  fi
  function_url="$(aws lambda get-function-url-config --function-name "${release_redirect_function_name}" --query FunctionUrl --output text)"
  release_redirect_domain="$(printf '%s\n' "${function_url#https://}" | sed 's|/$||')"
  log_ok "Release redirect Lambda ready"
}

allow_cloudfront_release_redirect() {
  local distribution_id="$1"
  local source_arn="arn:aws:cloudfront::${AWS_ACCOUNT_ID}:distribution/${distribution_id}"
  log_step "Restricting release redirect Lambda to CloudFront"
  aws lambda remove-permission --function-name "${release_redirect_function_name}" --statement-id cloudfront-url >/dev/null 2>&1 || true
  aws lambda remove-permission --function-name "${release_redirect_function_name}" --statement-id cloudfront-invoke >/dev/null 2>&1 || true
  aws lambda add-permission \
    --function-name "${release_redirect_function_name}" \
    --statement-id cloudfront-url \
    --action lambda:InvokeFunctionUrl \
    --principal cloudfront.amazonaws.com \
    --source-arn "${source_arn}" \
    --function-url-auth-type AWS_IAM >/dev/null
  aws lambda add-permission \
    --function-name "${release_redirect_function_name}" \
    --statement-id cloudfront-invoke \
    --action lambda:InvokeFunction \
    --principal cloudfront.amazonaws.com \
    --source-arn "${source_arn}" \
    --invoked-via-function-url >/dev/null
  log_ok "Release redirect access restricted"
}

ensure_redirect_function() {
  local function_file function_etag stage
  log_step "Publishing canonical-host redirect function"
  make_temp_file function_file
  cat >"${function_file}" <<EOF
function handler(event) {
  var request = event.request;
  var host = request.headers.host.value;
  var canonicalHost = "${WWW_CANONICAL_HOST}";

  function preferredContentType() {
    var header = request.headers.accept && request.headers.accept.value;
    var supported = ["text/html", "text/markdown", "text/plain", "application/json"];
    var bestType = "text/html";
    var bestQ = -1;
    var bestOrder = 999999;
    var bestSpecificity = -1;

    if (!header) {
      return bestType;
    }

    var ranges = header.split(",");
    for (var order = 0; order < ranges.length; order++) {
      var range = ranges[order].replace(/^\s+|\s+$/g, "");
      if (!range) {
        continue;
      }
      var parts = range.split(";");
      var media = parts[0].replace(/^\s+|\s+$/g, "").toLowerCase();
      var q = 1;

      for (var paramIndex = 1; paramIndex < parts.length; paramIndex++) {
        var param = parts[paramIndex].replace(/^\s+|\s+$/g, "").toLowerCase();
        if (param.slice(0, 2) === "q=") {
          var parsedQ = parseFloat(param.slice(2));
          q = isNaN(parsedQ) ? 0 : parsedQ;
        }
      }

      if (q <= 0) {
        continue;
      }

      for (var typeIndex = 0; typeIndex < supported.length; typeIndex++) {
        var candidate = supported[typeIndex];
        var specificity = -1;
        if (media === candidate) {
          specificity = 2;
        } else if (media.slice(-2) === "/*" && candidate.indexOf(media.slice(0, media.length - 1)) === 0) {
          specificity = 1;
        } else if (media === "*/*") {
          specificity = 0;
        }

        if (specificity < 0) {
          continue;
        }
        if (
          q > bestQ ||
          (q === bestQ && order < bestOrder) ||
          (q === bestQ && order === bestOrder && specificity > bestSpecificity)
        ) {
          bestType = candidate;
          bestQ = q;
          bestOrder = order;
          bestSpecificity = specificity;
        }
      }
    }

    return bestType;
  }

  function isKnownRoute(uri) {
    var routes = {
      "/": true,
      "/about": true,
      "/about/": true,
      "/docs": true,
      "/docs/": true,
      "/download": true,
      "/download/": true,
      "/privacy": true,
      "/privacy/": true,
      "/terms": true,
      "/terms/": true
    };
    return routes[uri] === true;
  }

  function retiredLocation(uri) {
    var prefixes = ["/de", "/fr", "/ja", "/zh-hans"];
    for (var i = 0; i < prefixes.length; i++) {
      if (uri.indexOf(prefixes[i] + "/") === 0) {
        uri = uri.slice(prefixes[i].length);
        break;
      }
    }
    if (uri.length > 1 && uri.slice(-1) === "/") {
      uri = uri.slice(0, -1);
    }
    var routes = {
      "/ai-agent-approval-gates": "https://" + canonicalHost + "/#controls",
      "/api-key-management-for-ai-agents": "https://" + canonicalHost + "/",
      "/av-trace": "https://" + canonicalHost + "/",
      "/github-cli-token-security-ai-agents": "https://" + canonicalHost + "/",
      "/hashicorp-vault-for-ai-agents": "https://" + canonicalHost + "/",
      "/mcp-secrets-management": "https://" + canonicalHost + "/",
      "/pricing": "https://" + canonicalHost + "/#pricing",
      "/privileged-access-management-for-ai-agents": "https://" + canonicalHost + "/",
      "/secret-scanner-for-ai-agents": "https://" + canonicalHost + "/#threats",
      "/secret-scanning-vs-agent-secret-protection": "https://" + canonicalHost + "/#threats",
      "/secrets-manager-for-ai-agents": "https://" + canonicalHost + "/",
      "/secure-aws-cli-credentials-ai-agents": "https://" + canonicalHost + "/",
      "/security": "https://github.com/automic-vault/automic-vault/security",
      "/security/whitepaper": "https://github.com/automic-vault/automic-vault/security",
      "/stop-ai-agents-reading-env-files": "https://" + canonicalHost + "/",
      "/blog/agent-pack": "https://" + canonicalHost + "/blog/",
      "/blog/agentic-toolkit": "https://" + canonicalHost + "/blog/",
      "/blog/unix-plus-plus": "https://" + canonicalHost + "/blog/"
    };
    return routes[uri] || "";
  }

  function jsonNotFound() {
    return {
      statusCode: 404,
      statusDescription: "Not Found",
      headers: {
        "content-type": { value: "application/json; charset=utf-8" }
      },
      body: JSON.stringify({ error: "not_found", path: request.uri })
    };
  }

  function appendQueryString(location) {
    if (request.querystring && Object.keys(request.querystring).length > 0) {
      var parts = [];
      for (var key in request.querystring) {
        if (!Object.prototype.hasOwnProperty.call(request.querystring, key)) {
          continue;
        }
        var entry = request.querystring[key];
        if (entry.multiValue) {
          for (var i = 0; i < entry.multiValue.length; i++) {
            var item = entry.multiValue[i];
            parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(item.value));
          }
        } else {
          parts.push(encodeURIComponent(key) + "=" + encodeURIComponent(entry.value));
        }
      }
      if (parts.length > 0) {
        return location + "?" + parts.join("&");
      }
    }
    return location;
  }

  function viewerProtocol() {
    var header = request.headers["cloudfront-forwarded-proto"];
    return header && header.value ? header.value.toLowerCase() : "https";
  }

  function canonicalLocation(uri) {
    return appendQueryString("https://" + canonicalHost + uri);
  }

  function packageLocation(uri) {
    var landingPages = {
      "/pkg": "/",
      "/pkg/": "/",
      "/de/pkg": "/de/",
      "/de/pkg/": "/de/",
      "/fr/pkg": "/fr/",
      "/fr/pkg/": "/fr/",
      "/ja/pkg": "/ja/",
      "/ja/pkg/": "/ja/",
      "/zh-hans/pkg": "/zh-hans/",
      "/zh-hans/pkg/": "/zh-hans/"
    };
    if (landingPages[uri]) {
      return appendQueryString("https://pkg.so" + landingPages[uri]);
    }
    return appendQueryString("https://pkg.so" + uri);
  }

  function isPackageOriginPath(uri) {
    var prefixes = ["/pkg", "/de/pkg", "/fr/pkg", "/ja/pkg", "/zh-hans/pkg"];
    for (var i = 0; i < prefixes.length; i++) {
      var prefix = prefixes[i];
      if (uri === prefix || uri.indexOf(prefix + "/") === 0) {
        return true;
      }
    }
    return false;
  }

  if (isPackageOriginPath(request.uri)) {
    return {
      statusCode: 301,
      statusDescription: "Moved Permanently",
      headers: {
        location: { value: packageLocation(request.uri) }
      }
    };
  }

  if (host !== canonicalHost || viewerProtocol() === "http") {
    return {
      statusCode: 301,
      statusDescription: "Moved Permanently",
      headers: {
        location: { value: canonicalLocation(request.uri) }
      }
    };
  }
  var retired = retiredLocation(request.uri);
  if (retired) {
    return {
      statusCode: 301,
      statusDescription: "Moved Permanently",
      headers: {
        location: { value: retired }
      }
    };
  }
  if (isPackageOriginPath(request.uri)) {
    return request;
  }
  if (request.uri === "/install.sh" || request.uri === "/scanner.sh" || request.uri === "/scanner.gz") {
    return request;
  }

  var preferredType = preferredContentType();
  if (request.uri === "/" || request.uri === "/index.html") {
    if (preferredType === "text/markdown") {
      request.uri = "/index.md";
    } else if (preferredType === "text/plain") {
      request.uri = "/index.txt";
    } else if (preferredType === "application/json") {
      request.uri = "/index.json";
    }
    return request;
  }
  if (preferredType === "application/json" && request.uri.indexOf(".") === -1 && !isKnownRoute(request.uri)) {
    return jsonNotFound();
  }
  if (request.uri !== "/" && request.uri.slice(-1) !== "/" && request.uri.indexOf(".") === -1) {
    return {
      statusCode: 301,
      statusDescription: "Moved Permanently",
      headers: {
        location: { value: appendQueryString(request.uri + "/") }
      }
    };
  }
  if (request.uri !== "/" && request.uri.slice(-1) === "/") {
    request.uri = request.uri + "index.html";
  }
  return request;
}

EOF


  if aws cloudfront describe-function --name "${redirect_function_name}" >/dev/null 2>&1; then
    log "  Updating ${redirect_function_name}"
    function_etag="$(
      aws cloudfront describe-function \
        --name "${redirect_function_name}" \
        --query 'ETag' \
        --output text
    )"
    aws cloudfront update-function \
      --name "${redirect_function_name}" \
      --if-match "${function_etag}" \
        --function-config Comment="Canonical host and retired route redirects",Runtime=cloudfront-js-2.0 \
        --function-code "fileb://${function_file}" >/dev/null
  else
    log "  Creating ${redirect_function_name}"
    aws cloudfront create-function \
      --name "${redirect_function_name}" \
      --function-config Comment="Canonical host and retired route redirects",Runtime=cloudfront-js-2.0 \
      --function-code "fileb://${function_file}" >/dev/null
  fi

  function_etag="$(
    aws cloudfront describe-function \
      --name "${redirect_function_name}" \
      --query 'ETag' \
      --output text
  )"
  stage="$(
    aws cloudfront describe-function \
      --name "${redirect_function_name}" \
      --query 'FunctionSummary.FunctionConfig.Stage' \
      --output text
  )"
  if [[ "${stage}" != "LIVE" ]]; then
    log "  Publishing function to LIVE"
    aws cloudfront publish-function \
      --name "${redirect_function_name}" \
      --if-match "${function_etag}" >/dev/null
  else
    log "  Function is already LIVE"
  fi
  log_ok "Redirect function ready"
}

ensure_response_headers_policy() {
  local policy_file policy_id etag response_file
  log_step "Preparing CloudFront security headers policy"
  make_temp_file policy_file
  make_temp_file response_file

  jq -n \
    --arg name "${response_headers_policy_name}" \
    '{
      Name: $name,
      Comment: "Security headers for Automic Vault static site",
      SecurityHeadersConfig: {
        StrictTransportSecurity: {
          Override: true,
          AccessControlMaxAgeSec: 63072000,
          IncludeSubdomains: true,
          Preload: true
        },
        ContentTypeOptions: {
          Override: true
        },
        FrameOptions: {
          Override: true,
          FrameOption: "DENY"
        },
        ReferrerPolicy: {
          Override: true,
          ReferrerPolicy: "strict-origin-when-cross-origin"
        },
        XSSProtection: {
          Override: true,
          Protection: true,
          ModeBlock: true
        },
        ContentSecurityPolicy: {
          Override: true,
          ContentSecurityPolicy: "default-src '\''self'\''; script-src '\''self'\'' '\''unsafe-inline'\'' '\''wasm-unsafe-eval'\'' https://www.googletagmanager.com; style-src '\''self'\'' '\''unsafe-inline'\'' https://fonts.googleapis.com; font-src '\''self'\'' https://fonts.gstatic.com; img-src '\''self'\'' data: https://www.automicvault.com; connect-src '\''self'\'' https://www.google-analytics.com https://www.google.com; frame-ancestors '\''none'\''; base-uri '\''self'\''; form-action '\''none'\''"
        }
      },
      CustomHeadersConfig: {
        Quantity: 1,
        Items: [
          {
            Header: "Permissions-Policy",
            Value: "camera=(), microphone=(), geolocation=(), payment=()",
            Override: true
          }
        ]
      },
      ServerTimingHeadersConfig: {
        Enabled: false
      },
      RemoveHeadersConfig: {
        Quantity: 0
      }
    }' >"${policy_file}"

  policy_id="$(
    aws cloudfront list-response-headers-policies \
      --type custom \
      --query "ResponseHeadersPolicyList.Items[?ResponseHeadersPolicy.ResponseHeadersPolicyConfig.Name == '${response_headers_policy_name}'].ResponseHeadersPolicy.Id | [0]" \
      --output text
  )"

  if [[ "${policy_id}" == "None" ]]; then
    policy_id="$(
      aws cloudfront create-response-headers-policy \
        --response-headers-policy-config "file://${policy_file}" \
        --query 'ResponseHeadersPolicy.Id' \
        --output text
    )"
    log_ok "Created response headers policy ${policy_id}"
    printf '%s\n' "${policy_id}"
    return 0
  fi

  aws cloudfront get-response-headers-policy-config \
    --id "${policy_id}" >"${response_file}"
  etag="$(jq -r '.ETag' "${response_file}")"
  aws cloudfront update-response-headers-policy \
    --id "${policy_id}" \
    --if-match "${etag}" \
    --response-headers-policy-config "file://${policy_file}" >/dev/null
  log_ok "Response headers policy ready"
  printf '%s\n' "${policy_id}"
}

ensure_cache_policy() {
  local policy_file policy_id etag response_file
  log_step "Preparing CloudFront Brotli cache policy"
  make_temp_file policy_file
  make_temp_file response_file

  jq -n \
    --arg name "${cache_policy_name}" \
    '{
      Name: $name,
      Comment: "Static site cache policy with Gzip, Brotli, viewer protocol, and asset version query strings",
      DefaultTTL: 86400,
      MaxTTL: 31536000,
      MinTTL: 0,
      ParametersInCacheKeyAndForwardedToOrigin: {
        EnableAcceptEncodingGzip: true,
        EnableAcceptEncodingBrotli: true,
        HeadersConfig: {
          HeaderBehavior: "whitelist",
          Headers: {
            Quantity: 1,
            Items: ["CloudFront-Forwarded-Proto"]
          }
        },
        CookiesConfig: {
          CookieBehavior: "none"
        },
        QueryStringsConfig: {
          QueryStringBehavior: "all"
        }
      }
    }' >"${policy_file}"

  policy_id="$(
    aws cloudfront list-cache-policies \
      --type custom \
      --query "CachePolicyList.Items[?CachePolicy.CachePolicyConfig.Name == '${cache_policy_name}'].CachePolicy.Id | [0]" \
      --output text
  )"

  if [[ "${policy_id}" == "None" ]]; then
    policy_id="$(
      aws cloudfront create-cache-policy \
        --cache-policy-config "file://${policy_file}" \
        --query 'CachePolicy.Id' \
        --output text
    )"
    log_ok "Created cache policy ${policy_id}"
    printf '%s\n' "${policy_id}"
    return 0
  fi

  aws cloudfront get-cache-policy-config \
    --id "${policy_id}" >"${response_file}"
  etag="$(jq -r '.ETag' "${response_file}")"
  aws cloudfront update-cache-policy \
    --id "${policy_id}" \
    --if-match "${etag}" \
    --cache-policy-config "file://${policy_file}" >/dev/null
  log_ok "Cache policy ready"
  printf '%s\n' "${policy_id}"
}

distribution_id_for_alias() {
  local alias_csv
  alias_csv="$(
    aws cloudfront list-distributions \
      --query "DistributionList.Items[?Aliases.Items && contains(join(',', Aliases.Items), '${WWW_DOMAIN}')].Id | [0]" \
      --output text
  )"

  if [[ "${alias_csv}" == "None" ]]; then
    return 1
  fi

  printf '%s\n' "${alias_csv}"
}

build_distribution_config() {
  local oac_id="$1"
  local function_arn="$2"
  local response_headers_policy_id="$3"
  local cache_policy_id="$4"
  local release_redirect_oac_id="$5"
  local release_redirect_domain="$6"
  local release_redirect_cache_policy_id="$7"
  local output_file="$8"

  jq -n \
    --arg caller_reference "${WWW_DOMAIN}-$(date +%s)" \
    --arg comment "${distribution_comment}" \
    --arg origin_id "${WWW_BUCKET}-origin" \
    --arg domain_name "${origin_domain}" \
    --arg oac_id "${oac_id}" \
    --arg function_arn "${function_arn}" \
    --arg response_headers_policy_id "${response_headers_policy_id}" \
    --arg cache_policy_id "${cache_policy_id}" \
    --arg release_origin_id "${release_redirect_origin_id}" \
    --arg release_origin_domain "${release_redirect_domain}" \
    --arg release_oac_id "${release_redirect_oac_id}" \
    --arg release_cache_policy_id "${release_redirect_cache_policy_id}" \
    --arg cert_arn "${WWW_CERTIFICATE_ARN}" \
    --arg domain_a "${WWW_DOMAIN}" \
    --arg domain_b "${WWW_WWW_DOMAIN}" \
    --arg price_class "${WWW_CLOUDFRONT_PRICE_CLASS}" \
    '
      def release_behavior($pattern):
        {
          PathPattern: $pattern,
          TargetOriginId: $release_origin_id,
          ViewerProtocolPolicy: "redirect-to-https",
          AllowedMethods: {
            Quantity: 2,
            Items: ["HEAD", "GET"],
            CachedMethods: {Quantity: 2, Items: ["HEAD", "GET"]}
          },
          Compress: false,
          SmoothStreaming: false,
          CachePolicyId: $release_cache_policy_id,
          ResponseHeadersPolicyId: $response_headers_policy_id,
          TrustedSigners: {Enabled: false, Quantity: 0},
          TrustedKeyGroups: {Enabled: false, Quantity: 0},
          LambdaFunctionAssociations: {Quantity: 0},
          FunctionAssociations: {Quantity: 0},
          FieldLevelEncryptionId: ""
        };
      {
      CallerReference: $caller_reference,
      Comment: $comment,
      Enabled: true,
      DefaultRootObject: "index.html",
      Origins: {
        Quantity: 2,
        Items: [{
          Id: $origin_id,
          DomainName: $domain_name,
          OriginPath: "",
          OriginAccessControlId: $oac_id,
          CustomHeaders: {Quantity: 0},
          S3OriginConfig: {
            OriginAccessIdentity: "",
            OriginReadTimeout: 30
          }
        }, {
          Id: $release_origin_id,
          DomainName: $release_origin_domain,
          OriginPath: "",
          OriginAccessControlId: $release_oac_id,
          CustomHeaders: {Quantity: 0},
          CustomOriginConfig: {
            HTTPPort: 80,
            HTTPSPort: 443,
            OriginProtocolPolicy: "https-only",
            OriginSslProtocols: {Quantity: 1, Items: ["TLSv1.2"]},
            OriginReadTimeout: 10,
            OriginKeepaliveTimeout: 5
          }
        }]
      },
      Aliases: {
        Quantity: 2,
        Items: [$domain_a, $domain_b]
      },
      DefaultCacheBehavior: {
        TargetOriginId: $origin_id,
        ViewerProtocolPolicy: "allow-all",
        AllowedMethods: {
          Quantity: 2,
          Items: ["HEAD", "GET"],
          CachedMethods: {
            Quantity: 2,
            Items: ["HEAD", "GET"]
          }
        },
        Compress: true,
        SmoothStreaming: false,
        CachePolicyId: $cache_policy_id,
        ResponseHeadersPolicyId: $response_headers_policy_id,
        TrustedSigners: {
          Enabled: false,
          Quantity: 0
        },
        TrustedKeyGroups: {
          Enabled: false,
          Quantity: 0
        },
        LambdaFunctionAssociations: {
          Quantity: 0
        },
        FunctionAssociations: {
          Quantity: 1,
          Items: [{
            EventType: "viewer-request",
            FunctionARN: $function_arn
          }]
        },
        FieldLevelEncryptionId: ""
        },
        CacheBehaviors: {
          Quantity: 2,
          Items: [release_behavior("av.dmg"), release_behavior("Automic*Vault.dmg")]
        },
      CustomErrorResponses: {
        Quantity: 1,
        Items: [{
          ErrorCode: 403,
          ResponsePagePath: "/404.html",
          ResponseCode: "404",
          ErrorCachingMinTTL: 60
        }]
      },
      Restrictions: {
        GeoRestriction: {
          RestrictionType: "none",
          Quantity: 0
        }
      },
      ViewerCertificate: {
        ACMCertificateArn: $cert_arn,
        SSLSupportMethod: "sni-only",
        MinimumProtocolVersion: "TLSv1.2_2021",
        Certificate: $cert_arn,
        CertificateSource: "acm"
      },
      PriceClass: $price_class,
      HttpVersion: "http2",
      IsIPV6Enabled: true
    }' >"${output_file}"
}

upsert_distribution() {
  local oac_id="$1"
  local function_arn="$2"
  local response_headers_policy_id="$3"
  local cache_policy_id="$4"
  local release_redirect_oac_id="$5"
  local release_redirect_domain="$6"
  local release_redirect_cache_policy_id="$7"
  local distribution_id etag config_file response_file
  log_step "Preparing CloudFront distribution"
  make_temp_file config_file
  make_temp_file response_file

  if distribution_id="$(distribution_id_for_alias)"; then
    log "  Updating distribution ${distribution_id}"
    aws cloudfront get-distribution-config \
      --id "${distribution_id}" >"${response_file}"
    etag="$(jq -r '.ETag' "${response_file}")"
    jq \
      --arg comment "${distribution_comment}" \
      --arg origin_id "${WWW_BUCKET}-origin" \
      --arg domain_name "${origin_domain}" \
      --arg oac_id "${oac_id}" \
      --arg function_arn "${function_arn}" \
      --arg response_headers_policy_id "${response_headers_policy_id}" \
      --arg cache_policy_id "${cache_policy_id}" \
      --arg release_origin_id "${release_redirect_origin_id}" \
      --arg release_origin_domain "${release_redirect_domain}" \
      --arg release_oac_id "${release_redirect_oac_id}" \
      --arg release_cache_policy_id "${release_redirect_cache_policy_id}" \
      --arg cert_arn "${WWW_CERTIFICATE_ARN}" \
      --arg domain_a "${WWW_DOMAIN}" \
      --arg domain_b "${WWW_WWW_DOMAIN}" \
      --arg price_class "${WWW_CLOUDFRONT_PRICE_CLASS}" \
      '
        def release_behavior($pattern):
          {
            PathPattern: $pattern,
            TargetOriginId: $release_origin_id,
            ViewerProtocolPolicy: "redirect-to-https",
            AllowedMethods: {
              Quantity: 2,
              Items: ["HEAD", "GET"],
              CachedMethods: {Quantity: 2, Items: ["HEAD", "GET"]}
            },
            Compress: false,
            SmoothStreaming: false,
            CachePolicyId: $release_cache_policy_id,
            ResponseHeadersPolicyId: $response_headers_policy_id,
            TrustedSigners: {Enabled: false, Quantity: 0},
            TrustedKeyGroups: {Enabled: false, Quantity: 0},
            LambdaFunctionAssociations: {Quantity: 0},
            FunctionAssociations: {Quantity: 0},
            FieldLevelEncryptionId: ""
          };
        .DistributionConfig.Comment = $comment
      | .DistributionConfig.DefaultRootObject = "index.html"
      | .DistributionConfig.Enabled = true
      | .DistributionConfig.PriceClass = $price_class
      | .DistributionConfig.Origins.Quantity = 2
      | .DistributionConfig.Origins.Items = [{
          Id: $origin_id,
          DomainName: $domain_name,
          OriginPath: "",
          OriginAccessControlId: $oac_id,
          CustomHeaders: {Quantity: 0},
          S3OriginConfig: {
            OriginAccessIdentity: "",
            OriginReadTimeout: 30
          }
        }, {
          Id: $release_origin_id,
          DomainName: $release_origin_domain,
          OriginPath: "",
          OriginAccessControlId: $release_oac_id,
          CustomHeaders: {Quantity: 0},
          CustomOriginConfig: {
            HTTPPort: 80,
            HTTPSPort: 443,
            OriginProtocolPolicy: "https-only",
            OriginSslProtocols: {Quantity: 1, Items: ["TLSv1.2"]},
            OriginReadTimeout: 10,
            OriginKeepaliveTimeout: 5
          }
        }]
      | .DistributionConfig.Aliases = {
          Quantity: 2,
          Items: [$domain_a, $domain_b]
        }
      | .DistributionConfig.DefaultCacheBehavior.TargetOriginId = $origin_id
      | .DistributionConfig.DefaultCacheBehavior.ViewerProtocolPolicy = "allow-all"
      | .DistributionConfig.DefaultCacheBehavior.AllowedMethods = {
          Quantity: 2,
          Items: ["HEAD", "GET"],
          CachedMethods: {
            Quantity: 2,
            Items: ["HEAD", "GET"]
          }
        }
      | .DistributionConfig.DefaultCacheBehavior.Compress = true
      | .DistributionConfig.DefaultCacheBehavior.SmoothStreaming = false
      | .DistributionConfig.DefaultCacheBehavior.CachePolicyId = $cache_policy_id
      | .DistributionConfig.DefaultCacheBehavior.ResponseHeadersPolicyId = $response_headers_policy_id
      | .DistributionConfig.DefaultCacheBehavior.TrustedSigners = {
          Enabled: false,
          Quantity: 0
        }
      | .DistributionConfig.DefaultCacheBehavior.TrustedKeyGroups = {
          Enabled: false,
          Quantity: 0
        }
      | .DistributionConfig.DefaultCacheBehavior.LambdaFunctionAssociations = {
          Quantity: 0
        }
      | .DistributionConfig.DefaultCacheBehavior.FunctionAssociations = {
          Quantity: 1,
          Items: [{
            EventType: "viewer-request",
            FunctionARN: $function_arn
          }]
        }
      | .DistributionConfig.DefaultCacheBehavior.FieldLevelEncryptionId = ""
      | del(
          .DistributionConfig.DefaultCacheBehavior.ForwardedValues,
          .DistributionConfig.DefaultCacheBehavior.MinTTL,
          .DistributionConfig.DefaultCacheBehavior.DefaultTTL,
          .DistributionConfig.DefaultCacheBehavior.MaxTTL
        )
        | .DistributionConfig.CacheBehaviors = {
            Quantity: 2,
            Items: [release_behavior("av.dmg"), release_behavior("Automic*Vault.dmg")]
          }
      | .DistributionConfig.CustomErrorResponses = {
          Quantity: 1,
          Items: [{
            ErrorCode: 403,
            ResponsePagePath: "/404.html",
            ResponseCode: "404",
            ErrorCachingMinTTL: 60
          }]
        }
      | .DistributionConfig.ViewerCertificate = {
          ACMCertificateArn: $cert_arn,
          SSLSupportMethod: "sni-only",
          MinimumProtocolVersion: "TLSv1.2_2021",
          Certificate: $cert_arn,
          CertificateSource: "acm"
        }
      ' "${response_file}" | jq '.DistributionConfig' >"${config_file}"

    if ! aws cloudfront update-distribution \
      --id "${distribution_id}" \
      --if-match "${etag}" \
      --distribution-config "file://${config_file}" \
      --query 'Distribution.Id' \
      --output text; then
      return 1
    fi
    return 0
  fi

  log "  Creating distribution for ${WWW_DOMAIN}, ${WWW_WWW_DOMAIN}"
  build_distribution_config "${oac_id}" "${function_arn}" "${response_headers_policy_id}" "${cache_policy_id}" "${release_redirect_oac_id}" "${release_redirect_domain}" "${release_redirect_cache_policy_id}" "${config_file}"
  aws cloudfront create-distribution \
    --distribution-config "file://${config_file}" \
    --query 'Distribution.Id' \
    --output text
}

put_bucket_policy() {
  local distribution_id="$1"
  local policy_file
  log_step "Restricting bucket reads to CloudFront"
  make_temp_file policy_file

  jq -n \
    --arg bucket "${WWW_BUCKET}" \
    --arg account_id "${AWS_ACCOUNT_ID}" \
    --arg distribution_id "${distribution_id}" \
    '{
      Version: "2012-10-17",
      Statement: [{
        Sid: "AllowCloudFrontServicePrincipalReadOnly",
        Effect: "Allow",
        Principal: {
          Service: "cloudfront.amazonaws.com"
        },
        Action: "s3:GetObject",
        Resource: ("arn:aws:s3:::" + $bucket + "/*"),
        Condition: {
          StringEquals: {
            "AWS:SourceArn": ("arn:aws:cloudfront::" + $account_id + ":distribution/" + $distribution_id)
          }
        }
      }]
    }' >"${policy_file}"

  aws s3api put-bucket-policy \
    --bucket "${WWW_BUCKET}" \
    --policy "file://${policy_file}"
  log_ok "Bucket policy applied"
}

sync_site() {
  local upload_site_dir="${prepared_site_dir:-${site_dir}}"

  log_step "Syncing static assets"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --delete \
    --exclude "AGENTS.md" \
    --exclude ".DS_Store" \
    --exclude "*/.DS_Store" \
    --exclude "Automic Vault.dmg" \
    --exclude "scanner.gz" \
    --exclude "scanner.sh" \
    --exclude "db.json" \
    --exclude "preview.jpg" \
    --exclude "*.html" \
    --exclude "*.xml" \
    --exclude "*.txt" \
    --exclude "*.md" \
    --exclude "*.json" \
    --exclude "*.css" \
    --cache-control "${WWW_ASSET_CACHE_CONTROL}"

  log_step "Uploading social preview"
  aws s3 cp "${upload_site_dir}/preview.jpg" "s3://${WWW_BUCKET}/preview.jpg" \
    --content-type "image/jpeg" \
    --cache-control "${WWW_PREVIEW_CACHE_CONTROL}"

  log_step "Syncing stylesheets"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --exclude "*" \
    --include "*.css" \
    --cache-control "${WWW_CSS_CACHE_CONTROL}"

  log_step "Syncing crawlable HTML and XML content"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --exclude ".DS_Store" \
    --exclude "*/.DS_Store" \
    --exclude "*" \
    --include "*.html" \
    --include "*.xml" \
    --exclude "AGENTS.md" \
    --cache-control "${WWW_HTML_CACHE_CONTROL}"

  log_step "Syncing crawlable plain text content"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --exclude ".DS_Store" \
    --exclude "*/.DS_Store" \
    --exclude "*" \
    --include "*.txt" \
    --exclude "AGENTS.md" \
    --content-type "text/plain; charset=utf-8" \
    --cache-control "${WWW_HTML_CACHE_CONTROL}"

  log_step "Syncing crawlable markdown content"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --exclude ".DS_Store" \
    --exclude "*/.DS_Store" \
    --exclude "*" \
    --include "*.md" \
    --exclude "AGENTS.md" \
    --content-type "text/markdown; charset=utf-8" \
    --cache-control "${WWW_HTML_CACHE_CONTROL}"

  log_step "Syncing crawlable JSON content"
  aws s3 sync "${upload_site_dir}/" "s3://${WWW_BUCKET}/" \
    --exclude ".DS_Store" \
    --exclude "*/.DS_Store" \
    --exclude "*" \
    --include "*.json" \
    --exclude "AGENTS.md" \
    --content-type "application/json; charset=utf-8" \
    --cache-control "${WWW_HTML_CACHE_CONTROL}"

  log_step "Removing repo-local guidance from S3"
  aws s3 rm "s3://${WWW_BUCKET}/AGENTS.md"

  log_ok "S3 content synced"
}

invalidate_dynamic_paths() {
  local distribution_id="$1"
  local invalidation_id

  log_step "Invalidating dynamic CloudFront paths"
  invalidation_id="$(
    aws cloudfront create-invalidation \
      --distribution-id "${distribution_id}" \
      --paths \
        '/av.dmg' '/Automic%20Vault.dmg' \
      --query 'Invalidation.Id' \
      --output text
  )"
  aws cloudfront wait invalidation-completed \
    --distribution-id "${distribution_id}" \
    --id "${invalidation_id}"
  log_ok "Dynamic path invalidation completed"
}

ensure_certificate_issued() {
  local status
  log_step "Checking ACM certificate"
  status="$(
    aws acm describe-certificate \
      --region us-east-1 \
      --certificate-arn "${WWW_CERTIFICATE_ARN}" \
      --query 'Certificate.Status' \
      --output text
  )"

  if [[ "${status}" != "ISSUED" ]]; then
    die "Certificate is not issued: ${status}"
  fi
  log_ok "Certificate is issued"
}

log_header
assert_www_i18n_current
prepare_site_for_upload
if [[ "${prepare_only}" == true ]]; then
  if [[ "${use_color}" == true ]]; then
    cat <<EOF

${green}${glyph_ok}${reset} ${bold}Website preparation complete${reset}
  AWS changes                 skipped
EOF
  else
    cat <<EOF

Website preparation complete.
AWS changes: skipped
EOF
  fi
  exit 0
fi
if [[ "${static_only}" == true ]]; then
  log_step "Checking S3 bucket"
  aws s3api head-bucket --bucket "${WWW_BUCKET}" >/dev/null
  log_ok "S3 bucket exists"
  sync_site

  if [[ "${use_color}" == true ]]; then
    cat <<EOF

${green}${glyph_ok}${reset} ${bold}Static deployment complete${reset}
  Bucket                      ${WWW_BUCKET}
  CloudFront configuration    skipped
EOF
  else
    cat <<EOF

Static deployment complete.
Bucket: ${WWW_BUCKET}
CloudFront configuration: skipped
EOF
  fi
  exit 0
fi
ensure_bucket
configure_static_origin
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
oac_id="$(ensure_oac)"
ensure_release_redirect_oac
ensure_release_redirect
ensure_redirect_function
response_headers_policy_id="$(ensure_response_headers_policy)"
cache_policy_id="$(ensure_cache_policy)"
log_step "Reading CloudFront function ARN"
function_arn="$(
  aws cloudfront describe-function \
    --name "${redirect_function_name}" \
    --stage LIVE \
    --query 'FunctionSummary.FunctionMetadata.FunctionARN' \
    --output text
)"
log_ok "Function ARN resolved"
ensure_certificate_issued
distribution_id="$(upsert_distribution "${oac_id}" "${function_arn}" "${response_headers_policy_id}" "${cache_policy_id}" "${release_redirect_oac_id}" "${release_redirect_domain}" "${release_redirect_cache_policy_id}")"
allow_cloudfront_release_redirect "${distribution_id}"
put_bucket_policy "${distribution_id}"
log_step "Waiting for CloudFront deployment"
aws cloudfront wait distribution-deployed --id "${distribution_id}"
log_ok "Distribution deployed"
sync_site
if [[ "${WWW_EMERGENCY_INVALIDATE}" == "true" ]]; then
  log_step "Submitting emergency CloudFront invalidation"
  aws cloudfront create-invalidation \
    --distribution-id "${distribution_id}" \
    --paths '/*' >/dev/null
  log_ok "Emergency invalidation submitted"
else
  invalidate_dynamic_paths "${distribution_id}"
fi

distribution_domain="$(
  aws cloudfront get-distribution \
    --id "${distribution_id}" \
    --query 'Distribution.DomainName' \
    --output text
)"

if [[ "${use_color}" == true ]]; then
  cat <<EOF

${green}${glyph_ok}${reset} ${bold}Deployment complete${reset}
  CloudFront distribution ID  ${distribution_id}
  CloudFront domain           ${distribution_domain}
  Bucket                      ${WWW_BUCKET}
  Aliases                     ${WWW_DOMAIN}, ${WWW_WWW_DOMAIN}
EOF
else
  cat <<EOF

Deployment complete.
CloudFront distribution ID: ${distribution_id}
CloudFront domain: ${distribution_domain}
Bucket: ${WWW_BUCKET}
Aliases: ${WWW_DOMAIN}, ${WWW_WWW_DOMAIN}
EOF
fi
