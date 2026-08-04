const repository = "automic-vault/automic-vault";
const apiUrl = `https://api.github.com/repos/${repository}/releases/latest`;
const versionPattern = /^\d+\.\d+\.\d+$/;

export function releaseAssetUrl(release) {
  const version = release?.tag_name;
  if (release?.draft || release?.prerelease || !versionPattern.test(version)) {
    throw new Error("GitHub did not return a stable semantic-version release");
  }

  const name = `Automic-Vault-${version}.dmg`;
  const asset = release.assets?.find((candidate) => candidate.name === name);
  if (!asset) {
    throw new Error(`Release ${version} has no ${name} asset`);
  }

  const url = new URL(asset.browser_download_url);
  const expectedPath = `/${repository}/releases/download/${version}/${name}`;
  if (url.protocol !== "https:" || url.hostname !== "github.com" || url.pathname !== expectedPath || url.search || url.hash) {
    throw new Error("GitHub returned an unexpected release asset URL");
  }
  return url.href;
}

export async function handler() {
  try {
    const response = await fetch(apiUrl, {
      headers: {
        accept: "application/vnd.github+json",
        "user-agent": "automic-vault-release-redirect",
        "x-github-api-version": "2022-11-28",
      },
      signal: AbortSignal.timeout(5000),
    });
    if (!response.ok) {
      throw new Error(`GitHub releases API returned ${response.status}`);
    }

    return {
      statusCode: 302,
      headers: {
        "cache-control": "public, max-age=3600, s-maxage=3600",
        location: releaseAssetUrl(await response.json()),
      },
      body: "",
    };
  } catch (error) {
    console.error(error);
    return {
      statusCode: 502,
      headers: { "cache-control": "no-store" },
      body: "Release download is temporarily unavailable.\n",
    };
  }
}
