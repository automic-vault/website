# Automic Vault

## Your tools have your authority. Make them ask.

Secrets for tools. Execution under control.

Automic Vault controls the last local hop between shells, scripts, agents, and
the tools they use. It keeps long-lived credentials in Keychain, releases named
values to an approved executable for one run, and asks you before a risky
command executes.

[Download for macOS](/Automic%20Vault.dmg) · [Read the docs](/docs/) ·
[Review the source](https://github.com/automic-vault/automic-vault)

## The Shortcut That Leaks a Secret

When a remote shell cannot use AWS, an agent may try to solve the problem by
reading `~/.aws/credentials` and uploading the keys from your Mac. At that
moment, a reusable cloud credential has crossed the trust boundary.

Automic Vault keeps the credential out of the agent's context. The tool request
stops at a native approval gate where you can inspect the executable, command,
working directory, and requested key, then approve it once or deny it.

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
