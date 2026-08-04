# Automic Vault Website

## Scope

This repository owns the Automic Vault S3-backed static website and its
CloudFront distribution, including the release redirect Lambda and deployment
automation.

Work here should be limited to:
- HTML pages
- CSS stylesheets
- static copy
- images and other public assets
- static metadata such as the sitemap, robots, llms, text,
  markdown, and JSON representations of website content
- localization data and generation
- website deployment and CloudFront configuration
- the release redirect Lambda and its tests

Do not add product runtime or server behavior, package manager behavior, helper
behavior, app/CLI behavior, or package-catalog code to this repository.

## Compatibility Boundaries

Keep legacy `/pkg/` redirects to `pkg.so`; do not reintroduce a package origin
or rendered package catalog here.

The website download URLs use the Lambda to find the latest GitHub release.
The static deploy must not upload a `.dmg`.

The static deploy must preserve the externally managed `/scanner.gz` and
`/scanner.sh` objects.

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
