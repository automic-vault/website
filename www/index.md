# Automic Vault

## Secrets for tools. Execution under control.

Automic Vault is a local macOS secrets and execution manager for developer
tools. It sits between the process asking and the executable that runs. Long-
lived credentials stay in Keychain, approved executables receive named values
for one run, and risky commands can require human approval.

[Download for macOS](/Automic%20Vault.dmg) · [Read the docs](/docs/) ·
[Review the source](https://github.com/automic-vault/automic-vault)

## The Local Execution Boundary

1. A shell, script, or agent requests work.
2. Automic Vault resolves the executable, arguments, working directory, and
   requested secrets.
3. You approve the secret handoff or sensitive command.
4. The local tool receives the secret for that execution and contacts the
   external service itself.

Automic Vault controls the last local hop. Only the approved tool receives the
raw credentials.

## Tool-Scoped Secrets

- Store long-lived values with `av save` in the Automic Vault Keychain.
- Use `av inject` to give named values to one approved executable.
- Prefer native credential protocols such as AWS `credential_process`,
  Kubernetes `ExecCredential`, and registry helpers.
- Keep raw values out of prompts, transcripts, shell startup files, and project
  configuration.

## Execution Management

`av contain` gives an agent a synthetic toolchain. Host tool requests return to
Automic Vault with the executable path, arguments, current directory, parent
process, and requested keys. Commands such as `gh release create`,
`npm publish`, or `terraform apply` can stop for human approval before they use
local authority.

```sh
printf '%s\n' "$GITHUB_TOKEN" | av save GITHUB_TOKEN
av inject +GITHUB_TOKEN /opt/homebrew/bin/gh repo view
av contain codex
```

## Security at the Executable Layer

Automic Vault uses local facts available at execution time: the binary on disk,
its path, arguments, parent process, working directory, and tool-specific
credential protocol. Central vaults can remain the source of truth while
Automic Vault controls the moment a Mac tool receives and uses a credential.

Automic Vault is Apache-2.0 open-source software. Its security model assumes
macOS Keychain, System Integrity Protection, and the signed app remain
trustworthy. Root compromise and malicious approved executables remain outside
that boundary.

## Founder

Max Howell created Homebrew. Automic Vault applies that local-infrastructure
experience to the authority developer tools use when they run.

## Key Pages

- [Documentation](/docs/)
- [Security model](/security/)
- [Security methods and gaps](/security/whitepaper/)
- [Pricing](/pricing/)
- [Source](https://github.com/automic-vault/automic-vault)
- [llms.txt](/llms.txt)
