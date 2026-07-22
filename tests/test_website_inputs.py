import html.parser
import importlib.util
import pathlib
import subprocess
import sys
import unittest
import urllib.parse
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
GA_SCRIPT = "https://www.googletagmanager.com/gtag/js?id=G-Y78QKG1T9Y"
GA_CONFIG = "gtag('config', 'G-Y78QKG1T9Y')"


def load_package_renderer():
    path = ROOT / "scripts" / "generate-pkg-pages.py"
    spec = importlib.util.spec_from_file_location("av_www_package_renderer_tests", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LocalReferenceParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []

    def handle_starttag(self, _tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.references.append(value)


class StaticHtmlAnalyticsTests(unittest.TestCase):
    def test_curated_taxonomy_overrides_fallback_package_category(self):
        renderer = load_package_renderer()
        page = renderer.PackagePage(provider="brew", name="aider", category="developer-tools")
        taxonomy = {
            "category": "ai",
            "categoryPath": ["ai", "coding-agents"],
            "categoryConfidence": "high",
            "tags": ["ai", "coding-agent"],
        }

        with (
            mock.patch.object(renderer, "load_pkg_taxonomy_index", return_value={}),
            mock.patch.object(renderer, "taxonomy_for_package", return_value=taxonomy),
        ):
            renderer.apply_package_taxonomy({"brew:aider": page})

        self.assertEqual(page.category, "ai")
        self.assertEqual(page.extra["pkgTaxonomy"]["categoryPath"], ["ai", "coding-agents"])

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
                self.assertIn("styles.css?v=108", text)
                self.assertIn("landing-pages.css?v=3", text)

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

    def test_public_assets_and_frontend_files_are_referenced(self):
        site = ROOT / "www"
        public_files = sorted((site / "assets").rglob("*"))
        public_files = [path for path in public_files if path.is_file()]
        public_files.extend(sorted(site.glob("*.css")))
        public_files.extend(sorted(site.glob("*.js")))

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
                if path in release_artifacts or path == "/pkg/" or any(
                    path.startswith(f"/{locale}/pkg/") for locale in ("de", "fr", "ja", "zh-hans")
                ):
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
