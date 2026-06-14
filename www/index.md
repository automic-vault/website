# Automic Vault

Don't get owned by your own tools.

Secure the tools you brew install.

From the creator of Homebrew, Automic Vault detects secret exposure, hardens
packages that work with secrets, encrypts `.env` files, and monitors the tools
you install with Homebrew, npm, pip, and curl one-liners.

## Detect

Supply chain attacks are up. Your credentials are the prize.

Automic Vault finds tokens, credentials, and helper leaks while they're still
on your machine.

Detect secret exposure in your stack before the next supply chain attack bites
you. Automic Vault surfaces package-owned tokens, credential files, helper
leaks, and agent-readable config while the tools are still local to your Mac.

## Harden Secrets

Off disk. Into Keychain.

One command moves plaintext credentials out of reach of agents and malware.

Automic Vault patches packages that work with secrets to keep those secrets
away from malware and agents. Supported tools get a Keychain-backed helper
path, so the command can run without leaving reusable credentials in files any
local process can read.

## Harden Immutability

Agents can run your tools without rewriting them.

Sealed installs. Controlled updates. Nothing changes without you.

Stop agents from modifying themselves by installing packages immutably, and
stop agents or malware from modifying vital tools in your stack. Automic Vault
puts tools in sealed roots and exposes a controlled `av` shim on `PATH`: agents
can run the tool, but changing the tool itself routes through an approved
update.

## Harden .env

Encrypt `.env`. Break nothing.

Keys stay in Keychain. Your shell keeps working.

Automic Vault provides dotenvx-compatible `.env` file encryption with the
private key securely stored in the AV Keychain.

## Monitor

Install freely. Know immediately.

Homebrew, npm, pip, curl: keep using all of it. We'll flag risky changes.

Keep installing with Homebrew, npm, pip, and curl one-liners. Automic Vault
watches for new hazards in the tools and local config that agents can reach.

## Secret Exposure Examples

- `gh auth token` prints a GitHub bearer token that an agent, script, or
  compromised tool can copy into API calls.
- `cat ~/.aws/credentials` turns a readable dotfile into cloud account access.
- `printf 'protocol=https\nhost=github.com\n\n' | git credential fill` asks the
  local credential helper to reveal repository credentials, even when there is
  no obvious token file.

## Built by Max Howell

Homebrew made installing tools normal. Automic Vault adds the local boundary.

Max Howell created Homebrew. Automic Vault comes from the same operating
reality: developers install a lot of tools, those tools hold real authority,
and the endpoint needs a boundary before agents or compromised packages can
turn local secrets into access.

> we needed this yesterday but i'll take it now
>
> - Hira, @Hiraweb3

Free, open source local security for agent toolchains.

Automic Vault is free open-source software under the Apache License 2.0.

## Key Pages

- [Documentation](/docs/): CLI commands and runtime patterns.
- [Security](/security/): threat model and disclosure information.
- [Security Methods and Gaps](/security/whitepaper/): candid white paper on controls, caveats, holes, successes, and hardening work.
- [Blog](/blog/): notes on agent tooling, package hardening, and local developer security.
- [Agent Pack](/blog/agent-pack/): agent CLIs and coding assistants in one installable pack.
- [UNIX++ Pack](/blog/unix-plus-plus/): modern command line replacements and operators in one installable pack.
- [The Agentic Toolkit](/blog/agentic-toolkit/): all the tools agents need in one installable pack.
- [Pricing](/pricing/): free open-source software pricing.
- [security.txt](/.well-known/security.txt): machine-readable security disclosure policy.
- [llms.txt](/llms.txt): concise AI system navigation.
- [llms-full.txt](/llms-full.txt): all checked-in site text in one file.

## Core Use Cases

- Find plaintext credentials in local dev-tool files such as `.env`, `.netrc`,
  `.npmrc`, GitHub CLI config, AWS credentials, and MCP config.
- Harden supported Homebrew, npm, and PyPI tools so secrets are exposed only to
  approved executables at runtime.
- Ask before sensitive commands publish packages, change cloud state, reveal
  tokens, or use protected secrets.
- Keep watching new installs, stale tools, and local config for hazards.
- Trace shell installers before an agent or developer runs them.

## Blog

- [Agent Pack](/blog/agent-pack/): 10 agent CLIs and coding assistants for
  terminal-native planning, editing, review, model routing, and usage
  inspection.
- [UNIX++ Pack](/blog/unix-plus-plus/): 23 modern command line replacements and
  operators for search, file inspection, process monitoring, data wrangling,
  HTTP/DNS work, and file watching.
- [The Agentic Toolkit](/blog/agentic-toolkit/): 26 Homebrew packages for
  media processing, image manipulation, runtimes, search, shell, build, OCR,
  metadata, and document conversion.
- [Preventing the Nx Console extension compromise](/blog/prevent-nx-console-vscode-compromise/): Nx Console 18.95.0 stole local developer credentials from editor sessions. Automic Vault would have stopped the local secret access.
- [Preventing the GitHub employee device breach](/blog/prevent-github-vscode-extension-breach/): A poisoned VS Code extension reached a GitHub employee device. Automic Vault would have prevented local credentials from becoming repository access.
- [Preventing the durabletask PyPI compromise](/blog/prevent-durabletask-pypi-compromise/): Malicious durabletask PyPI releases fetched rope.pyz and stole cloud and developer secrets. Automic Vault would have blocked the local theft path.
- [Preventing the TanStack npm credential theft](/blog/prevent-tanstack-npm-compromise/): TanStack packages were poisoned through trusted publishing, then stole local secrets. Automic Vault would have prevented the endpoint theft.
- [Preventing the node-ipc npm backdoor](/blog/prevent-node-ipc-npm-backdoor/): The node-ipc backdoor ran on module load and exfiltrated secrets over DNS. Automic Vault would have prevented useful credential theft.
- [Preventing the Bitwarden CLI npm compromise](/blog/prevent-bitwarden-cli-npm-compromise/): The compromised Bitwarden CLI npm package used install-time code to steal developer secrets. Automic Vault would have stopped the local theft.
- [Preventing the LiteLLM PyPI compromise](/blog/prevent-litellm-pypi-compromise/): LiteLLM 1.82.7 and 1.82.8 stole local credentials. Automic Vault would have prevented the workstation credential theft phase.
