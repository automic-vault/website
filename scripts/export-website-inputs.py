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
DEFAULT_AV_DB_ROOT = REPO_ROOT.parent / "av.db"
PRODUCT_REPO_ENV = "AUTOMIC_VAULT_REPO_PATH"
AV_DB_ROOT_ENV = "AV_DB_ROOT"
PRODUCT_VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.-]+)?$")
SCAN_LOG_ROW_RE = re.compile(r"^\|\s*[0-9]+\s*\|")


def default_product_repo() -> Path:
    return Path(os.environ.get(PRODUCT_REPO_ENV, DEFAULT_PRODUCT_REPO)).expanduser()


def default_av_db_root() -> Path:
    return Path(os.environ.get(AV_DB_ROOT_ENV, DEFAULT_AV_DB_ROOT)).expanduser()


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


def count_package_database_entries(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as err:
        raise SystemExit(f"Could not read package database {path}: {err}") from err
    except json.JSONDecodeError as err:
        raise SystemExit(f"Could not parse package database {path}: {err}") from err

    entries = data.get("entries")
    if isinstance(entries, dict) and entries:
        return len(entries)

    package_count = 0
    for key in ("formulas", "casks", "npms"):
        packages = data.get(key)
        if isinstance(packages, dict):
            package_count += len(packages)

    if package_count <= 0:
        raise SystemExit(f"Could not find package entries in {path}")
    return package_count


def scanned_package_count(product_repo: Path, av_db_root: Path) -> int:
    scan_log_paths = [
        av_db_root / "data" / "radioisotopes" / "SCAN_LOG.md",
        product_repo / "data" / "radioisotopes" / "SCAN_LOG.md",
    ]
    for path in scan_log_paths:
        if path.exists():
            return count_scanned_packages(path)

    package_database = av_db_root / "cache" / "automic-vault" / "db.json"
    if package_database.exists():
        return count_package_database_entries(package_database)

    searched = ", ".join(str(path) for path in [*scan_log_paths, package_database])
    raise SystemExit(f"Could not find scanned package source. Searched: {searched}")


def website_inputs(product_repo: Path | None = None, av_db_root: Path | None = None) -> dict[str, Any]:
    root = product_repo or default_product_repo()
    db_root = av_db_root or default_av_db_root()
    return {
        "schemaVersion": 1,
        "generatedAt": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "productVersion": read_product_version(root / "Cargo.toml"),
        "scannedPackageCount": scanned_package_count(root, db_root),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print deploy-time product inputs for the static website.")
    parser.add_argument(
        "--product-repo",
        default=None,
        help=f"Main Automic Vault checkout. Defaults to ${PRODUCT_REPO_ENV} or ../automic-vault.",
    )
    parser.add_argument(
        "--av-db-root",
        default=None,
        help=f"av.db checkout. Defaults to ${AV_DB_ROOT_ENV} or ../av.db.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    product_repo = Path(args.product_repo).expanduser() if args.product_repo else None
    av_db_root = Path(args.av_db_root).expanduser() if args.av_db_root else None
    json.dump(website_inputs(product_repo, av_db_root), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
