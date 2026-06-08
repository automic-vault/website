# Automic Vault

Let agents use tools, not your raw secrets.

Automic Vault is a local macOS security layer for AI coding agents. It keeps
credentials out of model context and plaintext files, asks before risky tool
actions, and installs packages in roots agents cannot quietly rewrite.

## What Changes

- Secrets become tool-bound: approved command-line tools can use the credentials
  they own without exposing raw values to agents or unrelated processes.
- Risky actions ask at execution: publishing, token reveal, and cloud mutations
  can require approval where the command actually runs.
- Packages install into owned roots: agent-used tools stay predictable instead
  of drifting through ambient user-writable paths.

## Key Workflows

- Move `.env`, shell profile, `.npmrc`, `.netrc`, GitHub CLI, AWS, and MCP
  credentials out of agent-readable plaintext.
- Inject approved secrets only into trusted tools.
- Scan local files before an agent run.
- Trace shell installers before an agent or developer runs them.
- Install and browse package coverage through Nucleus and the package catalog.

## Key Pages

- [Documentation](/docs/): CLI commands and runtime patterns.
- [Security](/security/): threat model and disclosure information.
- [Security Methods and Gaps](/security/whitepaper/): candid white paper on controls, caveats, holes, successes, and hardening work.
- [Pricing](/pricing/): free open-source software pricing.
- [AI agent secret scanner](/secret-scanner-for-ai-agents/): local credential scanning before agent runs.
- [AI agent approval gates](/ai-agent-approval-gates/): human approval for sensitive commands.
- [Package catalog](/pkg/): package-specific coverage and local secret-handling metadata.
- [Blog](/blog/): notes on agent tooling, package hardening, and local developer security.
- [llms.txt](/llms.txt): concise AI system navigation.
- [llms-full.txt](/llms-full.txt): all checked-in site text in one file.

Automic Vault is free open-source software under the Apache License 2.0.
