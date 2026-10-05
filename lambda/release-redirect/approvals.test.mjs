import assert from 'node:assert/strict';
import { test } from 'node:test';
import { approvalTotal } from './approvals.mjs';

test('queries only the fixed human approval aggregate and returns only its count', async () => {
  const total = await approvalTotal(async (url, options) => {
    assert.equal(url, 'https://us.posthog.com/api/projects/417890/query/');
    assert.equal(options.headers.authorization, 'Bearer test-key');
    assert.equal(options.redirect, 'error');
    assert.equal(JSON.parse(options.body).query.query,
      "SELECT count() FROM events WHERE event = 'approve' AND properties.app_name = 'Automic Vault'");
    return { ok: true, json: async () => ({ results: [[12345]], private_metadata: 'not public' }) };
  }, 'test-key');
  assert.equal(total, 12345);
});

test('missing credentials, unavailable data, and malformed totals never become zero', async () => {
  await assert.rejects(approvalTotal(() => assert.fail('must not fetch'), ''));
  await assert.rejects(approvalTotal(async () => ({ ok: false, status: 403 }), 'test-key'));
  for (const results of [undefined, [], [[-1]], [['12']], [[null]], [[1.5]], [[1, 2]], [[1], [2]]]) {
    await assert.rejects(approvalTotal(async () => ({ ok: true, json: async () => ({ results }) }), 'test-key'));
  }
  assert.equal(await approvalTotal(async () => ({ ok: true, json: async () => ({ results: [[0]] }) }), 'test-key'), 0);
});
