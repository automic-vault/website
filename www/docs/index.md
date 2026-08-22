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

## The security model

An **Authorization Request** is the complete immutable operation presented to
policy. A decision is about that complete request, not merely a Secret Name or
process identity. It can include the Verified Launcher and execution chain; Gate
Client and Authorization Gate; resolved Target, command, and arguments; physical
working directory; exact Secret Names and selected Values; runtime posture; and
existing-environment conflicts.

A **Secret Gate** controls Secret Application or, at stronger levels, Secret
Disclosure and elevated operations. An **Execution Gate** controls a privileged
operation without necessarily releasing an ordinary Secret; GPG Signing is one.
The Mac is always the **Local Execution Boundary**. Approval may come from the
Mac or an eligible iPhone, but the Mac revalidates the request before execution.

Secret Application puts a Value into an authorized operation without showing
it. Secret Disclosure reveals the raw Value. Automic Vault cannot promise that
a Target will not reveal a Secret after receiving it: the Target controls the
Value from that point onward.

Automic Vault is not a sandbox, a general process-containment system, a defense
against a compromised kernel or root account, or proof that signed code has good
intent. Code signing establishes identity and integrity—not trust or intent.

## App tour

The main window has global search and refresh controls plus ten sections.

### Detectors

Detectors find supported credential Exposures, configuration Hazards, and other
security-relevant state. Each Finding includes severity, affected paths,
explanation, remediation, and source-linked documentation. A clean scan is not
proof that no credential exists outside the covered detectors.

![Detectors list and source-linked Finding details](/docs/assets/detectors.png)

### Hardened Tools

Hardened Tools shows each installed hardener, protected launcher or native
credential route, current Target, embedded reference, and recent access.

![Hardened Tools list with selected tool status](/docs/assets/hardened-tools.png)

### Authorization Gates

A Gate shows its request type, Secret patterns, Targets, default rule for all
other apps, per-launcher overrides, and Hardened Runtime requirement.

![Authorization Gate policy and verified app overrides](/docs/assets/authorization-gates.png)

### Blessed Scripts

A Blessing binds a reviewed path, SHA-256 digest, Script Declaration, Secret
Names, Capabilities, interpreter, and optional Launcher Endorsements. Changing
or moving the script invalidates it. When a baseline exists, the app shows the
diff before replacement.

![Blessed Script checksum, Secret Names, capabilities, and launchers](/docs/assets/blessed-scripts.png)

### Launcher Bundles

A Launcher Bundle packages one regular single-file Mach-O CLI into a signed,
Hardened Runtime app. Automic Vault snapshots the payload, shows hashes and
entitlements, installs root-owned app and command link, and enrolls that exact
generation. JIT, unsigned-executable-memory, and library-validation exceptions
are explicit review choices.

![Create Launcher Bundle sheet](/docs/assets/launcher-bundles.png)

Deleting one revokes enrollment and launcher rules before moving it to Trash. A
Launcher Bundle establishes identity and integrity; it does not make code safe.

### Secrets

A Secret Name may have one Global Value and multiple Project Values. The app
never shows stored Values after saving. It can replace or delete Values, change
availability, rename the Secret, and remove the final Value and Direct Rules.

![Add Secret sheet with empty secure Value field](/docs/assets/secrets.png)

### Active Proxies

Active Proxies shows Target, PID, Secret Names, start time, request count,
permitted origins, and individual requests. Terminating a session ends its
memory-only rules, random Secret References, and Proxy Credential.

![Harmless active proxy session with sample Secret Name](/docs/assets/active-proxy.png)

### Authorization History

History records recent allowed and denied operations with decision, source,
command, reason, Verified Launcher, Secret Names and sources, Gate Client,
Target, runtime, and working directory.

![Authorization History detail for a sample proxy approval](/docs/assets/authorization-history.png)

History is local and bounded—not a tamper-proof, append-only, complete forensic
log. An allowed Secret Use is persisted and verified before release, but an
administrator can still alter local state.

### Doctor

Doctor verifies protected ownership, launchers, dependencies, Target selection,
file content, permissions, and PATH precedence, with remediation beside failures.

![Doctor showing healthy installation state](/docs/assets/doctor.png)

### Settings

Settings controls Approval routes, feedback, retained launcher provenance, GPG
Signing, `av list` policy, and app information.

## Approval and settings

Review the command, Secret Names, working directory, full Target path, Verified
Launcher, execution-chain roles, security posture, and warnings before allowing.

![Mac Approval request showing a complete sample operation](/docs/assets/approval-request.png)

### Touch ID Approval

Touch ID Approval is Mac-local and fresh-biometric-only. It allows neither login
password nor Apple Watch fallback and is separate from iPhone Approval.

![Touch ID Approval disabled](/docs/assets/touch-id-approval.png)

### iPhone Approval

An eligible iPhone on the same iCloud Keychain account can carry human Approval
while the Mac remains the Local Execution Boundary. When enabled with an
eligible phone, the Mac exposes no pointer or keyboard allow action. The phone
requires Face ID or Touch ID; Approval is unavailable through iPhone Mirroring.

![iPhone Approval disabled](/docs/assets/iphone-approval.png)

Recovery uses system authentication, rotates the account key, and invalidates
all registered phones and Macs. Treat recovery as a security event.

### Automic Authorization feedback

Allowed operations can show a notification, flash the menu bar, or show nothing.
History is still recorded. This does not suppress prompts or denial notices.

![Automic Authorization feedback choices](/docs/assets/automic-authorization.png)

### Detached Processes

Retained Launcher Provenance lets eligible detached descendants retain a
verified launcher chain after the original exits. It is off by default. Enabling
changes authority and needs Approval; disabling is immediate. It retains neither
a prior decision nor blanket process-tree access.

![Detached Processes disabled](/docs/assets/detached-processes.png)

### GPG Signing

GPG Signing stores an armored OpenPGP private key in Secret Custody and routes
Git through `av-gpg` and `av gpg-sign`. Git never receives the private key.

```sh
git config --global gpg.program av-gpg
git config --global gpg.format openpgp
git config --global commit.gpgSign true
```

Settings can import a key or generate an alternate EdDSA key. The private key is
never displayed; the public key can be copied. Alternate access can be limited
to exact Verified Launchers. The Execution Gate offers **Approval Required** and
**Allow Signing**. Signing binds Approval to the payload SHA-256 and returns only
a detached signature.

### Secret Name Access

Exact Verified Apps may run `av list` without Approval; all others require it.
This permits listing names only—not reading, changing, applying, or disclosing
their Values.

### About and menu bar

About shows the app version and GUI PATH captured before shell startup. The menu
bar provides Open Automic Vault, Check for Updates, and Quit, and surfaces live
Secret Uses and Temporary Access Grants without displaying Values.

## Secrets, Values, and selection

```sh
av save GH_TOKEN
av save --project-directory=. GH_TOKEN
av save --project-directory=/absolute/project AWS_PROFILE
```

A Secret Name is a letter or underscore followed by letters, digits, or
underscores. `save` canonicalizes an existing Project Directory, rejects the
filesystem root, reads one hidden non-empty Value from `/dev/tty`, trims its line
ending, and restores echo even on failure.

For each name, Automic Vault selects the nearest Project Value at or above the
physical canonical working directory on the same filesystem; otherwise it uses
the Global Value. Project Directory is a selector—not project identity or an
authorization boundary. A selected Value read failure never falls back.

Availability is independent of authorization. **When Unlocked** requires an
unlocked Keychain. **Available While Locked** permits use after the first unlock
following boot. Neither setting grants an operation.

## Access Levels

| Access Level | Meaning |
| --- | --- |
| Approval Required | Every matching request needs human Approval. |
| Read Only | Apply Secrets to read-only operations allowed by the Gate. |
| Read & Update | Homebrew-only update authority. |
| Local Write | Permit local writes without broader remote authority. |
| Write Access | Permit the Gate's write operations. |
| Full Access | Strongest supported operations, potentially Disclosure or elevated application. |
| Direct Access | Apply exact names through the Direct Gate for one Verified Launcher. |

New Secret Gates default to Read Only; GPG Signing to Approval Required;
Homebrew to Read & Update; Direct access to Approval Required.

The Direct Secret Gate is broad: exact names and one Verified Launcher, but no
Target or argument restriction. It permits neither listing nor changing Values.
Prefer a Tool-specific Gate.

A **Temporary Access Grant** provides ten minutes of memory-only Write Access,
bound to the exact Tool-specific Gate, Verified Launcher, accepted runtime, and
Agent Task Context. It excludes Direct Access, mutation, Disclosure, elevated
and unknown operations. Task context is a forgeable narrowing label, not
identity. End a grant anytime; grants vanish on expiry or app restart.

## Command reference

```text
av scan [--show-all|--json]
av doctor [<tool>] [--json]
av detectors --json
av hardeners --json
av bless [--endorse-launcher] <path>
av inject +KEY... [--] <command>
av inject -- <command>
av proxy +KEY... [--] <command>
av list
av save [--project-directory=DIR] KEY
av harden <tool> [-y|--yes]
av unharden brew [-y|--yes]
av gpg-sign [GPG options]
av open [--secret-gate <id>]
av help
av --version
```

Old v1 commands `install`, `contain`, `dotenv`, `credential-helper`, `gate`, and
`trace` are not part of 3.16.0.

### `av scan`

```sh
av scan
av scan --show-all
av scan --json
av scan --json --detector aws-cli-credentials-file
```

The human report omits medium and low severity unless `--show-all` is set. JSON
contains `findings` and `gui_path`. A completed scan exits `0` even with Findings;
consume the report, not status, as the audit result. Repeat `--detector NAME`
with JSON to limit automation.

### `av doctor`

```sh
av doctor
av doctor gh
av doctor gh --json
av doctor codex
```

Without a selector it checks applicable hardeners. A selector can be a hardener,
one of its commands, or a supported signed agent CLI. JSON contains `results`.
Exit `0` means healthy, `1` means attention needed, and `2` means invalid or
unknown selection.

### Machine-readable catalogs

```sh
av detectors --json |
  jq '.detectors[] | {name, docs_url, documentation}'

av hardeners --json |
  jq '.hardeners[] | {
    name, applicable, hardened, commands, stub_path, target_path, secret_gate
  }'
```

These are authoritative for the installed build. 3.16.0 ships 157 detectors and
50 hardeners. The `documentation` field contains the source-checked behavior and
security model. Generated environment wrappers warn that the Target can read
injected credentials; dedicated/native routes may provide narrower boundaries.

<details>
<summary>3.16.0 hardener names</summary>

`akamai`, `algolia`, `argocd`, `ast-cli`, `aws`, `brew`, `buf`, `censys`,
`checkov`, `circleci`, `civo`, `cloudsmith-cli`, `codex`, `composer`, `docker`,
`doctl`, `flyctl`, `gh`, `glab`, `gotify`, `gptcommit`, `grafanactl`, `hcloud`,
`heroku`, `huggingface-cli`, `jfrog-cli`, `k6`, `luarocks`, `minio-mc`,
`netlify-cli`, `node`, `pnpm`, `pulumi`, `qwen-code`, `runpodctl`, `s3cmd`,
`sentry-cli`, `snowflake-cli`, `snyk`, `stripe`, `sudo`, `supabase`,
`transifex-cli`, `travis`, `twine`, `vagrant`, `vault`, `virustotal-cli`,
`vultr`, `wsk`.

</details>

### `av save` and `av list`

```text
av save [--project-directory DIR] KEY
av save [--project-directory=DIR] KEY
av list
av ls
```

`list` shows names, never Values, and accepts no arguments. A pipeline does not
provide a Value to `save`:

```sh
# Wrong: save reads /dev/tty, not stdin.
printf '%s\n' "$GH_TOKEN" | av save GH_TOKEN
```

### `av inject`

```text
av inject [--replace-existing-env] [--allow-missing-keys] \
  +KEY [+KEY...] [--] COMMAND [args...]
av inject -- COMMAND [args...]
```

Bare commands resolve through PATH; a Target containing `/` must be absolute.
Existing environment values win with a warning unless
`--replace-existing-env` is used. Missing requested Secrets fail unless
`--allow-missing-keys` leaves them unset. Duplicate/invalid names and root are
rejected. On success, `exec` replaces `av` with the Target. Legacy
`--allow-existing-env`, `--force`, `--import`, and `--migrate` are rejected.

#### Shebang and Blessing workflow

```sh
#!/usr/local/bin/av inject +GH_TOKEN /bin/sh
# --- automic-vault
# capabilities:
#   gh: write
# ---
set -eu
gh release create "$1"
```

A blessable script is a regular UTF-8 file up to 1 MiB with absolute `av` and
interpreter paths. The optional manifest immediately follows the shebang.
Capabilities are ceilings, not grants. Execution uses a verified `/dev/fd/N`
snapshot; `AV_SCRIPT_PATH` and `AV_SCRIPT_DIR` identify its canonical source.

### `av proxy`

```text
av proxy [--replace-existing-env] +KEY [+KEY...] [--] COMMAND [args...]
```

Every session needs Approval. The Target receives random session Secret
References and a Proxy Credential, not raw Values. Automic Vault replaces common
uppercase/lowercase proxy variables, empties `NO_PROXY`, and sets standard CA
variables. Conflicts fail unless `--replace-existing-env` is used.

Destination rules are memory-only and scoped per session and origin. A Target
can bypass configured proxies; bearer credentials remain bearer credentials at
the destination. Proxying is narrower delivery, not containment. Root is denied.

### `av bless`

```sh
av bless ./release.sh
av bless --endorse-launcher ./release.sh
```

Approval binds the complete reviewed script. An endorsement allows only that
Verified Launcher to use automic authorization; without it every run needs
Approval. `--endorse-caller` is a compatibility alias. The UI inspects, narrows,
replaces, and revokes Blessings.

### `av harden` and `av unharden brew`

```sh
av harden gh
av harden aws --yes
av unharden brew --yes
```

A hardener may move a credential, install or replace a launcher, protect
ownership, install a signed Tool, or enable a native route. Read its embedded
documentation; some operations require `sudo`, but do not run all hardeners as
root. `-y`/`--yes` skips supported confirmations. Aliases include `homebrew`,
`gh-cli`, `stripe-cli`, `supabase-cli`, and `fly`. `unharden` is Homebrew-only.

### `av gpg-sign` and `av open`

`av gpg-sign` is Git plumbing, not an interactive interface. It accepts forwarded
GnuPG options, reads at most 16 MiB, binds to payload SHA-256, and returns a
detached signature and GnuPG status. Configure it in Settings.

```sh
av open
av open --secret-gate gh
```

Gate IDs use only ASCII letters, digits, hyphens, underscores, and periods.

### Global behavior and exit status

```sh
av help
av --version
av inject --help
av proxy --help
```

Not every subcommand has dedicated `--help`. Color is disabled by `NO_COLOR` or
`TERM=dumb`. Exit `0` is completion/approved execution; `1` operational failure,
denial, or unhealthy Doctor; `2` top-level usage or invalid Doctor selection.

## Common workflows

### GitHub CLI

```sh
av scan --json --detector gh-cli-hosts-token
av harden gh
av doctor gh
gh auth status
```

Inspect the `gh` Secret Gate before automic authorization. Direct `inject` works,
but the Tool-specific Gate can narrow policy by operation.

### AWS CLI

```sh
av harden aws
av doctor aws
aws sts get-caller-identity
```

The AWS route installs and verifies AWS's signed CLI under `/opt/av/aws`, moves
the default long-lived pair into Custody, and issues short-lived STS credentials.

### Docker

```sh
av harden docker
av doctor docker
docker pull registry.example.test/team/image:latest
```

Docker hardening retains the vendor-signed CLI and gates registry credentials on
live identity, ancestry, arguments, and requested registry.

### GPG-signed commits

Configure GPG Signing and `av-gpg`, then verify:

```sh
git commit --allow-empty -m 'verify signing'
git log --show-signature -1
```

## Troubleshooting

- **No response:** run `av open`; inspect History for exact denial details.
- **Wrong executable:** compare `command -v TOOL` with `av doctor TOOL`; authorize
  the native executable, not a shell or mutable shim.
- **Wrong Project Value:** confirm canonical working and Project Directories are
  on one filesystem and the latter is an ancestor.
- **Environment value wins:** remove the export or deliberately use
  `--replace-existing-env` after reviewing precedence.
- **Blessing stopped matching:** review the diff and re-bless only if correct;
  edits and moves invalidate identity.
- **Launcher Bundle denied after update:** create and review a new generation;
  digest, signature, enrollment, and runtime mismatches fail closed.
- **Security issue:** follow [security.txt](https://www.automicvault.com/.well-known/security.txt)
  and never post Values, private keys, or live credentials.

## Source of truth

This manual was checked against the CLI parser, implementations, app UI,
catalogs, tests, and canonical security documents for 3.16.0. For an installed
build prefer `av --version`, `av help`, `av detectors --json`, and
`av hardeners --json`.

- [CLI source](https://github.com/automic-vault/automic-vault/blob/3.16.0/src/cli/mod.rs)
- [App and CLI source](https://github.com/automic-vault/automic-vault/tree/3.16.0/src)
- [Detectors](https://github.com/automic-vault/automic-vault/tree/3.16.0/src/detectors)
- [Hardeners](https://github.com/automic-vault/automic-vault/tree/3.16.0/src/isotopes)
- [Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
- [Architecture](https://github.com/automic-vault/automic-vault/blob/main/docs/architecture.md)

Report discrepancies in the [issue tracker](https://github.com/automic-vault/automic-vault/issues).
