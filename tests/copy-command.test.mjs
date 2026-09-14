import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";
import { test } from "node:test";

test("copy preserves the command and reports success or failure without getting stuck", async () => {
  const source = readFileSync(new URL("../www/app.js", import.meta.url), "utf8");
  const command = "curl -fsSL https://www.automicvault.com/scanner.sh | bash";
  for (const fail of [false, true]) {
    let click;
    let copied;
    const status = { textContent: "Copy" };
    const button = {
      disabled: true,
      dataset: { copied: "Copied", failed: "Copy failed" },
      querySelector: () => status,
      addEventListener: (_event, handler) => { click = handler; },
    };
    runInNewContext(source, {
      document: { querySelector: (selector) => ({
        ".brew-copy-command": button,
        ".brew-scanner-command code": { textContent: command },
      })[selector] ?? null },
      navigator: { clipboard: { writeText: async (text) => {
        assert.equal(button.disabled, true);
        if (fail) throw new Error("Clipboard denied");
        copied = text;
      } } },
    });
    assert.equal(button.disabled, false);
    await click();
    assert.equal(button.disabled, false);
    assert.equal(button.dataset.state, fail ? "failed" : "copied");
    assert.equal(status.textContent, fail ? "Copy failed" : "Copied");
    assert.equal(copied, fail ? undefined : command);
  }
});
