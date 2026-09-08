# Hardener reference

Hardeners replace supported insecure credential paths with Tool-specific routes that Automic Vault can identify, authorize, and verify. Check the installed state before changing it:

```sh
av hardeners --json
av harden TOOL
av doctor TOOL
```

## Hardeners

- [Aliyun Cli](./aliyun-cli/) — `av harden aliyun-cli`
- [AWS](./aws/) — `av harden aws`
- [Codex](./codex/) — `av harden codex`
- [Docker](./docker/) — `av harden docker`
- [Fastly Cli](./fastly-cli/) — `av harden fastly-cli`
- [GitHub CLI](./gh/) — `av harden gh`
- [goat](./goat/) — `av harden goat`
- [Homebrew](./brew/) — `av harden brew`
- [Kubectl](./kubectl/) — `av harden kubectl`
- [Openhue Cli](./openhue-cli/) — `av harden openhue-cli`
- [OpenTofu](./opentofu/) — `av harden opentofu`
- [ordercli](./ordercli/) — `av harden ordercli`
- [Oxide CLI](./oxide-cli/) — `av harden oxide-cli`
- [Plumber](./plumber/) — `av harden plumber`
- [Podman](./podman/) — `av harden podman`
- [Railway](./railway/) — `av harden railway`
- [Rclone](./rclone/) — `av harden rclone`
- [Sqlcmd](./sqlcmd/) — `av harden sqlcmd`
- [Stripe CLI](./stripe/) — `av harden stripe`
- [sudo](./sudo/) — `av harden sudo`
- [Supabase](./supabase/) — `av harden supabase`
- [Terraform](./terraform/) — `av harden terraform`
- [Uaa Cli](./uaa-cli/) — `av harden uaa-cli`
- [Wakatime Cli](./wakatime-cli/) — `av harden wakatime-cli`
- [Wrangler](./wrangler/) — `av harden wrangler`
