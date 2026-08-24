# Hardener reference

Hardeners replace supported insecure credential paths with Tool-specific routes that Automic Vault can identify, authorize, and verify. Check the installed state before changing it:

```sh
av hardeners --json
av harden TOOL
av doctor TOOL
```

## Tool-specific hardeners

- [AWS](./aws/) — `av harden aws`
- [Codex](./codex/) — `av harden codex`
- [Docker](./docker/) — `av harden docker`
- [Homebrew](./brew/) — `av harden brew`
- [GitHub CLI](./gh/) — `av harden gh`
- [Stripe CLI](./stripe/) — `av harden stripe`
- [sudo](./sudo/) — `av harden sudo`
- [Supabase](./supabase/) — `av harden supabase`

## Environment-wrapper hardeners

These hardeners install a protected launcher for the Tool and migrate supported credentials into Automic Vault.

- [Akamai](./akamai/) — `av harden akamai`
- [Algolia](./algolia/) — `av harden algolia`
- [Argo CD](./argocd/) — `av harden argocd`
- [Checkmarx AST CLI](./ast-cli/) — `av harden ast-cli`
- [Buf](./buf/) — `av harden buf`
- [Censys](./censys/) — `av harden censys`
- [Checkov](./checkov/) — `av harden checkov`
- [CircleCI](./circleci/) — `av harden circleci`
- [Civo](./civo/) — `av harden civo`
- [Cloudsmith CLI](./cloudsmith-cli/) — `av harden cloudsmith-cli`
- [Composer](./composer/) — `av harden composer`
- [doctl](./doctl/) — `av harden doctl`
- [flyctl](./flyctl/) — `av harden flyctl`
- [glab](./glab/) — `av harden glab`
- [Gotify](./gotify/) — `av harden gotify`
- [GPTCommit](./gptcommit/) — `av harden gptcommit`
- [grafanactl](./grafanactl/) — `av harden grafanactl`
- [Heroku](./heroku/) — `av harden heroku`
- [Hetzner Cloud](./hcloud/) — `av harden hcloud`
- [Hugging Face CLI](./huggingface-cli/) — `av harden huggingface-cli`
- [JFrog CLI](./jfrog-cli/) — `av harden jfrog-cli`
- [Grafana k6](./k6/) — `av harden k6`
- [LuaRocks](./luarocks/) — `av harden luarocks`
- [MinIO Client](./minio-mc/) — `av harden minio-mc`
- [Netlify CLI](./netlify-cli/) — `av harden netlify-cli`
- [npm](./node/) — `av harden node`
- [pnpm](./pnpm/) — `av harden pnpm`
- [Pulumi](./pulumi/) — `av harden pulumi`
- [Qwen Code](./qwen-code/) — `av harden qwen-code`
- [RunPod CLI](./runpodctl/) — `av harden runpodctl`
- [s3cmd](./s3cmd/) — `av harden s3cmd`
- [Sentry CLI](./sentry-cli/) — `av harden sentry-cli`
- [Snowflake CLI](./snowflake-cli/) — `av harden snowflake-cli`
- [Snyk](./snyk/) — `av harden snyk`
- [Transifex CLI](./transifex-cli/) — `av harden transifex-cli`
- [Travis](./travis/) — `av harden travis`
- [Twine](./twine/) — `av harden twine`
- [Vagrant](./vagrant/) — `av harden vagrant`
- [HashiCorp Vault](./vault/) — `av harden vault`
- [VirusTotal CLI](./virustotal-cli/) — `av harden virustotal-cli`
- [Vultr CLI](./vultr/) — `av harden vultr`
- [OpenWhisk](./wsk/) — `av harden wsk`
