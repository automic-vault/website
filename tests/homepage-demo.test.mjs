import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { test } from 'node:test';

const source = readFileSync(new URL('../www/homepage.js', import.meta.url), 'utf8');
test('demo shows policy authorization before human Approval, supports pause/replay, and respects reduced motion', () => {
  for (const reduced of [false, true]) {
    let interval, click, arrival;
    const fields = Object.fromEntries(['read-command', 'write-command', 'output', 'notification', 'approval', 'wait'].map(key => [key, { hidden: false, textContent: '' }]));
    fields['read-command'].textContent = 'aws s3 ls';
    fields['write-command'].textContent = 'aws ec2 terminate-instances --instance-ids i-0123456789abcdef0';
    fields['demo-play'] = { disabled: true, addEventListener: (_, handler) => { click = handler; } };
    runInNewContext(source, {
      document: { querySelector: () => ({ querySelector: selector => fields[selector.slice(6, -1)] }), addEventListener() {} },
      matchMedia: () => ({ matches: reduced, addEventListener() {} }),
      setInterval: handler => { interval = handler; return 1; },
      clearInterval: () => { interval = undefined; },
      IntersectionObserver: class { constructor(handler) { arrival = handler; } observe() {} disconnect() {} },
    });
    assert.equal(fields['demo-play'].disabled, false);
    arrival([{ isIntersecting: true }]);
    if (!reduced) {
      assert.equal(fields.approval.hidden, true);
      for (let n = 0; n < 24; n++) interval();
      assert.equal(fields['read-command'].textContent, 'aws s3 ls');
      assert.equal(fields.notification.hidden, false);
      assert.equal(fields.output.hidden, false);
      assert.equal(fields.approval.hidden, true);
      click();
      assert.equal(interval, undefined);
      click();
      for (let n = 0; n < 116; n++) interval();
    }
    assert.equal(interval, undefined);
    assert.equal(fields.approval.hidden, false);
    assert.equal(fields.wait.hidden, false);
    assert.equal(fields.notification.hidden, true);
    assert.equal(fields['write-command'].textContent, 'aws ec2 terminate-instances --instance-ids i-0123456789abcdef0');
    assert.equal(fields['demo-play'].textContent, 'Replay demo ↻');
  }
});
