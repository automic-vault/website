# Automic Vault CLI manual

This manual documents the public `av` command surface shipped by Automic Vault
3.8.0. It was checked against the 3.8.0 source on August 16, 2026.

The supported top-level commands are:

```text
av scan [--show-all | --json]
av doctor [COMMAND] [--json]
av detectors --json
av hardeners --json
av bless [--endorse-launcher] PATH
av inject +KEY [--] COMMAND
av save [--project-directory=DIR] KEY
av harden NAME [--yes]
av unharden brew [--yes]
av open [--secret-gate ID]
```

Commands from the earlier v1 CLI—including `install`, `contain`, `dotenv`,
`credential-helper`, `gate`, and `trace`—are not part of the 3.8.0 CLI.

## Install and verify

Automic Vault requires macOS. Homebrew is one supported installation path.

```sh
brew install --cask automic-vault/isotopes/automic-vault
open /Applications/Automic\ Vault.app
av --version
av help
```

You can also download the current DMG from
[GitHub Releases](https://github.com/automic-vault/automic-vault/releases/latest)
or review and run the
[website installer](https://www.automicvault.com/install.sh).

The menu bar app owns Approval UI and Authorization Policy. Open it before using
commands that require Approval:

```sh
av open
```

## Five-minute path

Run a complete exposure scan, save one value through the hidden terminal prompt,
then release it only to the command that needs it:

```sh
av scan --show-all
av save GH_TOKEN
av inject +GH_TOKEN gh auth status
```

`av save` reads from `/dev/tty`; it does not read standard input. The value is
not echoed.
Remove any old plaintext export only after confirming the approved command works.

## Mental model

Automic Vault stores named Secret Values in the macOS Keychain. `av inject`
submits an Authorization Request containing the Verified Launcher, resolved
Target, arguments, working directory, requested Secret Names, selected Value
sources, and any existing environment conflicts. The app applies the
Authorization Policy or asks for Approval. If allowed, `av` replaces itself
with the Target process.

This is a Secret Application boundary, not a general sandbox. The Target receives
the rest of the current environment and controls a Secret after receipt. Keep
macOS, the app, and each authorized Target in your trust model.

## `av scan`

Scan the current home directory for supported credential Exposures, Hazards,
and other Detector Findings.

```sh
av scan
av scan --show-all
av scan --json
```

- The default human report hides medium- and low-severity findings.
- `--show-all` includes those lower-severity findings.
- `--json` writes an object containing `findings` and `gui_path`.
- A completed scan exits `0` even when it reports findings. Treat the report, not
  the status code, as the audit result.

Each finding includes a source, severity, explanation, remediation, affected
paths, and a source-linked detector document.

## `av doctor`

Check whether installed hardening still has the expected target, dependencies,
launcher type, owner, permissions, content, and `PATH` precedence.

```sh
av doctor
av doctor gh
av doctor gh --json
av doctor claude
av doctor codex
```

Without a selector, `doctor` checks applicable installed hardeners. A selector
can be a hardener, one of its commands, or a supported signed agent CLI.

- Exit `0`: every selected check is healthy.
- Exit `1`: one or more issues require attention.
- Exit `2`: invalid arguments, an unknown selector, or a selector with no
  Doctor-owned checks.

JSON output contains `results`; each issue includes its `kind`, message,
remediation, and relevant stub, target, or resolved path.

## Signed CLI launchers

Automic Vault can bind an Authorization Policy to either a signed app bundle or a
Developer ID-signed standalone executable. It validates the live code signature
and stores the launcher's designated requirement, which identifies the binary
and its signing team.

A standalone executable must have a valid Developer ID Application signature,
identifier, and Team ID. It must pass strict macOS signature validation and
enable Hardened Runtime before it can receive Secret Gate access. Unsigned and
arbitrary ad-hoc signed executables are rejected as ordinary launchers.

For one regular single-file Mach-O CLI, the app can instead create a Launcher
Bundle. Automic Vault snapshots the executable, signs the payload and launcher
with Hardened Runtime, installs the bundle and command link root-owned, and
enrolls that exact generation. Every authorization revalidates the live code
identity, nested signatures, payload digest, enrolled generation, and runtime
posture. Any change hard-denies the request.

A Launcher Bundle establishes identity and integrity for the exact packaged
code. It does not establish publisher trust or make the code safe. Scripts and
directory-shaped tools are not supported.

Run `av doctor claude` or `av doctor codex` to inspect the executable selected by
your current `PATH`. In Automic Vault Settings, add the launcher to the relevant
tool or blessed-script policy and select the resolved native executable rather
than a shell or package-manager shim. Review its identifier, Team ID, path, and
designated requirement before allowing it.

If the identity cannot be verified later, automic authorization fails closed and
requires Approval. Code signing proves identity and integrity, not intent.
Keep the terminal or agent app's permissions minimal because TCC remains
app-scoped.

## `av save`

Store a Global Value or a Project Value for one Secret Name:

```sh
av save GH_TOKEN
av save --project-directory=. GH_TOKEN
```

The Secret Name must be a valid environment variable name: it begins with a letter or
underscore and continues with letters, digits, or underscores. The command opens
`/dev/tty`, disables terminal echo while reading, trims the line ending, rejects
an empty value, and restores echo even if reading fails.

A Secret Name may have one Global Value and multiple Project Values. For each
requested name, `av inject` selects the nearest Project Value at or above the
physical working directory, then the Global Value if no Project Value matches.
The Project Directory selects a value; it is not an authorization boundary. A
read failure for the selected Value does not fall back to another Value.

Pipes do not provide the value:

```sh
# Wrong: save deliberately does not read stdin.
printf '%s\n' "$GH_TOKEN" | av save GH_TOKEN
```

## `av inject`

Request one or more named Secrets, then execute a Target:

```sh
av inject +GH_TOKEN gh auth status
av inject +AWS_ACCESS_KEY_ID +AWS_SECRET_ACCESS_KEY -- aws sts get-caller-identity
```

Full syntax:

```text
av inject [--replace-existing-env] [--allow-missing-keys] \
  +KEY [+KEY...] [--] COMMAND [args...]
```

Behavior:

- A bare command such as `gh` is resolved from `PATH`.
- A target containing a slash must be an absolute path.
- `--` is optional, but useful when the target or its arguments could be
  mistaken for inject options.
- Existing environment values win by default. A warning is printed for each
  conflict.
- `--replace-existing-env` lets the approved Keychain value replace an existing
  environment value.
- A missing requested Secret fails the run by default.
- `--allow-missing-keys` leaves missing Secrets unset; this is primarily useful for
  generated wrappers that support optional credentials.
- Duplicate or invalid Secret Names are rejected.
- `av inject` refuses to run as root.
- The menu bar approval service must be running.

The Authorization Request is denied if the service cannot authenticate, the
Authorization Policy does not allow the operation, or the user declines it. If
allowed, `av` uses `exec`, so the Target replaces the `av` process rather than becoming a detached
child.

### Shebang use

`av inject` can act as a script interpreter:

```sh
#!/usr/local/bin/av inject +API_TOKEN /bin/sh
set -eu
exec curl -H "Authorization: Bearer $API_TOKEN" https://api.example.test/me
```

The script path is included in the Authorization Request. Keep the interpreter
path absolute and the shebang to one requested-Secret set plus one interpreter.

## `av bless`

Review an exact script and its Script Declaration:

```sh
av bless ./release.sh
```

The app shows the canonical path, SHA-256 checksum, requested Secret Names,
Capabilities, injection flags, and Target interpreter. Approval creates a
Blessing bound to that complete review. Editing or moving the script makes the
Blessing stop matching.

A blessable script must be a regular UTF-8 file no larger than 1 MiB and start
with an absolute `av inject` shebang whose target interpreter is also absolute:

```sh
#!/usr/local/bin/av inject +GH_TOKEN /bin/sh
# --- automic-vault
# capabilities:
#   gh: write
# ---
set -eu
gh release create "$1"
```

The optional manifest must immediately follow the shebang. It may grant named
Secret Gates one of `read-only`, `local-write`, `write`, or `full`; unsupported
gates or Access Levels are rejected. `read-and-updates` and `trusted` remain
compatibility aliases. Capabilities are ceilings: undeclared or broader requests
from the script are denied. `full` includes Secret Disclosure and Elevated
Secret Application and should be granted sparingly.

Run `av bless --endorse-launcher ./release.sh` to include a Launcher Endorsement
in the review. Only an endorsed Verified Launcher can use the Blessing with
automic authorization. With no Launcher Endorsement, each execution requires
Approval. `--endorse-caller` remains a compatibility alias.
Blessed scripts run from a verified `/dev/fd/N` snapshot so edits cannot race
approval. `AV_SCRIPT_PATH` contains the canonical source path and `AV_SCRIPT_DIR`
its containing directory. Blessings can be inspected, narrowed, or revoked
under **Blessed Scripts** in the app.

## `av harden`

Apply a named hardener:

```sh
av harden NAME
av harden NAME --yes
```

Hardeners are Tool-specific security transformations. Depending on the Tool, a
Hardener can move existing Credentials into Keychain, install or replace a
Launcher, change protected ownership, or enable a native credential route.
Review its embedded documentation and prompts before approving system changes.
Some root-owned launchers require `sudo`; follow the selected hardener's
instructions rather than running every hardener as root.

`--yes` skips confirmation where the selected hardener supports it. A successful
run prints the matching `av doctor NAME` command.

Discover the current catalog before choosing a name:

```sh
av hardeners --json |
  jq '.hardeners[] | {name, applicable, hardened, commands, documentation}'
```

The source includes dedicated hardeners for AWS CLI, Docker, Homebrew, GitHub
CLI, sudo, Stripe, and Supabase plus generated environment wrappers and direct
Isotope installs for supported tools. Availability and applicability depend on
the installed tool and current machine.

AWS hardening installs and verifies AWS's signed CLI under `/opt/av/aws`, moves
the default long-lived key pair into Secret Custody, and uses a native helper to
issue short-lived STS credentials for normal invocations. Docker hardening keeps
the vendor-signed Docker CLI and gates registry credential release on its live
identity, ancestry, arguments, and requested registry.

## `av unharden brew`

Temporarily restore the system Homebrew launcher when a cask migration requires
ordinary Homebrew behavior:

```sh
av unharden brew
av unharden brew --yes
```

This command is intentionally limited to Homebrew. Follow the printed recovery
and re-hardening instructions; do not treat it as a generic hardener rollback.

The project [Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
defines the security terms used throughout these docs.

## Machine-readable catalogs

List every detector and its source documentation:

```sh
av detectors --json |
  jq '.detectors[] | {name, docs_url, documentation}'
```

List hardener state, commands, paths, and Secret Gate routes:

```sh
av hardeners --json |
  jq '.hardeners[] | {
    name,
    applicable,
    hardened,
    stub_path,
    target_path,
    commands,
    secret_gate
  }'
```

These commands are the most reliable way for automation to discover the catalog
shipped by the installed build. Do not hard-code a copied list of detectors or
hardeners.

## `av open`

Open the Automic Vault app and show its main window:

```sh
av open
```

Open a specific Secret Gate by its path-safe ID:

```sh
av open --secret-gate gh
```

Gate IDs may contain ASCII letters, digits, hyphens, underscores, and periods.
The option is also used by product links and generated guidance.

## Global options and exit status

```sh
av help
av --version
av inject --help
av inject --version
```

The CLI convention is:

- `0` for a completed command or approved execution;
- `1` for an operational failure, denied request, or unhealthy `doctor` result;
- `2` for top-level usage errors and invalid `doctor` selection.

The executed target's own behavior begins after a successful `inject`, because
that target replaces the `av` process.

## Source of truth

This manual was checked against the following implementation files:

- [`src/cli/mod.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/mod.rs)
- [`src/cli/scan.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/scan.rs)
- [`src/cli/doctor.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/doctor.rs)
- [`src/cli/save.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/save.rs)
- [`src/cli/inject.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/inject.rs)
- [`src/cli/bless.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/bless.rs)
- [`src/cli/launcher_bundle.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/launcher_bundle.rs)
- [`src/cli/open.rs`](https://github.com/automic-vault/automic-vault/blob/3.8.0/src/cli/open.rs)
- [`src/isotopes`](https://github.com/automic-vault/automic-vault/tree/3.8.0/src/isotopes)

For a particular installation, prefer the installed command's `av help`,
`av detectors --json`, and `av hardeners --json` output. Report documentation or
security discrepancies in the
[Automic Vault issue tracker](https://github.com/automic-vault/automic-vault/issues).
