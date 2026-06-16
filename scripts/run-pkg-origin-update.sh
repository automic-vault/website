#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
AV_DB_ROOT="${AV_DB_ROOT:-${repo_root}/../av.db}"

cd "${repo_root}"

log() {
  printf '[%s] %-5s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$1" "$2" >&2
}

format_duration() {
  local seconds="$1"
  local hours=$((seconds / 3600))
  local minutes=$(((seconds % 3600) / 60))
  local remainder=$((seconds % 60))

  if [[ "${hours}" -gt 0 ]]; then
    printf '%dh %dm %ds' "${hours}" "${minutes}" "${remainder}"
  elif [[ "${minutes}" -gt 0 ]]; then
    printf '%dm %ds' "${minutes}" "${remainder}"
  else
    printf '%ds' "${remainder}"
  fi
}

run_with_timeout() {
  local timeout_seconds="$1"
  shift

  python3 - "$timeout_seconds" "$@" <<'PY'
import os
import signal
import subprocess
import sys

timeout = int(sys.argv[1])
command = sys.argv[2:]
process = subprocess.Popen(command, start_new_session=True)
try:
    raise SystemExit(process.wait(timeout=timeout))
except KeyboardInterrupt:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        raise SystemExit(process.wait())
    try:
        process.wait(timeout=30)
        raise SystemExit(130)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        raise SystemExit(130)
except subprocess.TimeoutExpired:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        raise SystemExit(process.wait())
    try:
        process.wait(timeout=30)
        raise SystemExit(124)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        raise SystemExit(124)
PY
}

run_step() {
  local name="$1"
  shift
  local started_at elapsed exit_code

  log INFO "Starting ${name}"
  started_at="$(date +%s)"
  set +e
  "$@"
  exit_code=$?
  set -e
  elapsed=$(($(date +%s) - started_at))
  if [[ "${exit_code}" -ne 0 ]]; then
    log WARN "Failed ${name} after $(format_duration "${elapsed}") with exit code ${exit_code}"
    return "${exit_code}"
  fi
  log OK "Finished ${name} in $(format_duration "${elapsed}")"
}

run_enrichment_refresh() {
  local timeout_seconds="${AVWWW_PKG_ORIGIN_ENRICHMENT_REFRESH_TIMEOUT_SECONDS:-120}"

  if ! run_step "package-origin enrichment refresh" \
    run_with_timeout "${timeout_seconds}" \
      python3 "${AV_DB_ROOT}/scripts/generate-pkg-page-enrichment.py" --refresh; then
    log WARN "Homebrew API refresh did not finish within ${timeout_seconds}s; using cached package-origin enrichment inputs."
    run_step "package-origin enrichment cache fallback" \
      python3 "${AV_DB_ROOT}/scripts/generate-pkg-page-enrichment.py" --registry-cache-only
  fi
}

require_publish_env() {
  if [[ -z "${AV_WEB_ORIGIN_SECRET:-}" ]]; then
    log ERROR "Set AV_WEB_ORIGIN_SECRET before running the package-origin publish."
    return 1
  fi

  if [[ "${AV_WEB_ORIGIN_SECRET}" == encrypted:* ]]; then
    log ERROR "AV_WEB_ORIGIN_SECRET is still encrypted; resolve it before deploying the package origin."
    return 1
  fi

  if [[ -n "${WWW_PKG_ORIGIN_HEADER_VALUE:-}" && "${WWW_PKG_ORIGIN_HEADER_VALUE}" != "${AV_WEB_ORIGIN_SECRET}" ]]; then
    log WARN "WWW_PKG_ORIGIN_HEADER_VALUE is set but does not match AV_WEB_ORIGIN_SECRET."
  fi

  if [[ -n "${WWW_PKG_ORIGIN_HEADER_NAME:-}" && "${WWW_PKG_ORIGIN_HEADER_NAME}" != "${AV_WEB_ORIGIN_HEADER:-X-Automic-Vault-Origin}" ]]; then
    log WARN "WWW_PKG_ORIGIN_HEADER_NAME is set but does not match AV_WEB_ORIGIN_HEADER."
  fi

  if [[ -z "${AV_WEB_CERTBOT_EMAIL:-}" ]]; then
    log WARN "AV_WEB_CERTBOT_EMAIL is unset; Atlas deploy requires an existing TLS cert for ${AV_WEB_ORIGIN_DOMAIN:-av-origin.automicvault.com}."
  fi
}

require_publish_env
run_enrichment_refresh
run_step "package version freshness generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-version-freshness.py"
run_step "package manager index generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-manager-indexes.py"
run_step "package cross-ecosystem generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-cross-ecosystem.py"
run_step "package graph prepass generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-graph.py"
run_step "package graph curation generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-graph-curation.py"
run_step "package graph generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-graph.py"
run_step "package-origin SQLite generation" \
  python3 "${AV_DB_ROOT}/scripts/generate-pkg-sqlite.py"
run_step "Atlas package-origin deploy" \
  "${script_dir}/deploy-pkg-origin.sh" --skip-refresh --skip-sqlite
