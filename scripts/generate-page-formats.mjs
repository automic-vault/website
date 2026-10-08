#!/usr/bin/env node

import { execFileSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

// Run on the staged public site, preserving authored alternate representations.
const site = process.argv[2];
if (!site) throw new Error('Usage: generate-page-formats.mjs <site-dir>');

function generate(directory) {
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      generate(file);
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      const markdown = file.replace(/\.html$/, '.md');
      const plain = file.replace(/\.html$/, '.txt');
      if (!existsSync(markdown)) {
        const html = readFileSync(file, 'utf8');
        const content = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i)?.[1] ?? html;
        writeFileSync(markdown, execFileSync('pandoc', ['--from=html', '--to=gfm-raw_html', '--wrap=none'], { input: content }));
      }
      if (!existsSync(plain)) {
        writeFileSync(plain, execFileSync('pandoc', ['--from=gfm', '--to=plain', '--wrap=none'], { input: readFileSync(markdown) }));
      }
    }
  }
}

generate(site);
