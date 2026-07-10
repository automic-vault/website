# Automic Vault

## Secure the tools you brew install

- Encrypts plaintext secrets for all CLI tools.
- Enforces human approval for all secret usage.

[Download for macOS](/Automic%20Vault.dmg)

**No more plaintext secrets**

## “Helpful” Agents Take Dangerous Shortcuts

When a remote shell cannot use AWS, an agent may read
`~/.aws/credentials` and upload the keys from your Mac. A reusable cloud
credential has now crossed the trust boundary.

**Protecting secrets is not enough**

### The Tool Should Have to Ask

Automic Vault keeps the credential out of the agent's context. The request
stops at a native approval gate where you can inspect the command, working
directory, and requested key, then approve it once or deny it.

## Access Is Granted per Tool

Every secret use is restricted by default. You can auto-approve read-only
queries for one named tool, or explicitly grant full access to that tool
without granting access to any other executable.

## Every Secret Use Is Logged

Approved or denied, automatic or manual: every request leaves a local record
with the decision, launcher, requested key, command, and working directory.

## From the Creator of Homebrew

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](/docs/) · [Security model](/security/) ·
[Source](https://github.com/automic-vault/automic-vault)
