#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PRODUCT_REPO = REPO_ROOT.parent / "automic-vault"
PRODUCT_REPO_ENV = "AUTOMIC_VAULT_REPO_PATH"
PRODUCT_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$")
SCAN_LOG_ROW_RE = re.compile(r"^\|\s*[0-9]+\s*\|")


def default_product_repo() -> Path:
    return Path(os.environ.get(PRODUCT_REPO_ENV, DEFAULT_PRODUCT_REPO)).expanduser()


def read_product_version(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        raise SystemExit(f"Could not read product version source {path}: {err}") from err

    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, re.MULTILINE)
    if not match:
        raise SystemExit(f"Could not find package version in {path}")

    version = match.group(1)
    if not PRODUCT_VERSION_RE.fullmatch(version):
        raise SystemExit(f"Unexpected product version in {path}: {version}")
    return version


def count_scanned_packages(path: Path) -> int:
    try:
        count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if SCAN_LOG_ROW_RE.match(line))
    except OSError as err:
        raise SystemExit(f"Could not read scan log {path}: {err}") from err

    if count <= 0:
        raise SystemExit(f"Could not find scan log entries in {path}")
    return count


def website_inputs(product_repo: Path | None = None) -> dict[str, Any]:
    root = product_repo or default_product_repo()
    return {
        "schemaVersion": 1,
        "generatedAt": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "productVersion": read_product_version(root / "Cargo.toml"),
        "scannedPackageCount": count_scanned_packages(root / "data" / "radioisotopes" / "SCAN_LOG.md"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print deploy-time product inputs for the static website.")
    parser.add_argument(
        "--product-repo",
        default=None,
        help=f"Main Automic Vault checkout. Defaults to ${PRODUCT_REPO_ENV} or ../automic-vault.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    product_repo = Path(args.product_repo).expanduser() if args.product_repo else None
    json.dump(website_inputs(product_repo), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
