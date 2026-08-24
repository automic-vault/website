# Automic Vault Website

Source and deployment configuration for <https://www.automicvault.com/>.

The site is static HTML and CSS in `www/`, with generated localization,
S3/CloudFront deployment, and a Lambda that redirects download URLs to the
latest GitHub release.

## Checks

```sh
python3 -m unittest discover -s tests
scripts/deploy-www.sh --prepare-only
```

Regenerate the versioned manual and hardener pages with `node scripts/generate-docs.mjs`.

## Deploy

```sh
scripts/deploy-www.sh
```

Use `--static-only` to skip Lambda, CloudFront, and certificate configuration.
The full deploy creates or updates the private release redirect Lambda and its
CloudFront routes. The static sync never uploads product release artifacts.
