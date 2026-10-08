import assert from 'node:assert/strict';
import { readFileSync, mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import test from 'node:test';

const script = readFileSync(new URL('../scripts/deploy-www.sh', import.meta.url), 'utf8');
const source = script.split('cat >"${function_file}" <<EOF\n')[1].split('\nEOF')[0]
  .replace('${WWW_CANONICAL_HOST}', 'www.automicvault.com');
const { handler } = vm.runInNewContext(`${source}; ({ handler })`);
function request(uri, accept, host = 'www.automicvault.com') {
  return handler({ request: { uri, method: 'GET', headers: {
    host: { value: host }, ...(accept ? { accept: { value: accept } } : {}),
  }, querystring: {} } });
}

test('nested pages, homepage, explicit HTML, and localized routes negotiate formats', () => {
  for (const route of ['/', '/docs/', '/docs/blessed-scripts/', '/docs/reentrant-scripts/', '/docs/hardeners/gh/', '/blog/example/', '/ja/about/']) {
    const base = `${route}index`;
    for (const [accept, suffix] of [['text/markdown', '.md'], ['text/plain', '.txt'], ['text/html', '.html']]) {
      assert.equal(request(route, accept).uri, route === "/" && accept === "text/html" ? "/" : base + suffix);
      assert.equal(request(base + '.html', accept).uri, base + suffix);
      if (route !== '/' && accept !== 'text/html') assert.equal(request(route.slice(0, -1), accept).uri, base + suffix);
    }
  }
  assert.equal(request('/', 'application/json').uri, '/index.json');
});

test('quality, explicit exclusions, case, and wildcards select the right format', () => {
  for (const [accept, suffix] of [
    [undefined, '.html'], ['*/*', '.html'], ['text/*', '.html'],
    ['text/html,application/xhtml+xml,*/*;q=0.8', '.html'],
    ['text/markdown;q=0.5,text/html;q=0.9', '.html'],
    ['text/markdown,text/html', '.md'], ['text/plain;q=1,text/markdown;q=0.5', '.txt'],
    ['TEXT/MARKDOWN; charset=utf-8', '.md'],
    ['text/markdown;q=0,*/*;q=1', '.html'],
    ['text/html;q=0,text/markdown;q=0.8,*/*;q=0.5', '.md'],
    ['text/markdown;q=bogus,text/plain', '.txt'],
    ['text/markdown;q=2,text/plain', '.txt'],
  ]) assert.equal(request('/docs/', accept).uri, '/docs/index' + suffix, accept);
});

test('assets, explicit formats, installers, and redirects retain their behavior', () => {
  for (const uri of ['/install.sh', '/scanner.sh', '/scanner.gz', '/scanner.tgz', '/assets/icon.webp', '/docs/index.md', '/llms.txt', '/downloads.json']) {
    assert.equal(request(uri, 'text/markdown').uri, uri);
    assert.equal(request(uri, 'text/plain').uri, uri);
  }
  assert.equal(request('/docs/', 'text/markdown', 'automicvault.com').headers.location.value, 'https://www.automicvault.com/docs/');
  assert.equal(request('/pkg/foo/', 'text/markdown').headers.location.value, 'https://pkg.so/pkg/foo/');
  assert.equal(request('/missing', 'application/json').statusCode, 404);
  assert.ok(Buffer.byteLength(source) < 10240, 'CloudFront Function size limit');
  assert.match(script, /Header: "Vary",\s+Value: "Accept, Accept-Encoding"/);
});

test('staging generates readable formats and preserves authored content', () => {
  const directory = mkdtempSync(path.join(tmpdir(), 'av-formats-'));
  try {
    mkdirSync(path.join(directory, 'docs'));
    writeFileSync(path.join(directory, 'index.html'), '<nav>Navigation noise</nav><main><h1>Public page</h1><p>A &amp; B</p><pre><code>gh repo view</code></pre><script>secretScript()</script></main>');
    writeFileSync(path.join(directory, 'docs/index.html'), '<h1>Rendered</h1>');
    writeFileSync(path.join(directory, 'docs/index.md'), '# Authored guide\n\n`av bless`\n');
    writeFileSync(path.join(directory, 'docs/index.txt'), 'Authored plain text\n');
    execFileSync('node', [new URL('../scripts/generate-page-formats.mjs', import.meta.url).pathname, directory]);
    const markdown = readFileSync(path.join(directory, 'index.md'), 'utf8');
    const plain = readFileSync(path.join(directory, 'index.txt'), 'utf8');
    assert.match(markdown, /# Public page/);
    assert.match(markdown, /gh repo view/);
    assert.match(plain, /A & B/);
    assert.doesNotMatch(markdown, /Navigation noise|secretScript|<script>/);
    assert.equal(readFileSync(path.join(directory, 'docs/index.md'), 'utf8'), '# Authored guide\n\n`av bless`\n');
    assert.equal(readFileSync(path.join(directory, 'docs/index.txt'), 'utf8'), 'Authored plain text\n');
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
