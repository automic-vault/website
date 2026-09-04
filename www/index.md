# Automic Vault

You got

## Full-access agents

You got

## Supply-chain attacks

You got

## Apps Reddit promised were safe

But you also got

## Automic Vault

So

## You’re good

[Download for macOS](/Automic%20Vault.dmg)

Any agent. Any CLI. Any app. No agent setup required.

**The missing secrets manager for developers.** Give agents Read Only access to
command-line tools like `gh` and `aws`. When they need more, you approve it on
your Mac or iPhone.

## Read? Fine. Write? Ask.

Most secrets managers ask whether you can fetch a value. Automic Vault asks
whether this exact operation should get it. Same credential. Very different
question.

With Read Only access, one GitHub token produces different decisions:

```text
gh issue list     → automically authorized
gh issue create   → Approval required
gh auth token     → Secret Disclosure; Approval required
```

Automic Vault controls Secret Application. After the handoff, the Target
controls the Secret.

## Your credentials stay home.

Automic Vault moves supported credentials out of files your Tools—and your
agents—can read. The Mac checks who is asking, what will run, where it will run,
and which Secret Names it needs. Your commands keep working. Agents need no
Automic Vault plugin.

## Terminal is you. Codex isn’t.

Same Tool. Different Launcher. Different rules. Give Terminal Write Access,
keep Codex Read Only, and make Unknown processes ask every time.

- **Approval Required:** no standing permission. Every operation asks.
- **Read Only:** recognized reads run. Writes ask.
- **Write Access:** recognized reads and writes run. Secret Disclosure and
  Elevated Secret Application still ask.

## Put Approval in your pocket.

Turn on iPhone Approval and move every human Approval to your iPhone. The Mac still verifies the request,
records the decision, and enforces it. The Mac has no local allow action.
Secret Values and Authorization History stay on the Mac.

Routine request? Approve from the notification. Disclosure, Unconstrained
Secret Application, Unknown risk, or a warning? Open the app. No phone? Nothing
runs.

> iPhone Mirroring and **Show on Mac** can expose Approval controls on the Mac
> when biometrics are off. Disable them, or require Face ID or Touch ID on every
> eligible iPhone.

## Same name. Right secret.

Every project can ask for `API_TOKEN`. The physical working directory selects
the nearest Project Value, then falls back to the Global Value.

```sh
av save API_TOKEN
av save --project-directory=. API_TOKEN
av inject +API_TOKEN -- npm test
```

The path picks a Value. It never grants authority. The operation still crosses
the same Authorization Gate.

## Give agents a door. Not the keys.

A reentrant Blessed Script exposes fixed, reviewed entry points. The agent gets
the context it needs, returns a result, and carries on.

Every invocation is authorized separately. The agent never gets general access
to the underlying Tools, MCP servers, or Secret Values.

[Build the door](/docs/reentrant-scripts/).

## Not another harness guardrail.

Automic Vault is Zeroconf Above the Boundary: any agent, any harness, any app.
Hardeners reconfigure or patch the credential-bearing Tool itself, with its
credentials stored in Automic Vault.

AWS, Docker, Homebrew, and project scripts each hide credentials differently.
So each Hardener goes to the packaging layer and fixes that Tool there.

- **AWS:** short-lived credentials, every time. Long-lived default keys leave
  `~/.aws/credentials`.
- **Docker:** right process, right registry. The gate checks the live
  vendor-signed process, ancestry, arguments, and registry.
- **Homebrew:** reading is not installing. Inspection and `brew update` can run
  while installs still ask.
- **Launcher Bundles:** an identity for one-file CLIs. Exact enrolled Mach-O
  snapshots are installed root-owned and revalidated.
- **Detection:** find the loose keys first. Detectors report supported Exposures
  and Hazards, plus what to do about them.

## Receipts. Kept locally.

Allowed, denied, policy, or human Approval: it lands in bounded Authorization
History on your Mac with the Launcher, Secret Names, command, and working
directory.

Enough to understand what happened. Not a tamperproof or audit-complete
forensic ledger. Detectors also find supported plaintext and ambient
credentials before an agent does.

## We’re not magic.

Automic Vault protects supported credentials and sensitive Tool operations at
the Local Execution Boundary. It does not stop root, kernel compromise, or an
agent deleting your files with some other command.

Once a Target gets a Secret, the Target controls it. Code signing proves what
ran—not whether it’s nice. Project paths select Values, and agent task
identifiers narrow grants. Neither establishes identity.

## Free. Open source. macOS.

The Mac app costs nothing and ships under Apache-2.0. The optional paid iPhone
app moves human Approval off the machine running the agent.

[Documentation](https://www.automicvault.com/docs/) · [Security](https://github.com/automic-vault/automic-vault/security) ·
[Source](https://github.com/automic-vault/automic-vault)
