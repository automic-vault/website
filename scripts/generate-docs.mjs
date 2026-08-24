#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const docsDir = path.join(root, "www", "docs");
const manual = readFileSync(path.join(root, "scripts", "docs-manual.md"), "utf8");
const version = manual.match(/Automic Vault ([\d.]+) on/)?.[1];

if (!version) throw new Error("Could not read the documented version");

const cliVersion = execFileSync("av", ["--version"], { encoding: "utf8" }).trim().split(" ").at(-1);
if (cliVersion !== version) throw new Error(`Manual is ${version}, but installed av is ${cliVersion}`);

const hardeners = JSON.parse(execFileSync("av", ["hardeners", "--json"], {
  encoding: "utf8",
  maxBuffer: 16 * 1024 * 1024,
})).hardeners;

const pages = [
  {
    slug: "",
    title: "Automic Vault manual",
    lede: "Install Automic Vault, understand the operator console, and find the right reference.",
    description: `The source-checked Automic Vault ${version} manual for macOS.`,
    start: 0,
    end: "## Security foundations",
  },
  {
    slug: "security",
    title: "Security foundations",
    lede: "The request, identity, authority, delivery, and evidence boundaries behind every decision.",
    description: "How Automic Vault authorizes complete operations and where its security boundary ends.",
    start: "## Security foundations",
    end: "## App guide",
  },
  {
    slug: "app",
    title: "App guide",
    lede: "What every destination in the Automic Vault operator console shows and controls.",
    description: "A guide to every destination in the Automic Vault macOS app.",
    start: "## App guide",
    end: "## Approval and authority",
  },
  {
    slug: "authority",
    title: "Approval, authority, and secrets",
    lede: "Approval routes, temporary authority, Secret Value selection, and Access Levels.",
    description: "Automic Vault Approval, authorization, Secret Values, and Access Levels.",
    start: "## Approval and authority",
    end: "## Command reference",
  },
  {
    slug: "cli",
    title: "Command reference",
    lede: "The supported CLI surface, machine-readable catalogs, and exit behavior.",
    description: `Command reference for the Automic Vault ${version} CLI.`,
    start: "## Command reference",
    end: "## Common workflows",
  },
  {
    slug: "workflows",
    title: "Common workflows",
    lede: "Known-good paths for GitHub, AWS, Docker, Project Values, proxying, scripts, and signing.",
    description: "Common Automic Vault workflows for protected developer credentials.",
    start: "## Common workflows",
    end: "## Troubleshooting",
  },
  {
    slug: "troubleshooting",
    title: "Troubleshooting",
    lede: "Diagnose Approval, executable, Value selection, launcher, proxy, and Doctor failures.",
    description: "Troubleshooting and source references for Automic Vault.",
    start: "## Troubleshooting",
    end: null,
  },
];

const manualLinks = [
  ["", "Overview"],
  ["security", "Security foundations"],
  ["app", "App guide"],
  ["authority", "Approval and authority"],
  ["cli", "CLI reference"],
  ["workflows", "Workflows"],
  ["troubleshooting", "Troubleshooting"],
  ["hardeners", "Hardeners"],
];

function section(start, end) {
  const from = typeof start === "number" ? start : manual.indexOf(start);
  const to = end ? manual.indexOf(end) : manual.length;
  if (from < 0 || to < 0) throw new Error(`Missing manual boundary: ${start} / ${end}`);
  return manual.slice(from, to).trim();
}

function route(slug) {
  return slug ? `/docs/${slug}/` : "/docs/";
}

function titleCase(name) {
  const exact = {
    akamai: "Akamai", algolia: "Algolia", argocd: "Argo CD", "ast-cli": "Checkmarx AST CLI",
    aws: "AWS", buf: "Buf", brew: "Homebrew", circleci: "CircleCI", codex: "Codex",
    "cloudsmith-cli": "Cloudsmith CLI", docker: "Docker", doctl: "doctl", flyctl: "flyctl",
    gh: "GitHub CLI", glab: "glab", gptcommit: "GPTCommit", grafanactl: "grafanactl",
    hcloud: "Hetzner Cloud", "huggingface-cli": "Hugging Face CLI", "jfrog-cli": "JFrog CLI",
    k6: "Grafana k6", luarocks: "LuaRocks", "minio-mc": "MinIO Client",
    "netlify-cli": "Netlify CLI", node: "npm", pnpm: "pnpm", "qwen-code": "Qwen Code",
    "runpodctl": "RunPod CLI", s3cmd: "s3cmd", "sentry-cli": "Sentry CLI",
    "snowflake-cli": "Snowflake CLI", stripe: "Stripe CLI", sudo: "sudo", supabase: "Supabase",
    "transifex-cli": "Transifex CLI", vault: "HashiCorp Vault",
    "virustotal-cli": "VirusTotal CLI", vultr: "Vultr CLI", wsk: "OpenWhisk",
  };
  return exact[name] ?? name.split("-").map(word => word[0].toUpperCase() + word.slice(1)).join(" ");
}

function renderMarkdown(markdown) {
  return execFileSync("pandoc", ["--from=gfm", "--to=html", "--syntax-highlighting=none"], {
    input: markdown,
    encoding: "utf8",
    maxBuffer: 16 * 1024 * 1024,
  }).trim();
}

function nav(current, article, title) {
  const links = manualLinks.map(([slug, label]) => {
    const selected = current === slug || (current.startsWith("hardeners/") && slug === "hardeners");
    return `<li><a href="${route(slug)}"${selected ? ' aria-current="page"' : ""}>${label}</a></li>`;
  }).join("");
  const headings = [...article.matchAll(/<h([23]) id="([^"]+)">([\s\S]*?)<\/h\1>/g)]
    .filter(([, , , label], index) => index > 0 || label.replace(/<[^>]+>/g, "").trim() !== title)
    .map(([, level, id, label]) => `<li class="docs-nav-depth-${level}"><a href="#${id}">${label}</a></li>`)
    .join("");
  return `<nav class="docs-toc" aria-label="Documentation sections">
          <a class="docs-toc-title" href="/docs/">Manual</a>
          <section class="docs-nav-group">
            <h2>Documentation</h2>
            <ul>${links}</ul>
          </section>
${headings ? `          <section class="docs-nav-group">
            <h2>On this page</h2>
            <ul>${headings}</ul>
          </section>` : ""}
        </nav>`;
}

function htmlPage({ slug, title, lede, description, markdown }) {
  const pageRoute = route(slug);
  const markdownRoute = `${pageRoute}index.md`;
  const article = renderMarkdown(markdown);
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y78QKG1T9Y"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-Y78QKG1T9Y');
  </script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>${title} — Automic Vault</title>
  <meta name="description" content="${description}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Automic Vault">
  <meta property="og:title" content="${title}">
  <meta property="og:description" content="${description}">
  <meta property="og:url" content="https://www.automicvault.com${pageRoute}">
  <meta property="og:image" content="https://www.automicvault.com/preview.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${title}">
  <meta name="twitter:description" content="${description}">
  <meta name="twitter:image" content="https://www.automicvault.com/preview.jpg">
  <link rel="canonical" href="https://www.automicvault.com${pageRoute}">
  <link rel="alternate" type="text/markdown" title="Markdown" href="${markdownRoute}">
  <link rel="alternate" type="text/plain" title="llms.txt" href="/llms.txt">
  <script type="application/ld+json">
  {"@context":"https://schema.org","@type":"TechArticle","url":"https://www.automicvault.com${pageRoute}","headline":${JSON.stringify(title)},"description":${JSON.stringify(description)},"dateModified":"2026-08-23","author":{"@id":"https://www.automicvault.com/#organization"},"publisher":{"@id":"https://www.automicvault.com/#organization"},"about":{"@type":"SoftwareApplication","name":"Automic Vault","softwareVersion": "${version}","operatingSystem":"macOS","codeRepository":"https://github.com/automic-vault/automic-vault"}}
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&amp;family=Geist+Mono:wght@400;500;600;700&amp;display=swap" rel="stylesheet">
  <link rel="icon" href="/favicon.ico?v=5" sizes="16x16 32x32 48x48">
  <link rel="icon" href="/favicon-dark.svg?v=5" type="image/svg+xml" media="(prefers-color-scheme: dark)">
  <link rel="icon" href="/favicon.svg?v=5" type="image/svg+xml" media="(prefers-color-scheme: light)">
  <link rel="mask-icon" href="/safari-pinned-tab.svg?v=5" color="#ffffff" media="(prefers-color-scheme: dark)">
  <link rel="mask-icon" href="/safari-pinned-tab.svg?v=5" color="#111111" media="(prefers-color-scheme: light)">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png?v=3">
  <link rel="stylesheet" href="/styles.css?v=128">
  <link rel="stylesheet" href="/docs/styles.css?v=5">
</head>
<body>
  <div class="site-shell" id="top">
    <header class="masthead">
      <a class="brand" href="/" aria-label="Automic Vault home"><img class="brand-mark" src="/assets/icon@2x.webp?v=3" alt="" width="54" height="54"><span class="brand-type">Automic Vault</span></a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-label="Toggle navigation"><span></span><span></span></button>
      <nav class="nav" aria-label="Main navigation"><a href="/">Home</a><a href="https://pkg.so/">Packages</a><a href="/blog/">Blog</a><a href="/docs/" aria-current="page">Docs</a><a href="/download/">Download</a><a href="https://github.com/automic-vault/automic-vault">GitHub</a></nav>
    </header>
    <main>
      <header class="docs-hero"><div class="docs-hero-inner"><p class="eyebrow">Automic Vault ${version} · macOS</p><h1>${title}</h1><p class="lede">${lede}</p><ul class="docs-provenance" aria-label="Page formats"><li>Source checked</li><li><a href="${markdownRoute}">Markdown</a></li></ul></div></header>
      <div class="docs-layout">
        ${nav(slug, article, title)}
        <article class="docs-content">${article}
<p class="docs-source-link"><a href="${markdownRoute}">Read this page as Markdown</a></p></article>
      </div>
    </main>
    <footer class="docs-footer"><p class="docs-footer-line">Authorize the operation, not just the identity.</p><div class="docs-footer-meta"><div class="docs-footer-links"><a href="#top">Back to top</a><a href="/docs/">Docs</a><a href="${markdownRoute}">Markdown</a><a href="/download/">Download</a><a href="https://github.com/automic-vault/automic-vault">Source</a></div><span>Automic Vault ${version} manual</span></div></footer>
  </div>
  <script src="/app.js?v=26"></script>
</body>
</html>
`;
}

rmSync(path.join(docsDir, "hardeners"), { recursive: true, force: true });

for (const page of pages) {
  const dir = path.join(docsDir, page.slug);
  const markdown = section(page.start, page.end);
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, "index.md"), `${markdown}\n`);
  writeFileSync(path.join(dir, "index.html"), htmlPage({ ...page, markdown }));
}

const featuredCount = 8;
const hardenerList = items => items.map(({ name }) => `- [${titleCase(name)}](./${name}/) — \`av harden ${name}\``).join("\n");
const catalogMarkdown = `# Hardener reference

Hardeners replace supported insecure credential paths with Tool-specific routes that Automic Vault can identify, authorize, and verify. Check the installed state before changing it:

\`\`\`sh
av hardeners --json
av harden TOOL
av doctor TOOL
\`\`\`

## Tool-specific hardeners

${hardenerList(hardeners.slice(0, featuredCount))}

## Environment-wrapper hardeners

These hardeners install a protected launcher for the Tool and migrate supported credentials into Automic Vault.

${hardenerList(hardeners.slice(featuredCount))}
`;

const hardenerIndex = path.join(docsDir, "hardeners");
mkdirSync(hardenerIndex, { recursive: true });
writeFileSync(path.join(hardenerIndex, "index.md"), catalogMarkdown);
writeFileSync(path.join(hardenerIndex, "index.html"), htmlPage({
  slug: "hardeners",
  title: "Hardener reference",
  lede: `The complete ${version} catalog: what each hardener changes, protects, and cannot protect.`,
  description: `Reference for all ${hardeners.length} Automic Vault ${version} hardeners.`,
  markdown: catalogMarkdown,
}));

for (const hardener of hardeners) {
  const slug = `hardeners/${hardener.name}`;
  const dir = path.join(docsDir, slug);
  const documentation = hardener.documentation.trim().replace(/^# [^\n]+\n+/, "");
  const markdown = `# ${titleCase(hardener.name)} hardener

Run \`av harden ${hardener.name}\` to apply this hardener and \`av doctor ${hardener.name}\` to verify it.

${documentation}
`;
  mkdirSync(dir, { recursive: true });
  writeFileSync(path.join(dir, "index.md"), markdown);
  writeFileSync(path.join(dir, "index.html"), htmlPage({
    slug,
    title: `${titleCase(hardener.name)} hardener`,
    lede: `The changes, security properties, caveats, and verification path for the ${hardener.name} hardener.`,
    description: `How Automic Vault ${version} hardens ${titleCase(hardener.name)}.`,
    markdown,
  }));
}

console.log(`Generated ${pages.length} manual pages and ${hardeners.length} hardener pages.`);
