# Automic Vault

## Stop AI agents running wild on your Mac

Make agents ask before they install software, deploy to prod or use your secrets.

- Control software installs before an agent changes its toolchain.
- Keep credentials out of files and agent context.
- Approve or deny sensitive actions with a local record.

[Download for macOS](/Automic%20Vault.dmg)

## Your agent inherits your access

An agent can read the same credential files and run the same tools you can. A
helpful shortcut can upload a reusable cloud credential to a remote server.

Automic Vault removes plaintext secrets from files agents can read. If an
agent tries another route, such as `aws config export-credentials`, the command
stops at a native approval gate.

## Secrets stay out of the agent’s context

Automic Vault hardens tools that store secrets in plaintext, keeping
credentials out of an agent’s reach.

When an approved tool needs a secret, you see the command, working directory,
and requested key before anything runs.

### How it works

Automic Vault moves the secret out of the tool’s readable config and into
Keychain-backed storage. When the tool requests it, Automic Vault verifies the
signed app making the request, applies your access policy, and supplies the
secret only for the approved run—without exposing the raw value to the agent’s
context.

## Give yourself access. Make agents ask.

Choose how each signed app can use a secret.

- No access means everything has an approval gate.
- Read-only access is for tools you trust somewhat, like agents. Safe reads can
  proceed; writes require approval.
- Trusted access is for a terminal where you never intend to run `npm i`.†
  Commands that could reveal secrets always keep an approval gate.

† Automic Vault prevents installed packages from stealing protected secrets, as
attempted by supply-chain attacks such as the 2025 Shai-Hulud npm worm. Defense
in depth still matters: run `npm i` only in a dedicated terminal with low-to-no
privileges in both Automic Vault and macOS TCC.

## Every secret use is logged

Approved or denied, automatic or manual: every request leaves a local record
with the decision, launcher, requested key, command, and working directory.

## Know when an agent’s toolchain turns risky

Automic Vault monitors developer tools across ecosystems. It flags new threats
and shows you how to mitigate each finding.

## Control the tool layer beneath every agent

macOS can code sign apps, sandbox them, and keep them out of one another’s
private data. Command-line tools usually run with the authority of whichever
app launched them. That may be Terminal, an AI harness, an editor, or an
automation app.

Automic Vault identifies the tool and its signed launcher, then applies the
access rules you chose for that pairing.

[Read why the terminal needs its own security layer](/blog/bringing-macos-security-to-the-terminal/)

## From the creator of Homebrew

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](https://github.com/automic-vault/automic-vault#readme) · [Security](https://github.com/automic-vault/automic-vault/security) ·
[Source](https://github.com/automic-vault/automic-vault)
