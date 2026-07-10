# Automic Vault

## Secure the tools you brew install

- Encrypts plaintext secrets for all CLI tools.
- Enforces human approval for all secret usage.

[Download for macOS](/Automic%20Vault.dmg)

**No more plaintext secrets**

## “Helpful” Agents Take Dangerous Shortcuts

**Encrypting secrets is not enough**

### The Tool Should Have to Ask

Automic Vault keeps the credential out of the agent's context. The request
stops at a native approval gate where you can inspect the command, working
directory, and requested key, then approve it once or deny it.

## Granular Access per Tool Consumer

Every secret use is restricted by default. Relax the gate only for the
code-signed executable you name. Read-only `gh` approval is opt-in on a per
secret handling tool basis. Full `gh` access can be always approved for one
named calling app—Terminal.app in this example—without opening it to any other
consumer.

## Every Secret Use Is Logged

Approved or denied, automatic or manual: every request leaves a local record
with the decision, launcher, requested key, command, and working directory.

## Monitor Threats to your developer environment

Automic Vault monitors developer tools across all ecosystems. New threats are
flagged instantly, with clear steps to mitigate each finding.

## From the Creator of Homebrew

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](/docs/) · [Security model](/security/) ·
[Source](https://github.com/automic-vault/automic-vault)
