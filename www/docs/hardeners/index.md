# Hardener reference

Hardeners replace supported insecure credential paths with Tool-specific routes that Automic Vault can identify, authorize, and verify. Check the installed state before changing it:

```sh
av hardeners --json
av harden TOOL
av doctor TOOL
```

## Hardeners

- [AWS](./aws/) — `av harden aws`
- [Codex](./codex/) — `av harden codex`
- [Docker](./docker/) — `av harden docker`
- [GitHub CLI](./gh/) — `av harden gh`
- [goat](./goat/) — `av harden goat`
- [Homebrew](./brew/) — `av harden brew`
- [OpenTofu](./opentofu/) — `av harden opentofu`
- [ordercli](./ordercli/) — `av harden ordercli`
- [Oxide CLI](./oxide-cli/) — `av harden oxide-cli`
- [Railway](./railway/) — `av harden railway`
- [Stripe CLI](./stripe/) — `av harden stripe`
- [sudo](./sudo/) — `av harden sudo`
- [Supabase](./supabase/) — `av harden supabase`
- [Terraform](./terraform/) — `av harden terraform`
