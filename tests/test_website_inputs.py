import importlib.util
import html.parser
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
import urllib.parse


ROOT = pathlib.Path(__file__).resolve().parents[1]
WEBSITE_INPUTS_SCRIPT = ROOT / "scripts" / "export-website-inputs.py"
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


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_product_repo(root: pathlib.Path, version: str = "1.2.3") -> pathlib.Path:
    root.mkdir(parents=True)
    (root / "Cargo.toml").write_text(f'version = "{version}"\n', encoding="utf-8")
    return root


def write_scan_log(root: pathlib.Path) -> pathlib.Path:
    (root / "data" / "radioisotopes").mkdir(parents=True)
    (root / "data" / "radioisotopes" / "SCAN_LOG.md").write_text(
        "\n".join(
            [
                "| # | Package |",
                "| 1 | awscli |",
                "| nope | ignored |",
                "| 2 | gh |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root


def write_package_database(root: pathlib.Path) -> pathlib.Path:
    cache_dir = root / "cache" / "automic-vault"
    cache_dir.mkdir(parents=True)
    (cache_dir / "db.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "entries": {
                    "awscli": {},
                    "gh": {},
                    "ripgrep": {},
                },
            }
        ),
        encoding="utf-8",
    )
    return root


def write_current_package_database(root: pathlib.Path) -> pathlib.Path:
    root.mkdir(parents=True)
    (root / "db.json").write_text(
        json.dumps(
            {
                "schema": 1,
                "sources": {
                    "db": {
                        "schema": 1,
                        "entries": {
                            "awscli": {},
                            "gh": {},
                            "ripgrep": {},
                            "uv": {},
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return root


def write_combined_packages(root: pathlib.Path) -> pathlib.Path:
    combined = root / "combined"
    combined.mkdir(parents=True)
    (combined / "awscli.yml").write_text("name: awscli\n", encoding="utf-8")
    (combined / "gh.yml").write_text("name: gh\n", encoding="utf-8")
    return root


class WebsiteInputsExportTests(unittest.TestCase):
    def test_website_inputs_export_product_owned_contract(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_contract_test")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_product_repo(tmp_path / "automic-vault")
            av_db_root = write_scan_log(tmp_path / "av.db")
            payload = module.website_inputs(product_repo, av_db_root)

        self.assertEqual(payload["schemaVersion"], 1)
        self.assertRegex(payload["generatedAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertRegex(payload["productVersion"], module.PRODUCT_VERSION_RE)
        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_cli_prints_json_to_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_product_repo(tmp_path / "automic-vault")
            av_db_root = write_scan_log(tmp_path / "av.db")
            result = subprocess.run(
                [
                    sys.executable,
                    str(WEBSITE_INPUTS_SCRIPT),
                    "--product-repo",
                    str(product_repo),
                    "--av-db-root",
                    str(av_db_root),
                ],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["productVersion"], "1.2.3")
        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_website_inputs_falls_back_to_av_db_cache(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_cache_test")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_product_repo(tmp_path / "automic-vault")
            av_db_root = write_package_database(tmp_path / "av.db")
            payload = module.website_inputs(product_repo, av_db_root)

        self.assertEqual(payload["scannedPackageCount"], 3)

    def test_website_inputs_supports_current_package_database(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_current_db_test")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_product_repo(tmp_path / "av2")
            av_db_root = write_current_package_database(tmp_path / "run")
            payload = module.website_inputs(product_repo, av_db_root)

        self.assertEqual(payload["scannedPackageCount"], 4)

    def test_legacy_product_scan_log_still_works(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_legacy_test")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_scan_log(write_product_repo(tmp_path / "automic-vault"))
            av_db_root = tmp_path / "av.db"
            payload = module.website_inputs(product_repo, av_db_root)

        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_website_inputs_falls_back_to_combined_packages(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_combined_test")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = pathlib.Path(tmp)
            product_repo = write_product_repo(tmp_path / "automic-vault")
            av_db_root = write_combined_packages(tmp_path / "av.db")
            payload = module.website_inputs(product_repo, av_db_root)

        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_product_version_reader_rejects_unexpected_versions(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_version_test")
        with tempfile.TemporaryDirectory() as tmp:
            version_file = pathlib.Path(tmp) / "Cargo.toml"
            version_file.write_text('version = "latest"\n', encoding="utf-8")

            with self.assertRaises(SystemExit):
                module.read_product_version(version_file)


class StaticHtmlAnalyticsTests(unittest.TestCase):
    def test_all_static_html_pages_embed_google_analytics(self):
        missing = []
        for page in sorted((ROOT / "www").rglob("*.html")):
            text = page.read_text(encoding="utf-8")
            if GA_SCRIPT not in text or GA_CONFIG not in text:
                missing.append(str(page.relative_to(ROOT)))

        self.assertEqual(missing, [])

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
                self.assertIn("styles.css?v=106", text)
                self.assertIn("landing-pages.css?v=2", text)

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
                self.assertIn("app.js?v=25", text)

        self.assertTrue(pages)

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
