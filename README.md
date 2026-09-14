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

Regenerate the versioned manual and hardener pages from the sibling
`../av/src/isotopes/hardeners/*.md` files with `node scripts/generate-docs.mjs`.

## Deploy

```sh
scripts/deploy-www.sh
```

Use `--static-only` to skip Lambda, CloudFront, and certificate configuration.
The full deploy creates or updates the private release redirect Lambda and its
CloudFront routes. The static sync never uploads product release artifacts.

## Homepage screenshots

The landing pages use real product captures, with no CLI examples. All five
sections have screenshots, including Project Values and pending iPhone requests
from two Macs. Keep captures, intrinsic dimensions, alt descriptions, and captions
aligned across all five languages. New Japanese acquisition copy still needs
native-language review before publication.
