# Automic Vault

## Your secrets manager should know what the secrets *do*.

Automic Vault is the secret manager for developers. It moves supported
credentials out of plaintext files and checks the Tool, Verified Launcher,
Target, command, arguments, working directory, and requested Secret Names before
applying one. Your existing commands still work, and agents need no plugin.

- One credential, different decisions: `gh issue list` can run while
  `gh auth token` still needs Approval.
- Terminal and Codex get separate rules: policy follows each Verified Launcher.
- Use `API_TOKEN` across projects: the working directory selects the Project
  Value.

[Download for macOS](/Automic%20Vault.dmg)

## How authorization works

Most secrets managers check an identity and Secret Name before returning the
stored value.

Automic Vault checks the Verified Launcher, Tool, Target, command, arguments,
working directory, Secret Names, and selected Secret Value sources. Policy
evaluates the complete Authorization Request on the Mac where it will run.

With Read Only access, one GitHub token produces different decisions:

```text
gh issue list     → automically authorized
gh issue create   → Approval required
gh auth token     → Secret Disclosure; Approval required
```

Automic Vault controls Secret Application. After the handoff, the Target
controls the Secret.

## Set separate rules for each Verified Launcher

Terminal, Codex, and an unknown process can invoke the same Tool. Automic Vault
identifies the Verified Launcher and gives each Tool–Launcher pairing its own
Authorization Policy.

- **Approval Required** gives the Launcher no durable policy grant.
- **Read Only** automically authorizes recognized reads.
- **Write Access** automically authorizes recognized reads and writes. Secret
  Disclosure and Elevated Secret Application still require Approval.

## Use the same Secret Name across projects

A Secret Name can have a Global Value and multiple Project Values. Automic
Vault selects the nearest Project Value for the physical working directory.
Every project can request `API_TOKEN`.

```sh
av save API_TOKEN
av save --project-directory=. API_TOKEN
av inject +API_TOKEN -- npm test
```

The Project Directory selects a value; it does not grant authority. This also
lets Automic Vault hold a project-specific dotenvx decryption key while dotenvx
continues to manage the encrypted `.env` file.

## Give an agent task ten minutes of Write Access

Eligible Codex tasks and Claude Code sessions can receive a visible, in-memory
Temporary Access Grant for ten minutes. The grant is scoped to one Verified
Launcher, Tool-specific gate, runtime posture, and task. It never covers direct
secret access, mutation, disclosure, elevated application, or unknown
operations.

Blessed Scripts bind an exact path, contents, Secret Names, and declared Tool
capabilities. Any edit invalidates the Blessing.

## Move every human Approval to iPhone

iPhone Approval is optional and enabled per Mac. Open Automic Vault on an
iPhone using the same iCloud Keychain account, enable iPhone Approval, and allow
notifications. Then open **Settings → iPhone Approval** on the Mac and enable it
there.

The iPhone carries the human decision. The Mac still verifies the complete
Authorization Request, rejects stale responses, persists the Authorization
Record, and enforces the result. Secret Values and Authorization History stay
on the Mac. The Mac exposes no local allow action while iPhone Approval is
enabled.

Routine requests can offer **Approve Once** in an authenticated notification.
Requests with Unknown operation risk, Secret Disclosure, Unconstrained Secret
Application, or a security warning open the full app. Face ID or Touch ID is
optional per iPhone. If no phone or relay is available, the request waits until
its Gate Client cancels.

> iPhone Mirroring and **Show on Mac** can expose Approval controls on the Mac
> when biometrics are off. Disable them, or require Face ID or Touch ID on every
> eligible iPhone.

## Deeper than agent-harness guardrails

Harness guardrails govern one harness. Automic Vault works deeper: its
Hardeners reconfigure or patch the credential-bearing Tool itself, so the same
gate applies when Terminal, Codex, another harness, or an unknown process
invokes it.

- **AWS:** normal invocations receive short-lived STS credentials from a native
  helper. Long-lived keys stay in Automic Vault.
- **Docker:** the gate verifies the vendor-signed Docker process, ancestry,
  arguments, and registry before releasing credentials.
- **Launcher Bundles:** an exact single-file Mach-O CLI snapshot is signed,
  installed root-owned, and revalidated on every request.
- **Homebrew:** policy can allow reads and `brew update` while installs and
  upgrades still require Approval.
- **Detection:** over 100 supported developer configurations are checked for
  Exposures and Hazards.

## The boundary ends at the Target

Automic Vault controls supported Secret Application and sensitive Tool
operations at the Local Execution Boundary. macOS handles general process and
filesystem security. Root or kernel compromise, arbitrary local destruction,
and the Target's behavior after Secret Application remain outside the product
boundary. Code signing proves identity and integrity, not intent. A compromised
Target can leak a received Secret.

Authorization History stays on the Mac and records bounded details for allowed
and denied requests. It is not a tamperproof or audit-complete log.

## From the creator of Homebrew

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](https://www.automicvault.com/docs/) · [Security](https://github.com/automic-vault/automic-vault/security) ·
[Source](https://github.com/automic-vault/automic-vault)
