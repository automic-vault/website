# Automic Vault

## Turn developer credentials into bounded authority.

Automic Vault authorizes verified software to apply credentials to one complete
operation under local policy on your Mac. Your tools keep their normal commands;
no agent plugin is required.

- Authorize the operation: command and context matter, not only the Secret Name.
- Scope the software: each Verified Launcher receives its own policy.
- Keep the workflow: tools and agents continue using their normal commands.

[Download for macOS](/Automic%20Vault.dmg)

## Retrieval is not the policy

Most secrets managers decide whether an identity may retrieve a named secret.
Once the value is returned, their job is done.

Automic Vault decides whether a Verified Launcher may apply the requested
Secrets to a complete operation. Its Authorization Request includes the Tool,
Target, command, arguments, working directory, Secret Names, and selected Secret
Value sources.

With Read Only access, one GitHub token produces different decisions:

```text
gh issue list     → automically authorized
gh issue create   → Approval required
gh auth token     → Secret Disclosure; Approval required
```

Automic Vault controls Secret Application. After the handoff, the Target
controls the Secret.

## Policy follows verified software

Terminal, Codex, and an unknown process can invoke the same Tool. Automic Vault
identifies the Verified Launcher and gives each Tool–Launcher pairing its own
Authorization Policy.

- **Approval Required** gives the Launcher no durable policy grant.
- **Read Only** automically authorizes recognized reads.
- **Write Access** automically authorizes recognized reads and writes. Secret
  Disclosure and Elevated Secret Application still require Approval.

## Project Values without project-shaped names

A Secret Name can have a Global Value and multiple Project Values. Automic
Vault selects the nearest Project Value for the physical working directory, so
projects can all request `API_TOKEN` instead of inventing prefixed names.

```sh
av save API_TOKEN
av save --project-directory=. API_TOKEN
av inject +API_TOKEN -- npm test
```

The Project Directory selects a value; it does not grant authority. This also
lets Automic Vault hold a project-specific dotenvx decryption key while dotenvx
continues to manage the encrypted `.env` file.

## Bounded agent and automation access

Eligible Codex tasks and Claude Code sessions can receive a visible, in-memory
Temporary Access Grant for ten minutes. The grant is scoped to one Verified
Launcher, Tool-specific gate, runtime posture, and task. It never covers direct
secret access, mutation, disclosure, elevated application, or unknown
operations.

Blessed Scripts bind an exact path, contents, Secret Names, and declared Tool
capabilities. Any edit invalidates the Blessing.

## Tool-specific protection

- **AWS:** normal invocations receive short-lived STS credentials from a native
  helper instead of ambient long-lived keys.
- **Docker:** the gate verifies the vendor-signed Docker process, ancestry,
  arguments, and registry before releasing credentials.
- **Launcher Bundles:** an exact single-file Mach-O CLI snapshot is signed,
  installed root-owned, and revalidated on every request.
- **Homebrew:** policy can allow reads and `brew update` while installs and
  upgrades still require Approval.
- **Detection:** over 100 supported developer configurations are checked for
  Exposures and Hazards.

## A precise security boundary

Automic Vault controls supported Secret Application and sensitive Tool
operations at the Local Execution Boundary. It is not a system sandbox, does
not intercept every process, and does not contain root or kernel compromise.
Code signing proves identity and integrity, not intent. A Target can leak a
Secret after receiving it.

Authorization History stays on the Mac and records bounded details for allowed
and denied requests. It is not a tamperproof or audit-complete log.

## From the creator of Homebrew

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](https://www.automicvault.com/docs/) · [Security](https://github.com/automic-vault/automic-vault/security) ·
[Source](https://github.com/automic-vault/automic-vault)
