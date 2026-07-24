# Automic Vault CLI manual

This manual documents the public `av` command surface shipped by Automic Vault
2.1.0 and still present in the current source tree. It was checked against
`~/sync/av2` on July 24, 2026.

The supported top-level commands are:

```text
av scan [--show-all | --json]
av doctor [COMMAND] [--json]
av detectors --json
av hardeners --json
av inject +KEY [--] COMMAND
av save KEY
av harden NAME [--yes]
av open [--secret-gate ID]
```

Commands from the earlier v1 CLI—including `install`, `contain`, `dotenv`,
`credential-helper`, `gate`, and `trace`—are not part of the 2.1.0 CLI.

## Install and verify

Automic Vault requires macOS and currently expects Homebrew.

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

The menu bar app owns approval UI and policy. Open it before using commands that
request approval:

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

Automic Vault stores named values in the macOS Keychain. `av inject` asks the
signed menu bar app to approve a specific request containing the resolved target,
arguments, working directory, requested keys, and any existing environment
conflicts. After approval, `av` replaces itself with the target process.

This is a secret handoff boundary, not a general sandbox. The target receives the
rest of the current environment, and an approved executable can use a released
secret. Keep macOS, the app, and each approved target in your trust model.

## `av scan`

Audit the current home directory for exposed credentials, unsafe tool
configuration, and other detector findings.

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
```

Without a selector, `doctor` checks applicable installed hardeners. A selector
can be a hardener or one of its commands. Current development builds also check
supported signed agent CLIs when they are present.

- Exit `0`: every selected check is healthy.
- Exit `1`: one or more issues require attention.
- Exit `2`: invalid arguments, an unknown selector, or a selector with no
  Doctor-owned checks.

JSON output contains `results`; each issue includes its `kind`, message,
remediation, and relevant stub, target, or resolved path.

## `av save`

Store one named value in the Automic Vault Keychain:

```sh
av save GH_TOKEN
```

The key must be a valid environment variable name: it begins with a letter or
underscore and continues with letters, digits, or underscores. The command opens
`/dev/tty`, disables terminal echo while reading, trims the line ending, rejects
an empty value, and restores echo even if reading fails.

Pipes do not provide the value:

```sh
# Wrong: save deliberately does not read stdin.
printf '%s\n' "$GH_TOKEN" | av save GH_TOKEN
```

## `av inject`

Request one or more named Keychain values, then execute a command:

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
- A missing requested key fails the run by default.
- `--allow-missing-keys` leaves missing keys unset; this is primarily useful for
  generated wrappers that support optional credentials.
- Duplicate or invalid key names are rejected.
- `av inject` refuses to run as root.
- The menu bar approval service must be running.

The request is denied if the approval service cannot authenticate, the policy
does not allow the operation, or the user declines it. On approval, `av` uses
`exec`, so the target replaces the `av` process rather than becoming a detached
child.

### Shebang use

`av inject` can act as a script interpreter:

```sh
#!/usr/local/bin/av inject +API_TOKEN /bin/sh
set -eu
exec curl -H "Authorization: Bearer $API_TOKEN" https://api.example.test/me
```

The script path is included in the approval request. Keep the interpreter path
absolute and the shebang to one requested-key set plus one interpreter.

## `av harden`

Apply a named hardener:

```sh
av harden NAME
av harden NAME --yes
```

Hardeners are tool-specific migrations and launch boundaries. Depending on the
tool, a hardener can move existing credentials into Keychain, install or replace
a launcher, change protected ownership, or enable a native credential route.
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

The source currently includes dedicated hardeners for AWS CLI, Homebrew, GitHub
CLI, sudo, and Supabase plus generated environment wrappers for supported tools.
Availability and applicability depend on the installed tool and current machine.

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

- [`src/cli/mod.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/mod.rs)
- [`src/cli/scan.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/scan.rs)
- [`src/cli/doctor.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/doctor.rs)
- [`src/cli/save.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/save.rs)
- [`src/cli/inject.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/inject.rs)
- [`src/cli/open.rs`](https://github.com/automic-vault/automic-vault/blob/2.1.0/src/cli/open.rs)
- [`src/isotopes`](https://github.com/automic-vault/automic-vault/tree/2.1.0/src/isotopes)

For a particular installation, prefer the installed command's `av help`,
`av detectors --json`, and `av hardeners --json` output. Report documentation or
security discrepancies in the
[Automic Vault issue tracker](https://github.com/automic-vault/automic-vault/issues).
