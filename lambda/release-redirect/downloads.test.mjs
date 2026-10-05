import assert from 'node:assert/strict';
import { test } from 'node:test';
import { downloadTotal } from './downloads.mjs';

const release = (id, count, tag = '1.2.3') => ({
  tag_name: tag, draft: false, prerelease: false,
  assets: [{ id, name: `Automic-Vault-${tag.replace(/^v/, '')}.dmg`, download_count: count }],
});
const response = data => ({ ok: true, json: async () => data });

test('counts stable installer downloads, including legacy v tags, excluding other assets', async () => {
  const stable = release(1, 42);
  stable.assets.push({ id: 99, name: 'SHA256SUMS', download_count: 100 });
  assert.equal(await downloadTotal(async () => response([
    stable, release(2, 8, 'v1.0.0'),
    { ...release(3, 100), draft: true },
    { ...release(4, 100), prerelease: true },
    release(5, 100, 'nightly'),
  ])), 50);
});

test('paginates without double counting assets shifted by a new release', async () => {
  const urls = [];
  const first = Array.from({ length: 100 }, (_, i) => release(i + 1, 1));
  assert.equal(await downloadTotal(async url => {
    urls.push(url);
    return response(urls.length === 1 ? first : [release(100, 1), release(101, 2)]);
  }), 102);
  assert.match(urls[1], /page=2$/);
});

test('does not present partial totals after upstream errors or malformed counts', async () => {
  await assert.rejects(downloadTotal(async () => ({ ok: false, status: 403 })));
  for (const count of [-1, '42', null, 1.5, Number.MAX_SAFE_INTEGER + 1]) {
    await assert.rejects(downloadTotal(async () => response([release(1, count)])));
  }
  await assert.rejects(downloadTotal(async () => response({})));
  await assert.rejects(downloadTotal(async () => response([
    release(1, Number.MAX_SAFE_INTEGER), release(2, 1),
  ])));
});

test('fails instead of silently truncating at the pagination bound', async () => {
  const page = Array.from({ length: 100 }, (_, i) => release(i + 1, 1));
  await assert.rejects(downloadTotal(async () => response(page)), /pagination limit/);
});
