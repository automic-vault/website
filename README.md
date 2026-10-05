# Automic Vault Website

Source and deployment configuration for <https://www.automicvault.com/>.

The site is static HTML and CSS in `www/`, with generated localization,
S3/CloudFront deployment, and a Lambda that redirects download URLs to the
latest GitHub release and serves the all-time installer download count.

`/downloads.json` sums stable-release DMG downloads, including legacy `v` tags,
across GitHub release pages. CloudFront caches the response for one hour. The
homepage omits the statistic if it cannot load a valid count. This is a count of
downloads, including repeat downloads and upgrades, not unique users; deleted
GitHub assets are unavailable to the total. The Lambda needs no GitHub token
or additional AWS permissions.

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

The English landing page uses the Tinycast-inspired direction in `www/homepage.css`,
with an illustrated AWS demo in `www/homepage.js` and real product captures.
Translated landing pages retain the prior design while the English direction is reviewed. All five
sections have screenshots, including Project Values and pending iPhone requests
from two Macs. Keep captures, intrinsic dimensions, alt descriptions, and captions
aligned across all five languages. New Japanese acquisition copy still needs
native-language review before publication.

`/approvals.json` publishes only the all-time count of PostHog `approve` events
for `app_name = Automic Vault` in project 417890. These are recorded explicit
human Approvals, not automatic policy decisions or proof of completed Secret
Use. Telemetry delivery and retention limit the count. It is cached for one hour
and loads independently of downloads.

Configure `POSTHOG_RO_API_KEY` in the release redirect Lambda's encrypted
environment in the region named by CloudFront's Lambda origin (`us-east-2`
for the production distribution). An older same-named function exists in
`us-east-1`; it does not serve the website. Use an explicit `--region` when
configuring the key. Configure the environment using a project-restricted key with query read access. Never put it
in `www/`, a committed file, or browser code. Routine deployments preserve the
Lambda environment; they do not need the key locally. The public endpoint accepts
no query parameters or SQL and returns only `{ "total": number }`.
