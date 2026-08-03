# Automic Vault Website

Static website repository for <https://www.automicvault.com/>.

The product repository still owns release artifacts and scanner publishing.
`~/src/pkgdb` owns package database generation, the Rust package origin, Atlas
deployment, and the dedicated `pkg.so` CloudFront distribution.
This repo owns static pages, assets, static localization, S3/CloudFront
configuration for `atomicvault.com`, and the GitHub release redirect Lambda.

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

## Legacy Package Routes

The `atomicvault.com/pkg/` routes permanently redirect to their canonical
`pkg.so` pages through the viewer-request CloudFront Function. Deploy normally
to publish the redirects:

```sh
scripts/deploy-www.sh
```

For example, `/fr/pkg/brew/awscli/?source=old` redirects to
`https://pkg.so/fr/pkg/brew/awscli/?source=old`.

Package generation and Atlas deployment run from `~/src/pkgdb` with
`scripts/deploy-atlas.sh`.

## Package Traffic Loop

Use the ops repo Search Console credentials to refresh `/pkg/` opportunities:

```sh
scripts/pkg-traffic-loop.mjs --days 90 --row-limit 25000
```

The script writes ignored artifacts to `cache/pkg-traffic-loop.json` and
`cache/pkg-traffic-loop.md`. Use the report to pick a high-impression package
query, improve the package renderer or metadata in `../pkgdb`, verify there,
and commit the focused change before the next loop pass.
