# Automic Vault Website

Static website repository for <https://www.automicvault.com/>.

The product repository still owns release artifacts and scanner publishing.
`~/src/av.db` owns package database generation and `/db.json` export artifacts.
This repo owns static pages, assets, static localization, S3/CloudFront
configuration, the GitHub release redirect Lambda, and the Atlas `av-web`
package-origin service.

## Checks

```sh
python3 scripts/generate-www-i18n.py --check
node scripts/generate-llms-full.mjs www /tmp/llms-full.txt
node --test lambda/release-redirect/index.test.mjs
scripts/deploy-www.sh --prepare-only
```

## Deploy

```sh
scripts/deploy-www.sh
```

Use `--static-only` to skip Lambda, CloudFront, and certificate configuration.
The full deploy creates or updates the private release redirect Lambda and its
CloudFront routes. The static sync never uploads product release artifacts.

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
The refresh path also builds `../av.db/cache/cratesio/index.json` for Cargo
package pages; those crates.io records stay out of the exported `db.json`.

## Package Traffic Loop

Use the ops repo Search Console credentials to refresh `/pkg/` opportunities:

```sh
scripts/pkg-traffic-loop.mjs --days 90 --row-limit 25000
```

The script writes ignored artifacts to `cache/pkg-traffic-loop.json` and
`cache/pkg-traffic-loop.md`. Use the report to pick a high-impression package
query, improve the package renderer or metadata, verify with `cargo test`, and
commit the focused change before the next loop pass.
