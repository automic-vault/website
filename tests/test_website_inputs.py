import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
WEBSITE_INPUTS_SCRIPT = ROOT / "scripts" / "export-website-inputs.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_product_repo(root: pathlib.Path, version: str = "1.2.3") -> pathlib.Path:
    (root / "data" / "radioisotopes").mkdir(parents=True)
    (root / "Cargo.toml").write_text(f'version = "{version}"\n', encoding="utf-8")
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


class WebsiteInputsExportTests(unittest.TestCase):
    def test_website_inputs_export_product_owned_contract(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_contract_test")
        with tempfile.TemporaryDirectory() as tmp:
            payload = module.website_inputs(write_product_repo(pathlib.Path(tmp)))

        self.assertEqual(payload["schemaVersion"], 1)
        self.assertRegex(payload["generatedAt"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertRegex(payload["productVersion"], module.PRODUCT_VERSION_RE)
        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_cli_prints_json_to_stdout(self):
        with tempfile.TemporaryDirectory() as tmp:
            product_repo = write_product_repo(pathlib.Path(tmp))
            result = subprocess.run(
                [sys.executable, str(WEBSITE_INPUTS_SCRIPT), "--product-repo", str(product_repo)],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["productVersion"], "1.2.3")
        self.assertEqual(payload["scannedPackageCount"], 2)

    def test_product_version_reader_rejects_unexpected_versions(self):
        module = load_module(WEBSITE_INPUTS_SCRIPT, "export_website_inputs_version_test")
        with tempfile.TemporaryDirectory() as tmp:
            version_file = pathlib.Path(tmp) / "Cargo.toml"
            version_file.write_text('version = "latest"\n', encoding="utf-8")

            with self.assertRaises(SystemExit):
                module.read_product_version(version_file)


if __name__ == "__main__":
    unittest.main()
