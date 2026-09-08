## Troubleshooting

### Approval does not appear

Run `av open` and confirm the installed app version matches `av --version`.
Inspect Authorization History for a policy denial that occurred before human
Approval was eligible. If iPhone Approval is enabled, check phone eligibility,
relay and iCloud Keychain state, device lock, and biometric availability; do not
expect a local allow button to appear as fallback.

### The wrong executable runs

Compare `command -v TOOL`, the Target in the Approval request, and `av doctor
TOOL`. Shell hashes, aliases, shims, package-manager links, and GUI PATH can all
differ. Authorize the native executable or protected launcher described by the
hardener; a mutable shell is too broad a Target.

### The wrong Project Value is selected

Compare the physical canonical working directory with every Project Directory.
The selected directory must be an ancestor on the same filesystem; the nearest
match wins. Symlink spelling, repository remote, branch, and logical `$PWD` do
not establish selection. History records the source chosen for the request.

### An environment value wins

Environment-mode `av inject` preserves an existing environment value by default and warns. Remove
the export at its source, or use `--replace-existing-env` only after confirming
that Automic Vault should override it. Do not suppress the warning without
understanding which credential the Target would otherwise receive.

FD mode instead removes the requested names from the environment, including
existing values, and delivers the stored Values on the specified descriptors.

### FD delivery fails before the consumer starts

Check that each mapping names a distinct, unused descriptor of 3 or higher.
`av` refuses to overwrite inherited descriptors. Pick unused numbers that the
consumer supports. A Value that exceeds available pipe capacity also fails
before Target execution, even if it fits the separate 1 MiB save limit.

FD delivery requires fresh human Approval. A Direct Access Rule or Blessing
does not bypass that prompt, and an FD-mode shebang is unsupported.

### A Blessing stopped matching

Path, file type, size, interpreter, declaration, and content all participate in
the reviewed state. Compare the app's baseline with the current file. Re-bless
only an intentional change; an unexplained mismatch is evidence to investigate.

### A Launcher Bundle is denied after update

Digest, signature, enrollment, entitlements, runtime, and protected ownership
fail closed. Prepare and review a new generation. Do not replace the enrolled
payload in place or add a broad compatibility exception merely to make the new
binary run.

### Proxy traffic does not appear

The Target may ignore proxy variables, use a protocol the proxy does not handle,
inherit conflicting network configuration, or open another channel. Confirm the
session is live and the process shown in Active Proxies is the process making the
request. Treat bypass as outside proxy containment, not as a UI refresh bug.

### Doctor reports healthy but the workflow fails

Doctor validates known installation invariants. The request can still be denied
by Gate policy, launcher identity, runtime, Value selection, or Tool semantics,
and the external service can reject the resulting credential. Read History and
the Tool's own error separately.

### Collecting a safe diagnostic

Record `av --version`, the relevant `av doctor TOOL --json` result, the detector
or hardener name, and a redacted History entry. Never paste Values, private keys,
proxy credentials, Secret References, session tokens, or live authorization
artifacts into an issue.

For a suspected vulnerability, follow
[security.txt](https://www.automicvault.com/.well-known/security.txt) instead of
the public issue tracker.

## Source of truth

The saving and FD delivery sections were checked against the 4.6.0 source and
tests. The linked v1 copy script was tested with disposable legacy Keychain
fixtures and the actual save implementation using isolated test storage; it is
not a full v1 upgrade test. UI screenshots come from 3.16.0. For your installed
build, prefer `av --version`, `av help`, `av detectors --json`, and `av hardeners --json`.

- [4.6.0 release](https://github.com/automic-vault/automic-vault/releases/tag/4.6.0)
- [CLI source](https://github.com/automic-vault/automic-vault/blob/4.6.0/src/cli/mod.rs)
- [App and CLI source](https://github.com/automic-vault/automic-vault/tree/4.6.0/src)
- [Detectors](https://github.com/automic-vault/automic-vault/tree/4.6.0/src/detectors)
- [Hardeners](https://github.com/automic-vault/automic-vault/tree/4.6.0/src/isotopes)
- [Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
- [Architecture](https://github.com/automic-vault/automic-vault/blob/main/docs/architecture.md)

Report discrepancies in the [issue tracker](https://github.com/automic-vault/automic-vault/issues).
