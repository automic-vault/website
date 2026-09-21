# Automic Vault

> CLI security is broken. The packaging layer is where we fix it.

Max Howell

I created Homebrew. Now I’m fixing what happens when agents use it.

Automic Vault hardens supported CLI tools on macOS, moves exposed credentials into the Keychain, and gates their use while you keep your usual commands.

Free and open source. Your existing commands keep working. No agent plugin required.

[Download for macOS](https://www.automicvault.com/Automic%20Vault.dmg) · [See it in action](https://www.automicvault.com/#demo)

## Fix the tools where you install them.

You install a CLI to do a job. Its credentials often end up in files or helpers that any code running as you can read. Agents inherit that mess.

For GitHub, av harden gh installs our signed, patched CLI and migrates its credentials into Automic Vault custody. You still run gh. Authenticated operations now reach its Authorization Gate.

[See how we harden your tools](https://www.automicvault.com/docs/hardeners/)

### Your secrets manager should know what the secrets do.

Reading an issue, publishing a release, and revealing a token need different authority. AV checks the complete operation before applying the credential.

One token. Three decisions.

GitHub · Verified Launcher with Read Only policy

| Command | Decision | Reason |
| --- | --- | --- |
| `gh issue list` | Authorized | Read Only |
| `gh issue create` | Approval required | Remote Write |
| `gh auth token` | Approval required | Secret Disclosure |

Revealing a credential needs its own decision, even when nothing changes remotely.

### Homebrew: Updates can run. Installs can ask.

Homebrew hardening protects /opt/homebrew from changes by other code running as you. At Read & Update, recognized inspection commands and brew update can run; installs and upgrades need Approval. This targets Apple Silicon Homebrew; services and shell completions are incompatible while hardened.

[How Homebrew hardening works](https://www.automicvault.com/docs/hardeners/brew/)

### AWS: Short-lived credentials per invocation.

Normal AWS commands receive short-lived session credentials. Long-lived keys leave the shared credentials file. AV obtains session credentials separately for each AWS process.

[How AWS hardening works](https://www.automicvault.com/docs/hardeners/aws/)

### Docker: The process and registry matter.

Before releasing a registry credential, AV verifies the live Docker Desktop process, its signature, runtime protections, ancestry, arguments, and requested registry.

[How Docker hardening works](https://www.automicvault.com/docs/hardeners/docker/)

## Start with the credentials sitting on your Mac.

Secure your command line

Scan without installing:

```sh
curl -fsSL https://www.automicvault.com/scanner.sh | bash
```

Downloads a small standalone scanner built from the latest release sources, verifies its signature, and runs it in a read-only sandbox with no network access.

Find credentials that tools, dependencies, and agents can read from your files or credential helpers. Each Finding explains the exposure and what you can do about it.

Choose a supported Hardener for a Finding, then use av doctor to verify the installed protection.

A clean Scan covers the checks AV supports. It does not certify your whole machine as secure.

[Find your tools](https://www.automicvault.com/docs/hardeners/)

## Let your agent read GitHub. Make it ask to write.

Decide what your tools and agents can do

Choose Read Only for your agent’s GitHub gate and a different policy for your terminal. AV verifies each Launcher’s live software identity before applying its policy.

AV does not sandbox your agent or prevent arbitrary local file changes.

Write Access still leaves disclosure and elevated credential use behind Approval. Unknown operations always need a human decision.

For an eligible agent task, grant ten active minutes of Write Access at one gate. You can extend, suspend, or end that grant from its visible controls.

Code signing establishes software identity and integrity, not intent. Task identifiers narrow temporary grants; they do not establish identity.

[Choose how much authority to give](https://www.automicvault.com/docs/authority/)

## Review the release script once.

Give agents the capabilities they need

Let an agent prepare release notes while a reviewed script publishes to GitHub and updates your CDN. A Blessed Script binds exact contents and declared capabilities to your review.

A reentrant script pauses for agent input, exposes fixed entry points for context, then continues the deterministic work. AV authorizes each invocation. Editing the script invalidates its Blessing.

Validate agent output before using it. Keep Secret Values within the script’s execution; a Blessing does not make its code trustworthy.

[Build a reviewed agent workflow](https://www.automicvault.com/docs/reentrant-scripts/)

## See what you’re being asked to allow.

See the software, command, arguments, working directory, and Secret Names before you allow an operation.

## Keep project secrets out of plaintext files

Use the same Secret Name across projects with a different Project Value for each. AV selects the nearest matching physical directory, or the Global Value when no Project Value matches.

For compatible HTTP clients, the Secret Proxy gives your application a temporary reference and applies the real credential only to approved destinations.

Directories select Values; they grant no authority. Policy covers all Values of a Secret Name. Proxy references are bearer values that can exercise already-granted session access.

[Understand Project Values](https://www.automicvault.com/docs/authority/) · [Explore credential proxying](https://www.automicvault.com/docs/workflows/)

## Approve operations across your Macs

Review requests from your enrolled Macs on eligible iPhones using the same iCloud Keychain account. See the operation you’re being asked to allow, wherever it originated.

Each Mac keeps its Secrets, policy, and Authorization History, and enforces the decision locally. You can also enable Touch ID Approval on a Mac for biometric-only allow actions.

iPhone Approval removes pointer- and keyboard-driven allow actions on the Mac. Disable iPhone Mirroring and Show on Mac, or require Face ID or Touch ID on every eligible iPhone. An unavailable relay never enables a fallback.

[Set up iPhone and Touch ID Approval](https://www.automicvault.com/docs/authority/) · [Join the public iPhone beta on TestFlight](https://testflight.apple.com/join/cfnDU5kM)

## Where this stops

AV protects supported credentials and gates supported Tool operations against code running as you. Wrappers do not intercept every command, and installing a package does not make it safe. Root or kernel compromise, arbitrary local destruction, and a Target’s behavior after receiving a Secret remain outside this boundary.

Authorization History keeps local records of allowed and denied requests. AV persists and verifies the record of an allowed Secret Use before releasing the Secret. History is bounded; it is not a tamper-resistant or complete forensic log.

[Read the security model](https://www.automicvault.com/docs/security/) · [Canonical definitions](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)

## Free. Open source. macOS.

The Mac app costs nothing and ships under Apache-2.0. Optional iPhone Approval requires an active subscription to send allow responses. Denying a request does not require a subscription.
