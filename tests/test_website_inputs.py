import datetime
import html.parser
import pathlib
import re
import subprocess
import sys
import unittest
import urllib.parse
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
GA_SCRIPT = "https://www.googletagmanager.com/gtag/js?id=G-Y78QKG1T9Y"
GA_CONFIG = "gtag('config', 'G-Y78QKG1T9Y')"


class LocalReferenceParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, _tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


class StaticHtmlAnalyticsTests(unittest.TestCase):
    def test_release_download_uses_private_cloudfront_lambda_origin(self):
        subprocess.run(
            ["node", "--test", str(ROOT / "lambda" / "release-redirect" / "index.test.mjs")],
            cwd=ROOT,
            check=True,
        )
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")
        self.assertIn('OriginAccessControlOriginType: "lambda"', deploy_script)
        self.assertIn('--auth-type AWS_IAM', deploy_script)
        self.assertNotIn('--auth-type NONE', deploy_script)
        self.assertIn('release_behavior("av.dmg")', deploy_script)
        self.assertIn('release_behavior("Automic*Vault.dmg")', deploy_script)
        self.assertEqual(deploy_script.count("CustomHeaders: {Quantity: 0}"), 4)
        update_config = deploy_script.split("aws lambda update-function-configuration", 1)[1].split("aws lambda wait", 1)[0]
        update_code = deploy_script.split("aws lambda update-function-code", 1)[1].split("else", 1)[0]
        self.assertNotIn("--architectures", update_config)
        self.assertIn("--architectures arm64", update_code)

    def test_pkg_so_redirect_is_permanent(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")

        self.assertNotIn("WWW_PKG_SO_REDIRECT", deploy_script)
        self.assertNotIn("redirectPackages", deploy_script)
        for old_path, new_path in {
            "/pkg": "/",
            "/pkg/": "/",
            "/de/pkg": "/de/",
            "/de/pkg/": "/de/",
            "/fr/pkg": "/fr/",
            "/fr/pkg/": "/fr/",
            "/ja/pkg": "/ja/",
            "/ja/pkg/": "/ja/",
            "/zh-hans/pkg": "/zh-hans/",
            "/zh-hans/pkg/": "/zh-hans/",
        }.items():
            self.assertIn(f'"{old_path}": "{new_path}"', deploy_script)
        self.assertIn('return appendQueryString("https://pkg.so" + landingPages[uri]);', deploy_script)
        self.assertIn('return appendQueryString("https://pkg.so" + uri);', deploy_script)
        self.assertIn('request.uri === "/db.json" || isPackageOriginPath(request.uri)', deploy_script)
        self.assertIn("if (isPackageOriginPath(request.uri))", deploy_script)
        self.assertIn('statusCode: 301', deploy_script)
        self.assertNotIn("WWW_PKG_ORIGIN", deploy_script)
        self.assertNotIn("atlas-pkg-origin", deploy_script)
        self.assertNotIn("pkg_behaviors", deploy_script)

    def test_deploy_reads_region_from_bucket(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")

        region_setup = deploy_script.split('export WWW_BUCKET="${WWW_BUCKET:-${WWW_DOMAIN}}"', 1)[1].split(
            "export WWW_CLOUDFRONT_PRICE_CLASS", 1
        )[0]
        self.assertIn("aws s3api get-bucket-location", region_setup)
        self.assertIn("--region us-east-1", region_setup)
        self.assertIn('AWS_REGION="us-east-1"', region_setup)
        self.assertNotIn("require_env AWS_REGION", deploy_script)
        self.assertNotIn(".envrc", deploy_script)

    def test_deploy_finds_certificate_for_both_aliases(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")

        self.assertIn("aws acm list-certificates", deploy_script)
        self.assertIn("--certificate-statuses ISSUED", deploy_script)
        self.assertIn("contains(SubjectAlternativeNameSummaries", deploy_script)
        self.assertNotIn("require_env WWW_CERTIFICATE_ARN", deploy_script)

    def test_distribution_update_does_not_assume_origin_order(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")
        update = deploy_script.split("if distribution_id=", 1)[1].split("if ! aws cloudfront update-distribution", 1)[0]

        self.assertNotIn(".DistributionConfig.Origins.Items[0]", update)
        self.assertIn("Id: $origin_id", update)
        self.assertIn("S3OriginConfig: {", update)

    def test_static_pages_link_directly_to_pkg_so(self):
        stale = []
        for page in sorted((ROOT / "www").rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            if re.search(r'href="(?:\.\./|/)(?:de/|fr/|ja/|zh-hans/)?pkg/', text):
                stale.append(str(page.relative_to(ROOT)))
        self.assertEqual(stale, [])

    def test_all_static_html_pages_embed_google_analytics(self):
        missing = []
        for page in sorted((ROOT / "www").rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            if GA_SCRIPT not in text or GA_CONFIG not in text:
                missing.append(str(page.relative_to(ROOT)))

        self.assertEqual(missing, [])

    def test_csp_allows_google_analytics_script(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")
        self.assertIn("script-src", deploy_script)
        self.assertIn("https://www.googletagmanager.com", deploy_script)
        self.assertIn("connect-src", deploy_script)
        self.assertIn("https://www.google-analytics.com", deploy_script)
        self.assertIn("https://www.google.com", deploy_script)

    def test_localized_static_pages_are_current(self):
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate-www-i18n.py"), "--check"],
            cwd=ROOT,
            check=True,
        )

    def test_content_pages_share_current_chrome_and_styles(self):
        pages = []
        for route in ("about", "privacy", "terms"):
            pages.append(ROOT / "www" / route / "index.html")
            pages.extend(
                ROOT / "www" / locale / route / "index.html"
                for locale in ("de", "fr", "ja", "zh-hans")
            )

        for page in pages:
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.relative_to(ROOT)):
                self.assertIn('class="seo-masthead"', text)
                self.assertIn('class="seo-footer"', text)
                self.assertIn("styles.css?v=128", text)
                self.assertIn("landing-pages.css?v=5", text)

    def test_mobile_navigation_has_shared_behavior_and_cache_version(self):
        script = (ROOT / "www" / "app.js").read_text(encoding="utf-8")
        self.assertIn('document.querySelector(".nav-toggle")', script)
        self.assertIn('nav.classList.toggle("is-open"', script)
        self.assertIn('toggle.setAttribute("aria-expanded"', script)

        pages = []
        for page in sorted((ROOT / "www").rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            if 'class="nav-toggle"' not in text:
                continue

            pages.append(page)
            with self.subTest(page=page.relative_to(ROOT)):
                self.assertIn("app.js?v=26", text)

        self.assertTrue(pages)

    def test_docs_match_the_v2_cli_surface(self):
        html = (ROOT / "www" / "docs" / "index.html").read_text(encoding="utf-8")
        markdown = (ROOT / "www" / "docs" / "index.md").read_text(encoding="utf-8")
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")

        for text in (html, markdown):
            with self.subTest(format="html" if text is html else "markdown"):
                for command in (
                    "av scan",
                    "av doctor",
                    "av detectors --json",
                    "av hardeners --json",
                    "av inject",
                    "av save",
                    "av harden",
                    "av open",
                ):
                    self.assertIn(command, text)
                self.assertIn("does not read standard input", text)
                self.assertIn("not part of", text)

        self.assertIn('"/docs": true', deploy_script)
        self.assertIn('"/docs/": true', deploy_script)
        self.assertNotIn(
            '"/docs": "https://github.com/automic-vault/automic-vault#readme"',
            deploy_script,
        )

    def test_cloudfront_origin_uses_the_bucket_region(self):
        deploy_script = (ROOT / "scripts" / "deploy-www.sh").read_text(encoding="utf-8")

        self.assertIn("aws s3api get-bucket-location", deploy_script)
        self.assertIn('if [[ "${bucket_region}" == "us-east-1" ]]', deploy_script)
        self.assertIn(
            'origin_domain="${WWW_BUCKET}.s3.amazonaws.com"',
            deploy_script,
        )
        self.assertIn(
            'origin_domain="${WWW_BUCKET}.s3.${bucket_region}.amazonaws.com"',
            deploy_script,
        )
        self.assertNotIn(
            'origin_domain="${WWW_BUCKET}.s3.${AWS_REGION}.amazonaws.com"',
            deploy_script,
        )
        self.assertIn("ensure_bucket\nconfigure_static_origin", deploy_script)

    def test_llms_files_are_structured_and_match_the_current_docs(self):
        docs = (ROOT / "www" / "docs" / "index.html").read_text(encoding="utf-8")
        version_match = re.search(r'"softwareVersion": "([^"]+)"', docs)
        self.assertIsNotNone(version_match)
        version = version_match.group(1)

        locales = ("", "de", "fr", "ja", "zh-hans")
        for locale in locales:
            llms_path = ROOT / "www" / locale / "llms.txt"
            text = llms_path.read_text(encoding="utf-8")
            lines = text.splitlines()
            page_entries = [line for line in lines if line.startswith("- [")]
            urls = re.findall(r"\[[^]]+\]\((https://[^)]+)\)", text)

            with self.subTest(locale=locale or "en"):
                self.assertEqual(lines[0], "# Automic Vault")
                self.assertTrue(lines[2].startswith("> "))
                self.assertLessEqual(len(lines[2][2:]), 200)
                self.assertGreaterEqual(sum(line.startswith("## ") for line in lines), 3)
                self.assertGreaterEqual(len(page_entries), 10)
                self.assertEqual(len(page_entries), len(urls))
                self.assertTrue(all("): " in line for line in page_entries))
                self.assertIn(f"Automic Vault {version}", text)
                self.assertIn("https://github.com/automic-vault/automic-vault", text)
                if locale:
                    self.assertIn(f"https://www.automicvault.com/{locale}/", text)
                    self.assertIn(f"https://pkg.so/{locale}/", text)
                else:
                    self.assertIn("https://www.automicvault.com/download/", text)
                    self.assertIn("https://www.automicvault.com/.well-known/security.txt", text)
                    self.assertIn("https://pkg.so/", text)

    def test_secondary_formats_and_localized_llms_are_discoverable(self):
        home = (ROOT / "www" / "index.html").read_text(encoding="utf-8")
        expected_alternates = {
            "text/markdown": "/index.md",
            "text/plain": "/index.txt",
            "application/json": "/index.json",
        }
        for media_type, href in expected_alternates.items():
            self.assertIn(f'type="{media_type}"', home)
            self.assertIn(f'href="{href}"', home)

        current_headline = "A new kind of secrets manager for a new era of development."
        for filename in ("index.md", "index.txt", "index.json"):
            text = (ROOT / "www" / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn(current_headline, text)
                self.assertNotIn("Stop AI agents running wild", text)

        for locale in ("de", "fr", "ja", "zh-hans"):
            for page in sorted((ROOT / "www" / locale).rglob("*.html")):
                with self.subTest(page=page.relative_to(ROOT)):
                    self.assertIn(
                        f'<link rel="alternate" type="text/plain" title="llms.txt" href="/{locale}/llms.txt">',
                        page.read_text(encoding="utf-8"),
                    )

    def test_crawler_and_security_metadata_are_current(self):
        robots = (ROOT / "www" / "robots.txt").read_text(encoding="utf-8")
        self.assertNotIn("automicvault.com/pkg/sitemap.xml", robots)
        for user_agent in (
            "GPTBot",
            "OAI-SearchBot",
            "ChatGPT-User",
            "PerplexityBot",
            "Perplexity-User",
            "ClaudeBot",
            "Claude-SearchBot",
            "Claude-User",
            "Google-Extended",
            "Bingbot",
        ):
            with self.subTest(user_agent=user_agent):
                self.assertIn(f"User-agent: {user_agent}\nAllow: /", robots)

        security = (ROOT / "www" / ".well-known" / "security.txt").read_text(encoding="utf-8")
        fields = dict(line.split(": ", 1) for line in security.splitlines())
        expires = datetime.datetime.fromisoformat(fields["Expires"].removesuffix("Z")).date()
        self.assertGreater(expires, datetime.date.today() + datetime.timedelta(days=180))
        self.assertEqual(fields["Canonical"], "https://www.automicvault.com/.well-known/security.txt")
        self.assertTrue(fields["Contact"].startswith("https://"))
        self.assertNotIn("Policy", fields)

        sitemap = ET.parse(ROOT / "www" / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        lastmods = {
            node.findtext("s:loc", namespaces=namespace): node.findtext("s:lastmod", namespaces=namespace)
            for node in sitemap.findall("s:url", namespace)
        }
        self.assertEqual(lastmods["https://www.automicvault.com/docs/"], "2026-07-27")
        for url in (
            "https://www.automicvault.com/llms.txt",
            "https://www.automicvault.com/llms-full.txt",
            "https://www.automicvault.com/.well-known/security.txt",
        ):
            self.assertEqual(lastmods[url], "2026-07-28")

    def test_public_assets_and_frontend_files_are_referenced(self):
        site = ROOT / "www"
        public_files = sorted((site / "assets").rglob("*"))
        public_files = [
            path for path in public_files
            if path.is_file() and path.name != ".DS_Store"
        ]
        public_files.extend(sorted(
            path for path in site.iterdir()
            if path.is_file() and path.suffix in {".css", ".ico", ".jpg", ".js", ".png", ".svg", ".webp"}
        ))

        source_files = []
        for directory in (site, ROOT / "scripts", ROOT / "crates", ROOT / "data"):
            for path in directory.rglob("*"):
                if not path.is_file() or path.is_relative_to(site / "assets"):
                    continue
                try:
                    source_files.append((path, path.read_text(encoding="utf-8")))
                except UnicodeDecodeError:
                    continue

        unreferenced = []
        for public_file in public_files:
            reference = public_file.relative_to(site).as_posix()
            if not any(reference in text for path, text in source_files if path != public_file):
                unreferenced.append(reference)

        self.assertEqual(unreferenced, [])

    def test_local_html_references_resolve(self):
        site = ROOT / "www"
        missing = []
        release_artifacts = {"/Automic Vault.dmg", "/install.sh", "/scanner.gz", "/scanner.sh"}

        for page in sorted(site.rglob("*.html")):
            parser = LocalReferenceParser()
            parser.feed(page.read_text(encoding="utf-8"))
            relative = page.relative_to(site)
            route = "/" if relative == pathlib.Path("index.html") else f"/{relative.parent.as_posix()}/"

            for reference in parser.references:
                parsed = urllib.parse.urlsplit(reference)
                if parsed.scheme not in {"", "http", "https"}:
                    continue
                if parsed.netloc and parsed.netloc != "www.automicvault.com":
                    continue
                path = urllib.parse.unquote(urllib.parse.urljoin(route, parsed.path or route))
                if path in release_artifacts:
                    continue
                target = site / path.lstrip("/")
                if path.endswith("/"):
                    target /= "index.html"
                elif target.is_dir():
                    target /= "index.html"
                if not target.exists():
                    missing.append(f"{relative}: {reference}")

        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
