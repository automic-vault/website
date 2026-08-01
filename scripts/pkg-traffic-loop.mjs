#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const PROVIDERS = new Set(["brew", "cask", "npm", "pip", "cargo"]);
const DEFAULT_OUTPUT_JSON = "cache/pkg-traffic-loop.json";
const DEFAULT_OUTPUT_MD = "cache/pkg-traffic-loop.md";

function usage() {
  console.error(`Usage:
  scripts/pkg-traffic-loop.mjs [--days 90] [--row-limit 25000]
  scripts/pkg-traffic-loop.mjs --input-json /tmp/gsc.json

Options:
  --ops             Path to the ops repo; defaults to ../ops
  --site            GSC site key configured in ops; defaults to automic-vault
  --days            Number of final GSC days to query; defaults to 90
  --row-limit       page+query rows to request; defaults to 25000
  --min-impressions Minimum impressions for opportunity rows; defaults to 10
  --top             Number of opportunities in the markdown report; defaults to 40
  --input-json      Reuse a saved gsc-stats.js JSON response instead of querying GSC
  --output-json     JSON artifact path; defaults to ${DEFAULT_OUTPUT_JSON}
  --output-md       Markdown artifact path; defaults to ${DEFAULT_OUTPUT_MD}
`);
}

function parseArgs(argv) {
  const args = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      args.help = true;
      continue;
    }
    if (!arg.startsWith("--")) throw new Error(`Unexpected argument: ${arg}`);
    const key = arg.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) throw new Error(`Missing value for ${arg}`);
    args[key] = next;
    index += 1;
  }
  return args;
}

function numberArg(args, key, fallback, minimum = 1) {
  const value = Number(args[key] || fallback);
  if (!Number.isInteger(value) || value < minimum) {
    throw new Error(`--${key} must be an integer >= ${minimum}`);
  }
  return value;
}

function readSearchConsoleRows(args) {
  if (args["input-json"]) {
    return JSON.parse(fs.readFileSync(path.resolve(args["input-json"]), "utf8"));
  }
  const opsRoot = path.resolve(args.ops || "../ops");
  const script = path.join(opsRoot, "scripts", "gsc-stats.js");
  const output = execFileSync("node", [
    script,
    "--site",
    args.site || "automic-vault",
    "--days",
    String(numberArg(args, "days", 90)),
    "--dimensions",
    "page+query",
    "--row-limit",
    String(numberArg(args, "row-limit", 25000)),
  ], {
    cwd: opsRoot,
    encoding: "utf8",
    maxBuffer: 64 * 1024 * 1024,
  });
  return JSON.parse(output);
}

function packagePath(url) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== "www.automicvault.com") return null;
    return parsed.pathname;
  } catch {
    return null;
  }
}

function packageRoute(pathname) {
  const match = pathname.match(/^\/(?:(de|fr|ja|zh-hans)\/)?pkg\/([^/]+)\/([^/]+)\/?$/);
  if (!match) return null;
  const [, locale = "en", provider, slug] = match;
  if (!PROVIDERS.has(provider)) return null;
  return { locale, provider, slug, path: pathname };
}

function summarize(rows) {
  const totals = rows.reduce((acc, row) => {
    const impressions = Number(row.impressions || 0);
    const clicks = Number(row.clicks || 0);
    acc.clicks += clicks;
    acc.impressions += impressions;
    acc.weightedPosition += Number(row.position || 0) * impressions;
    return acc;
  }, { clicks: 0, impressions: 0, weightedPosition: 0 });
  return {
    clicks: totals.clicks,
    impressions: totals.impressions,
    ctr: totals.impressions ? totals.clicks / totals.impressions : 0,
    position: totals.impressions ? totals.weightedPosition / totals.impressions : null,
  };
}

function queryIntent(query) {
  const lower = query.toLowerCase();
  if (/https?:\/\/|api\.github\.com|github\.com\/.*\/(?:archive|releases)|\.tar\.gz|\.zip/.test(lower)) {
    return "source-artifact";
  }
  if (/\b(vs|versus)\b|formulae\.brew\.sh|homebrew formula/.test(lower)) {
    return "comparison";
  }
  if (/\b(install|brew|homebrew|formula|npm|pip|cargo|cask|package|packages?)\b|インストール|パッケージ|安装|软件包/.test(lower)) {
    return "install-intent";
  }
  return "long-tail";
}

function opportunityScore(row, intent) {
  const impressions = Number(row.impressions || 0);
  const clicks = Number(row.clicks || 0);
  const ctr = Number(row.ctr || 0);
  const position = Number(row.position || 100);
  const noClickBoost = clicks === 0 ? 1.45 : 1;
  const intentBoost = {
    "install-intent": 1.35,
    comparison: 1.2,
    "source-artifact": 0.8,
    "long-tail": 1,
  }[intent] || 1;
  const reachableBoost = position <= 12 ? 1.25 : position <= 25 ? 0.95 : 0.55;
  const ctrGap = Math.max(0.15, 1 - Math.min(0.5, ctr * 8));
  return impressions * noClickBoost * intentBoost * reachableBoost * ctrGap;
}

function aggregate(data, minImpressions) {
  const rows = data.rows?.["page+query"] || [];
  const packageRows = rows.flatMap((row) => {
    const [url, query] = row.keys || [];
    const pathname = packagePath(url);
    const route = pathname ? packageRoute(pathname) : null;
    if (!route) return [];
    const intent = queryIntent(query || "");
    return [{
      page: url,
      query: query || "",
      ...route,
      intent,
      clicks: Number(row.clicks || 0),
      impressions: Number(row.impressions || 0),
      ctr: Number(row.ctr || 0),
      position: Number(row.position || 0),
      score: opportunityScore(row, intent),
    }];
  });
  const pageMap = new Map();
  for (const row of packageRows) {
    const key = row.page;
    const current = pageMap.get(key) || {
      page: row.page,
      path: row.path,
      locale: row.locale,
      provider: row.provider,
      slug: row.slug,
      rows: [],
    };
    current.rows.push(row);
    pageMap.set(key, current);
  }
  const pages = [...pageMap.values()].map((page) => ({
    ...page,
    summary: summarize(page.rows),
    topQueries: [...page.rows].sort((a, b) => b.score - a.score).slice(0, 8),
  })).sort((a, b) => b.summary.impressions - a.summary.impressions);
  const opportunities = packageRows
    .filter((row) => row.impressions >= minImpressions)
    .sort((a, b) => b.score - a.score);
  return {
    rows: packageRows,
    pages,
    opportunities,
    summary: summarize(packageRows),
  };
}

function pct(value) {
  return `${(Number(value || 0) * 100).toFixed(2)}%`;
}

function pos(value) {
  return value == null ? "-" : Number(value).toFixed(1);
}

function markdownTable(rows) {
  const lines = [
    "| Score | Impr | Clicks | Pos | Intent | Page | Query |",
    "| ---: | ---: | ---: | ---: | --- | --- | --- |",
  ];
  for (const row of rows) {
    lines.push(`| ${row.score.toFixed(0)} | ${row.impressions} | ${row.clicks} | ${pos(row.position)} | ${row.intent} | ${row.path} | ${row.query.replaceAll("|", "\\|")} |`);
  }
  return lines.join("\n");
}

function renderMarkdown(data, aggregateResult, top) {
  const total = data.totals || {};
  const pkg = aggregateResult.summary;
  const topRows = aggregateResult.opportunities.slice(0, top);
  return `# Package Traffic Loop

Generated: ${new Date().toISOString()}
GSC range: ${data.startDate} to ${data.endDate}
Property: ${data.property}
Auth: ${data.authSource || "unknown"}

## Baseline

- Site: ${total.clicks || 0} clicks, ${total.impressions || 0} impressions, ${pct(total.ctr)}, average position ${pos(total.position)}
- Package pages: ${pkg.clicks} clicks, ${pkg.impressions} impressions, ${pct(pkg.ctr)}, average position ${pos(pkg.position)}
- Package rows observed: ${aggregateResult.rows.length}
- Package pages observed: ${aggregateResult.pages.length}

## Loop

1. Observe: run \`scripts/pkg-traffic-loop.mjs\` to refresh package page/query data from Search Console.
2. Prioritize: pick high-score rows with real impressions, weak CTR, and reachable positions.
3. Improve: edit the package origin or metadata in \`../pkgdb\` so the target query is answered in the HTML, markdown alternate, schema, and internal links.
4. Verify: run \`cargo test\` from \`../pkgdb\`, spot-check rendered pages, and make sure the changed terms appear in title/H1/meta/markdown where appropriate.
5. Commit: keep each completed traffic improvement in a focused commit, deploy the package origin, then rerun this report after GSC has fresh final data.

## Top Opportunities

${markdownTable(topRows)}
`;
}

function writeArtifact(file, content) {
  const resolved = path.resolve(file);
  fs.mkdirSync(path.dirname(resolved), { recursive: true });
  fs.writeFileSync(resolved, content);
  return resolved;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return;
  }
  const minImpressions = numberArg(args, "min-impressions", 10);
  const top = numberArg(args, "top", 40);
  const data = readSearchConsoleRows(args);
  const aggregateResult = aggregate(data, minImpressions);
  const output = {
    generatedAt: new Date().toISOString(),
    source: {
      property: data.property,
      authSource: data.authSource,
      startDate: data.startDate,
      endDate: data.endDate,
    },
    siteTotals: data.totals,
    packageTotals: aggregateResult.summary,
    observedPackageRows: aggregateResult.rows.length,
    observedPackagePages: aggregateResult.pages.length,
    topPages: aggregateResult.pages.slice(0, 50),
    opportunities: aggregateResult.opportunities,
  };
  const jsonPath = writeArtifact(args["output-json"] || DEFAULT_OUTPUT_JSON, `${JSON.stringify(output, null, 2)}\n`);
  const markdownPath = writeArtifact(args["output-md"] || DEFAULT_OUTPUT_MD, renderMarkdown(data, aggregateResult, top));
  console.log(`Wrote ${jsonPath}`);
  console.log(`Wrote ${markdownPath}`);
  console.log(`Package pages: ${aggregateResult.summary.clicks} clicks / ${aggregateResult.summary.impressions} impressions / ${pct(aggregateResult.summary.ctr)} CTR`);
  console.log(`Top opportunity: ${aggregateResult.opportunities[0]?.path || "none"}`);
}

try {
  main();
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
