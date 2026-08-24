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
