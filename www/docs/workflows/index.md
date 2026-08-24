## Common workflows

Every migration follows the same safe sequence: observe the current state, read
the Tool-specific design, establish the protected route, verify a harmless
operation, inspect the decision, and only then remove the old credential. Do not
turn a migration into an outage by deleting the only working copy first.

### GitHub CLI

```sh
av scan --json --detector gh-cli-hosts-token
av harden gh
av doctor gh
gh auth status
```

Inspect the `gh` Secret Gate before automic authorization. Direct `inject` works,
but the Tool-specific Gate can narrow policy by operation.

Use `gh auth status` as the first test because it is read-only. A repository
creation, release, issue edit, or token-management call is a write and should
remain Approval Required until the exact launcher and workflow justify a narrow
rule or Temporary Access Grant.

### AWS CLI

```sh
av harden aws
av doctor aws
aws sts get-caller-identity
```

The AWS route installs and verifies AWS's signed CLI under `/opt/av/aws`, moves
the default long-lived pair into Custody, and issues short-lived STS credentials.

Verify the account and ARN returned by `sts get-caller-identity` before any
write. The short-lived session narrows credential lifetime; IAM still decides
what the resulting AWS identity can do.

### Docker

```sh
av harden docker
av doctor docker
docker pull registry.example.test/team/image:latest
```

Docker hardening retains the vendor-signed CLI and gates registry credentials on
live identity, ancestry, arguments, and requested registry.

Test against a non-sensitive image first. Registry authorization is separate
from container isolation: a successful protected pull says nothing about the
image's safety.

### Project-specific Values

```sh
mkdir -p "$PWD/example-project"
av save --project-directory="$PWD/example-project" GH_TOKEN
cd "$PWD/example-project"
av inject +GH_TOKEN gh auth status
```

Confirm History names the expected Project Value source. A nested Project Value
wins over a broader ancestor; a directory on another filesystem never matches.
Moving a checkout can therefore change selection without changing its Git
remote. Treat the canonical physical directory as configuration, not identity.

### One-off environment application

```sh
av inject +SENTRY_AUTH_TOKEN sentry-cli info
```

Use `inject` when no narrower native or Tool-specific route exists. Inspect
existing environment conflicts; by default an already exported value wins with
a warning. `--replace-existing-env` is an explicit precedence decision, not a
routine flag.

### Proxy-only delivery

```sh
av proxy +VARLOCK_SAMPLE_SECRET -- /path/to/target
```

Approve the session, then approve only expected destinations as they appear.
Terminate the session from Active Proxies when the task ends. Use a real Secret
Name in practice; the sample above documents shape without exposing a credential.

### Blessing a release script

```sh
chmod 700 ./release.sh
av bless ./release.sh
./release.sh v3.16.1
```

Review the digest, interpreter, Secret Names, and capability ceilings in Blessed
Scripts before the first run. If an edit is intentional, inspect the complete
diff and create a new Blessing. If an edit is unexpected, revoke and investigate.

### Enrolling an unsigned developer CLI

Open **Launcher Bundles**, choose the regular single-file Mach-O executable,
review its hashes and entitlements, and install the generated bundle. Point
policy at the installed command. On update, prepare and enroll a new generation;
the old digest must not silently become the new trusted payload.

### GPG-signed commits

Configure GPG Signing and `av-gpg`, then verify:

```sh
git commit --allow-empty -m 'verify signing'
git log --show-signature -1
```

Check the signer fingerprint and payload in Git's output. **Allow Signing** is
appropriate only for an exact Verified Launcher whose commit workflow you
accept; otherwise retain Approval Required.
