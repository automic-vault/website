import assert from "node:assert/strict";
import { releaseAssetUrl } from "./index.mjs";

const release = {
  tag_name: "2.2.1",
  draft: false,
  prerelease: false,
  assets: [{
    name: "Automic-Vault-2.2.1.dmg",
    browser_download_url: "https://github.com/automic-vault/automic-vault/releases/download/2.2.1/Automic-Vault-2.2.1.dmg",
  }],
};

assert.equal(releaseAssetUrl(release), release.assets[0].browser_download_url);
assert.throws(() => releaseAssetUrl({ ...release, draft: true }));
assert.throws(() => releaseAssetUrl({
  ...release,
  assets: [{ ...release.assets[0], browser_download_url: "https://example.com/release.dmg" }],
}));

// Exercise both routes and ensure upstream failures never become a zero total.
const { handler } = await import('./index.mjs');
const originalFetch = globalThis.fetch;
try {
  globalThis.fetch = async () => ({ ok: true, json: async () => [
    { ...release, assets: [{ ...release.assets[0], id: 1, download_count: 1234 }] },
  ] });
  const count = await handler({ rawPath: '/downloads.json' });
  assert.equal(count.statusCode, 200);
  assert.deepEqual(JSON.parse(count.body), { total: 1234 });
  assert.match(count.headers['cache-control'], /s-maxage=3600/);
  assert.match(count.headers['content-type'], /application\/json/);
  globalThis.fetch = async () => ({ ok: true, json: async () => release });
  assert.equal((await handler({ rawPath: '/av.dmg' })).headers.location, release.assets[0].browser_download_url);
  globalThis.fetch = async () => ({ ok: false, status: 403 });
  const originalError = console.error;
  console.error = () => {};
  try {
    const failure = await handler({ rawPath: '/downloads.json' });
    assert.equal(failure.statusCode, 502);
    assert.equal(failure.headers['cache-control'], 'no-store');
  } finally {
    console.error = originalError;
  }
} finally {
  globalThis.fetch = originalFetch;
}
