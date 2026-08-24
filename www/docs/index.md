# Automic Vault manual

This is the user and operator manual for Automic Vault 3.16.0 on macOS. It was
checked against the installed CLI, app UI, and 3.16.0 source on August 22, 2026.

Automic Vault does more than store a Secret. It authorizes a complete operation:
the Verified Launcher, Gate Client, Target, command and arguments, working
directory, requested Secret Names, and selected Value sources. If allowed, it
applies the Secret to the Target without displaying the stored Value.

- [Download](https://www.automicvault.com/download/)
- [Source and releases](https://github.com/automic-vault/automic-vault)
- [Canonical Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
- [Architecture and security boundaries](https://github.com/automic-vault/automic-vault/blob/main/docs/architecture.md)
- [Product positioning](https://github.com/automic-vault/automic-vault/blob/main/docs/positioning.md)

## Install and verify

```sh
brew install --cask automic-vault/isotopes/automic-vault
open /Applications/Automic\ Vault.app
av --version
av help
```

You may instead use the [latest release](https://github.com/automic-vault/automic-vault/releases/latest)
or review the [website installer](https://www.automicvault.com/install.sh). The
menu bar app owns Approval UI and Authorization Policy. Open it before an
operation that needs Approval: `av open`.

## Start here

Scan the Mac, save one Value through the hidden terminal prompt, and apply it
only to the Target that needs it:

```sh
av scan --show-all
av save GH_TOKEN
av inject +GH_TOKEN gh auth status
```

`av save` opens `/dev/tty`, turns terminal echo off, and **does not read standard input**.
Do not remove the old credential until the approved command succeeds.
For a Tool with a supplied hardener, prefer its Tool-specific flow:

```sh
av hardeners --json | jq '.hardeners[] | select(.applicable) | {name, hardened}'
av harden gh
av doctor gh
```

## Interface map

The main window is an operator console for exposure, authority, live use, and
evidence. Global search filters the selected destination; Refresh recomputes
live state. The sidebar separates four jobs:

| Job | Destinations | Question answered |
| --- | --- | --- |
| Discover | Detectors, Doctor | Where is supported insecure state, and is the protected route healthy? |
| Establish authority | Hardened Tools, Authorization Gates, Blessed Scripts, Launcher Bundles | Which exact code and operations can ask for authority? |
| Operate | Secrets, Active Proxies | Which named Values exist, and which proxy sessions are live? |
| Audit and configure | Authorization History, Settings | Why was an operation allowed or denied, and which approval routes are enabled? |

Counts are live summaries, not security conclusions. A zero beside Active
Proxies means no proxy session is registered now; it does not prove that no
Target currently holds a Value it received earlier. A clean Doctor view means
the checks implemented by that build passed; it is not a whole-machine attestation.
