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

The landing pages use real product captures, with no CLI examples. Two visible
slots are waiting for captures (marked `data-screenshot-needed` in each page):

- **Project Values:** one selected Secret Name with a Global Value and two
  Project Values. Show recognizable demo project paths; hide all Secret Values.
- **Multi-Mac Approval:** pending iPhone requests from two named Macs, plus one
  expanded request with its originating Mac, operation, and real Approval controls.
  Use demo requests with no private data.

Replace each slot with the supplied capture, including intrinsic dimensions and
an accurate alt description. Keep the captions and all five language versions
aligned. New Japanese acquisition copy still needs native-language review before
publication.
