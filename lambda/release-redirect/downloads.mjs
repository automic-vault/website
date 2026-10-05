const releasesUrl = 'https://api.github.com/repos/automic-vault/automic-vault/releases';

// Count installer assets only: checksums and SBOMs are not app downloads.
export async function downloadTotal(fetchImpl = fetch) {
  const signal = AbortSignal.timeout(7000);
  const seen = new Set();
  let total = 0;
  for (let page = 1; page <= 20; page++) {
    const response = await fetchImpl(`${releasesUrl}?per_page=100&page=${page}`, {
      headers: {
        accept: 'application/vnd.github+json',
        'user-agent': 'automic-vault-download-count',
        'x-github-api-version': '2022-11-28',
      },
      signal,
      redirect: 'error',
    });
    if (!response.ok) throw new Error(`GitHub releases API returned ${response.status}`);
    const releases = await response.json();
    if (!Array.isArray(releases)) throw new Error('Invalid release list');
    for (const release of releases) {
      if (release.draft || release.prerelease || !/^v?\d+\.\d+\.\d+$/.test(release.tag_name)) continue;
      const version = release.tag_name.replace(/^v/, '');
      if (!Array.isArray(release.assets)) throw new Error('Invalid asset list');
      for (const asset of release.assets) {
        if (asset.name !== `Automic-Vault-${version}.dmg`) continue;
        if (!Number.isSafeInteger(asset.id) || asset.id <= 0 ||
            !Number.isSafeInteger(asset.download_count) || asset.download_count < 0) {
          throw new Error('Invalid download count');
        }
        if (seen.has(asset.id)) continue;
        seen.add(asset.id);
        total += asset.download_count;
        if (!Number.isSafeInteger(total)) throw new Error('Download count overflow');
      }
    }
    if (releases.length < 100) return total;
  }
  throw new Error('Release pagination limit reached');
}
