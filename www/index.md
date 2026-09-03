# Automic Vault

From the creator of Homebrew

## Run agents full access. Don’t lose sleep.

**The missing secrets manager for developers.**

Give agents read-only access to command-line tools like `gh` and `aws`. When
they need more, a human must approve it on your Mac or a connected iPhone.

[Download for macOS](/Automic%20Vault.dmg)

**Deeper than guardrails.** Zeroconf above the boundary: supported tools work
with any agent, any harness, *any app*. Hardeners move those tools into a
hardened state at the packaging layer, with their credentials stored in Automic
Vault.

## Full access shouldn’t mean ambient credentials

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

## Ten minutes. One task. One Tool.

Eligible Codex tasks and Claude Code sessions can receive a visible, in-memory
Temporary Access Grant for ten minutes. The grant is scoped to one Verified
Launcher, Tool-specific gate, runtime posture, and task. It never covers direct
secret access, mutation, disclosure, elevated application, or unknown
operations.

Blessed Scripts bind an exact path, contents, Secret Names, and declared Tool
capabilities. Any edit invalidates the Blessing.

## Credentials stay on your Mac until an authorized operation needs them

Automic Vault moves supported credentials out of readable Tool configuration.
The Mac verifies the Launcher, Tool, Target, command, arguments, working
directory, requested Secret Names, and selected Value sources. Your existing
commands keep working, and agents need no Automic Vault plugin.

## Set separate rules for Terminal and Codex

Terminal, Codex, and an unknown process can invoke the same Tool. Automic Vault
identifies the Verified Launcher and gives each Tool–Launcher pairing its own
Authorization Policy.

- **Approval Required** gives the Launcher no durable policy grant.
- **Read Only** automically authorizes recognized reads.
- **Write Access** automically authorizes recognized reads and writes. Secret
  Disclosure and Elevated Secret Application still require Approval.

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

## One Secret Name. The right Project Value.

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

## When full access is too broad, expose one reviewed path

A reentrant Blessed Script runs deterministic work until it needs agent input,
then exits with a prompt that names the required output, fixed subcommands, and
the command that resumes the workflow.

Automic Vault authorizes every invocation separately. The agent can inspect
context and return a result through those reviewed entry points without general
access to the underlying Tools, MCP servers, or Secret Values. The script
validates the output before it acts.

[Design a reentrant Blessed Script](/docs/reentrant-scripts/).

## Controls live below the agent harness

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

## Every decision leaves local evidence

Allowed or denied, policy or Approval: requests leave bounded Authorization
History on your Mac with the decision, Launcher, Secret Names, command, and
working directory. Detectors report supported Exposures and Hazards with
concrete mitigation steps.

## Automic Vault does not make full access harmless

Automic Vault controls supported Secret Application and sensitive Tool
operations at the Local Execution Boundary. macOS handles general process and
filesystem security. Root or kernel compromise, arbitrary local destruction,
and the Target's behavior after Secret Application remain outside the product
boundary. Code signing proves identity and integrity, not intent. A compromised
Target can leak a received Secret.

Authorization History stays on the Mac and records bounded details for allowed
and denied requests. It is not a tamperproof or audit-complete log.

## Free. Open source. Built for macOS.

Automic Vault is free Apache-2.0 open-source software for macOS.

[Documentation](https://www.automicvault.com/docs/) · [Security](https://github.com/automic-vault/automic-vault/security) ·
[Source](https://github.com/automic-vault/automic-vault)
