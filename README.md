# Automic Vault Website

Static website repository for <https://www.automicvault.com/>.

The product repository still owns release artifacts and scanner publishing.
`~/src/av.db` owns package database generation and `/db.json` export artifacts.
This repo owns static pages, assets, static localization, S3/CloudFront
configuration, and the Atlas `av-web` package-origin service.

## Inputs

Deploy-time product values come from a JSON artifact exported by the product
repo:

```sh
python3 ../automic-vault/scripts/export-website-inputs.py --output /tmp/website-inputs.json
```

The artifact uses schema version 1 and provides the product version and scanned
Homebrew package count used while preparing the site.

## Checks

```sh
python3 scripts/generate-www-i18n.py --check
node scripts/generate-llms-full.mjs www /tmp/llms-full.txt
scripts/deploy-www.sh --prepare-only --inputs /tmp/website-inputs.json
```

## Deploy

```sh
scripts/deploy-www.sh --inputs /tmp/website-inputs.json
```

Use `--static-only` to skip CloudFront and certificate configuration. The deploy
script excludes package-origin routes and product-owned release artifacts.

## Package Origin

Build the private package SQLite artifact in `av.db`:

```sh
python3 ../av.db/scripts/hourly-maintenance.py --no-commit
```

Deploy the Atlas package origin from this repo:

```sh
scripts/deploy-pkg-origin.sh --skip-refresh --skip-sqlite
```

`AV_WEB_SQLITE_PATH` defaults to `../av.db/cache/pkg.sqlite`.
