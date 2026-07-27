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
