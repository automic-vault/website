## Command reference

```text
av scan [--show-all|--json]
av doctor [<tool>] [--json]
av detectors --json
av hardeners --json
av bless [--endorse-launcher] <path>
av inject +KEY... [--] <command>
av inject -- <command>
av inject --mode=fd +KEY:FD... -- <command>
av proxy +KEY... [--] <command>
av list
av save [--multiline | --stdin] [--project-directory=DIR] KEY
av harden <tool> [-y|--yes]
av unharden brew [-y|--yes]
av gpg-sign [GPG options]
av open [--secret-gate <id>]
av help
av --version
```

Old v1 commands `install`, `contain`, `dotenv`, `credential-helper`, `gate`, and
`trace` are not part of 4.6.0.

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

These are authoritative for the installed build. The `documentation` field
contains the source-checked behavior and
security model. Generated environment wrappers warn that the Target can read
injected credentials; dedicated/native routes may provide narrower boundaries.

See the [hardener reference](/docs/hardeners/) for the rendered documentation.

### `av save` and `av list`

```text
av save [--multiline | --stdin] [--project-directory DIR] KEY
av save [--multiline | --stdin] [--project-directory=DIR] KEY
av list
av ls
```

`list` shows names, never Values, and accepts no arguments. `save` defaults to a
hidden single line; select `--multiline` for hidden multiline entry or `--stdin`
for exact redirected input. Both modes require import Approval:

```sh
av save --multiline DEPLOY_PRIVATE_KEY
av save --stdin --project-directory=. API_TOKEN <&3
```

The second example assumes a trusted producer has supplied readable FD 3.
Input is nonempty UTF-8 without NUL bytes, at most 1 MiB. See
[saving safely](/docs/authority/#saving-safely) for EOF and replacement behavior.

### `av inject`

```text
av inject [--replace-existing-env] [--allow-missing-keys] \
  +KEY [+KEY...] [--] COMMAND [args...]
av inject -- COMMAND [args...]
av inject --mode=fd +KEY:FD [+KEY:FD...] -- COMMAND [args...]
```

Bare commands resolve through PATH; a Target containing `/` must be absolute.
In the default environment mode (`--mode=env`), existing environment values win with a warning unless
`--replace-existing-env` is used. Missing requested Secrets fail unless
`--allow-missing-keys` leaves them unset. Duplicate/invalid names and root are
rejected. On success, `exec` replaces `av` with the Target. Legacy
`--allow-existing-env`, `--force`, `--import`, and `--migrate` are rejected.

#### File descriptor delivery

Available since 4.6.0:

```sh
av inject --mode=fd +FOO:3 +BAR:4 -- /path/to/consumer
```

The consumer must read the indicated descriptors. Each Secret arrives through
its own read-only anonymous pipe as exact stored UTF-8 bytes, then EOF. There
is no bundle format, trimming, or added newline. Consumed bytes are not replayed.
Automic Vault removes the requested Secret Names from the Target's environment,
including existing values, and preserves stdin/stdout/stderr and unrelated
environment entries.

Every invocation requires fresh human Approval. Direct Access Rules,
Blessings, Tool-specific policies, and Temporary Access Grants do not authorize
FD delivery. Approval shows the mappings and selected Value sources;
Authorization History records them before release. Update the app and CLI
together: older apps reject this operation.

Descriptors must be distinct, unused decimal integers of 3 or higher, without
leading zeros. Every Secret requires a mapping. Duplicate names, missing
Secrets, `--allow-missing-keys`, `--replace-existing-env`, and FD shebangs are
rejected. If a Value exceeds available pipe capacity, the command fails before
starting the Target; this ceiling can be smaller than the 1 MiB save limit.

The Target can copy the bytes or pass descriptors to its children. FD delivery
does not provide encrypted backup/recovery or restore whitespace lost during an
earlier import. See the [repository guide](https://github.com/automic-vault/automic-vault/blob/main/docs/direct-secret-access.md#apply-secrets-through-file-descriptors).

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

FD mode in an `av inject` shebang is currently unsupported. A Blessed Script
can invoke `av inject --mode=fd` as a command, but each invocation still needs
fresh human Approval.

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
