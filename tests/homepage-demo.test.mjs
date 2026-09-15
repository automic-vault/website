import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import { test } from 'node:test';

const source = readFileSync(new URL('../www/homepage.js', import.meta.url), 'utf8');
test('loops AWS and Claude Code scenes, pauses without losing position, and offers static reduced-motion scenes', () => {
  for (const reduced of [false, true]) {
    let interval, click, arrival;
    const fields = {};
    const field = key => fields[key] ??= { hidden: false, textContent: '' };
    field('demo-play').addEventListener = (_, handler) => { click = handler; };
    const document = {
      hidden: false,
      querySelector: () => ({ querySelector: selector => field(selector.slice(6, -1)) }),
      addEventListener: (_, handler) => { document.visibilityChanged = handler; },
    };
    const motion = { matches: reduced, addEventListener: (_, handler) => { motion.changed = handler; } };
    runInNewContext(source, {
      document, matchMedia: () => motion,
      setInterval: handler => { interval = handler; return 1; },
      clearInterval: () => { interval = undefined; },
      IntersectionObserver: class { constructor(handler) { arrival = handler; } observe() {} },
    });
    const advance = count => { for (let n = 0; n < count; n++) interval(); };
    arrival([{ isIntersecting: true }]);
    if (reduced) {
      assert.equal(interval, undefined);
      assert.equal(field('approval').hidden, false);
      assert.equal(field('demo-play').textContent, 'Next demo →');
      click();
      assert.match(field('approval-title').textContent, /Claude Code.*GitHub/);
      assert.equal(field('approval-icon').src, '/assets/claude-icon.svg');
      assert.equal(interval, undefined);
      click();
      assert.match(field('approval-title').textContent, /Terminal.*AWS/);
      continue;
    }
    advance(24);
    assert.equal(field('read-command').textContent, 'aws s3 ls');
    assert.equal(field('notification').hidden, false);
    assert.equal(field('approval').hidden, true);
    click();
    assert.equal(interval, undefined);
    arrival([{ isIntersecting: false }]);
    arrival([{ isIntersecting: true }]);
    assert.equal(interval, undefined, 'scrolling must not override manual pause');
    click();
    assert.equal(field('read-command').textContent, 'aws s3 ls', 'resume retains position');
    while (field('approval').hidden) advance(1);
    assert.equal(field('wait').hidden, false);
    assert.match(field('write-command').textContent, /^aws ec2 terminate-instances/);
    advance(71);
    assert.match(field('approval-title').textContent, /Terminal/);
    advance(1);
    assert.match(field('session').textContent, /Claude Code/);
    assert.equal(field('approval').hidden, true);
    while (field('notification').hidden) advance(1);
    assert.equal(field('read-command').textContent, 'ssh deploy@staging.example.com uptime');
    assert.equal(field('policy').textContent, 'Authorized by Allow Authentication policy');
    assert.equal(field('approval-icon').src, '/assets/claude-icon.svg');
    while (field('approval').hidden) advance(1);
    assert.equal(field('write-command').textContent, 'gh pr merge 42 --squash --repo acme/web');
    assert.equal(field('secrets').textContent, 'GH_TOKEN');
    document.hidden = true;
    document.visibilityChanged();
    assert.equal(interval, undefined);
    document.hidden = false;
    document.visibilityChanged();
    advance(72);
    assert.match(field('session').textContent, /Terminal/);
    arrival([{ isIntersecting: false }]);
    assert.equal(interval, undefined);
    arrival([{ isIntersecting: true }]);
    motion.matches = true;
    motion.changed();
    assert.equal(interval, undefined);
    assert.equal(field('approval').hidden, false);
  }
});
