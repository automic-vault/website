# Automic Vault Website

## Scope

This repository owns the Automic Vault S3-backed static website and its
CloudFront distribution.

Work here should be limited to:
- HTML pages
- CSS stylesheets
- static copy
- images and other public assets
- static metadata such as the sitemap, robots, llms, text,
  markdown, and JSON representations of website content

Do not add product runtime code, server code, package manager behavior, helper
behavior, app/CLI behavior, or package-origin server code to this repository.

## Package Catalog Boundary

The live package catalog and its Rust origin are owned by `~/src/pkgdb`.

`/pkg/`, localized `/de/pkg/`, `/fr/pkg/`, `/ja/pkg/`, `/zh-hans/pkg/`, package
sitemaps, markdown alternates, `/pkg/styles.css`, `/pkg/search.js`, and
`/pkg/search.json` remain Atlas origin routes until the staged `pkg.so`
redirect is explicitly enabled.

This repository keeps the CloudFront behaviors that route those paths to the
Atlas origin. Do not duplicate the package renderer, SQLite pipeline, service,
or deployment scripts here.

## Release Artifact Boundary

The product repository owns the release assets. This repository owns the
website download URLs and the Lambda that redirects both `.dmg` routes to the
latest GitHub release asset. The static deploy must not upload a `.dmg`.

The product repository still owns `/scanner.gz` and `/scanner.sh`. The static
website deploy excludes those objects and must not delete or overwrite them.

## Deployment Safety

Run static deploys through `scripts/deploy-www.sh`. Use `--prepare-only` before
mutating S3 or CloudFront.

This `AGENTS.md` file is local repository guidance only. It must not be synced
or uploaded to S3.

## Editing Principles

Prioritize:
- clear page purpose
- readable HTML
- small CSS changes that fit the existing stylesheet structure
- stable URLs
- accessible text and image alternatives
- low-surprise changes

Preserve the existing shape of the website unless the task explicitly asks for
a redesign. Keep SEO-facing alternate formats aligned with canonical page
content when editing them together.

Commit as Codex after each completed job.
