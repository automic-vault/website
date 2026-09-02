# Automic Vault manual

This is the user and operator manual for Automic Vault 3.16.0 on macOS. It was
checked against the installed CLI, app UI, and 3.16.0 source on August 22, 2026.

Automic Vault does more than store a Secret. It authorizes a complete operation:
the Verified Launcher, Gate Client, Target, command and arguments, working
directory, requested Secret Names, and selected Value sources. If allowed, it
applies the Secret to the Target without displaying the stored Value.

- [Download](https://www.automicvault.com/download/)
- [Source and releases](https://github.com/automic-vault/automic-vault)
- [Canonical Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
- [Architecture and security boundaries](https://github.com/automic-vault/automic-vault/blob/main/docs/architecture.md)
- [Product positioning](https://github.com/automic-vault/automic-vault/blob/main/docs/positioning.md)

## Install and verify

```sh
brew install --cask automic-vault/isotopes/automic-vault
open /Applications/Automic\ Vault.app
av --version
av help
```

You may instead use the [latest release](https://github.com/automic-vault/automic-vault/releases/latest)
or review the [website installer](https://www.automicvault.com/install.sh). The
menu bar app owns Approval UI and Authorization Policy. Open it before an
operation that needs Approval: `av open`.

## Start here

Scan the Mac, save one Value through the hidden terminal prompt, and apply it
only to the Target that needs it:

```sh
av scan --show-all
av save GH_TOKEN
av inject +GH_TOKEN gh auth status
```

`av save` opens `/dev/tty`, turns terminal echo off, and **does not read standard input**.
Do not remove the old credential until the approved command succeeds.
For a Tool with a supplied hardener, prefer its Tool-specific flow:

```sh
av hardeners --json | jq '.hardeners[] | select(.applicable) | {name, hardened}'
av harden gh
av doctor gh
```

## Interface map

The main window is an operator console for exposure, authority, live use, and
evidence. Global search filters the selected destination; Refresh recomputes
live state. The sidebar separates four jobs:

| Job | Destinations | Question answered |
| --- | --- | --- |
| Discover | Detectors, Doctor | Where is supported insecure state, and is the protected route healthy? |
| Establish authority | Hardened Tools, Authorization Gates, Blessed Scripts, Launcher Bundles | Which exact code and operations can ask for authority? |
| Operate | Secrets, Active Proxies | Which named Values exist, and which proxy sessions are live? |
| Audit and configure | Authorization History, Settings | Why was an operation allowed or denied, and which approval routes are enabled? |

Counts are live summaries, not security conclusions. A zero beside Active
Proxies means no proxy session is registered now; it does not prove that no
Target currently holds a Value it received earlier. A clean Doctor view means
the checks implemented by that build passed; it is not a whole-machine attestation.

## Security foundations

Automic Vault's security model starts with the operation, then works outward to
identity, policy, human authority, delivery, and evidence. Reading the model in
that order avoids the most common mistake: treating possession of a Secret Name
or a signed process identity as permission by itself.

### The request envelope

An **Authorization Request** is the complete immutable operation presented to
policy. Depending on the Gate, it contains:

- the Verified Launcher and the observed execution chain;
- the Gate Client and selected Authorization Gate;
- the resolved Target executable, command, arguments, and physical working directory;
- the exact Secret Names and selected Value sources;
- Target runtime posture, including Hardened Runtime where required;
- environment conflicts and Gate-specific facts such as registry, host, or GPG payload digest.

A decision binds to that envelope. Changing an argument, Target, directory,
Value source, launcher generation, or relevant runtime fact creates a different
request. A label such as “ChatGPT,” “gh,” or “read only” is useful UI shorthand,
but is not the complete security decision.

[![Mac Approval showing command, Secret Names, working directory, Target, Verified Launcher, execution chain, and warnings](/docs/assets/approval-request.png)](/docs/assets/approval-request.png)

Before approving, read the request from top to bottom. Confirm the command is the
operation you intended, the Secret Names are the minimum required, the working
directory is expected, the full Target path is native and immutable enough for
the policy, and the Verified Launcher is the app or bundle you meant to authorize.
Warnings are part of the request, not decoration.

### Custody, Application, and Disclosure

**Secret Custody** stores a Value under macOS-backed protection. **Secret
Application** places that Value into an authorized operation without displaying
it. **Secret Disclosure** reveals the raw Value and is a stronger authority.
These are different capabilities.

A Target controls a Value after receiving it. It may log, cache, transform,
transmit, or disclose that Value. Automic Vault narrows who may receive a Value
and for which operation; it cannot retract a Value already delivered or promise
that an authorized Target behaves well.

An **Execution Gate** can authorize a privileged operation without releasing an
ordinary Secret. GPG Signing is the clearest example: the private key stays in
Custody and the caller receives a detached signature. A **Secret Gate** controls
Secret Application and, only at stronger levels where defined, Disclosure or
elevated use.

### Identity and provenance

A **Verified Launcher** is a live, revalidated code identity used as an input to
policy. Code signing, a Launcher Bundle, a blessed script digest, and Hardened
Runtime can strengthen identity and integrity. None proves benign intent.

Launcher provenance is checked again at use time. A mutable wrapper, unexpected
interpreter, replaced binary, incompatible entitlement, lost execution ancestry,
or changed script can invalidate the route. A native Target or exact reviewed
snapshot gives policy a stable object to revalidate. A shell leaves every child
behind a broad interpreter boundary.

### Authority and decision sources

An operation can be allowed by **Human**, **Policy**, or a narrowly scoped
**Temporary Access Grant**. Authorization History records the source so an
operator can distinguish “a person allowed this exact request” from “an existing
rule matched this request.”

Approval may be carried on the Mac or an eligible iPhone. The Mac remains the
**Local Execution Boundary** in both cases: it builds and revalidates the request,
applies the decision, and performs the operation. Moving the human gesture to an
iPhone does not move execution or Custody to the phone.

### Secure defaults

Defaults trade convenience for narrow authority:

- new Secret Gates begin at **Read Only**;
- GPG Signing begins at **Approval Required**;
- Direct Secret Access begins at **Approval Required**;
- Detached Processes is off;
- proxy sessions always require Approval and keep rules only in memory;
- Project Value selection never falls back after a selected Value fails to read;
- availability while locked is separate from authorization;
- unknown, elevated, Disclosure, Direct, and mutation operations are excluded from Temporary Access Grants.

Fail-closed behavior can surface as a denial after an update, move, permission
change, or runtime change. Diagnose the mismatch; do not weaken the rule merely
to restore yesterday's behavior.

### What Automic Vault does not do

Automic Vault is not a sandbox, malware detector, whole-process containment
system, network firewall, defense against a compromised kernel or root account,
or proof that signed code has good intent. Proxying does not force a Target to
use the proxy. History is not a remote, append-only audit ledger. Project
Directory is not project identity. Agent Task Context is not identity.

Those boundaries are security properties, not disclaimers to work around. They
tell you where another control is needed: sandbox the Target, restrict network
egress, protect the administrator account, ship logs remotely, or use a dedicated
short-lived credential system when the threat model requires it.

## App guide

The screenshots use a harmless sample Secret Name; stored Values remain hidden.

### Detectors

Detectors inspect supported credential locations and configurations for
**Exposures**, **Hazards**, and other security-relevant Findings. The catalog in
3.16.0 contains 157 detectors. A selected detector explains its trigger
conditions, sensitive files, current result, remediation, and source-linked
rationale.

[![Detector catalog with a passing plaintext-credential check and its source-linked rationale](/docs/assets/detectors.png)](/docs/assets/detectors.png)

**Security basis.** Detection and remediation are separate operations. A Finding
records evidence about known state. The operator reviews any credential move,
configuration rewrite, or authority change as a separate Tool-specific migration.

**Workflow.** Start with `av scan --show-all` for a human report. Use the app to
read the selected detector's paths and explanation. If a hardener is available,
review it under Hardened Tools before running `av harden TOOL`. Re-run the exact
detector and Doctor afterward.

**Limits and failure modes.** Coverage is catalog-bound. A clean result means
the detector's trigger did not fire against the files it could inspect; it does
not prove the credential exists nowhere else. Missing permissions, absent Tools,
parse failures, and unsupported versions must be interpreted from the Finding,
not collapsed into “secure.”

### Hardened Tools

Hardened Tools shows installed hardeners and native protected routes. A detail
view identifies the current launcher or Target, current result, what the hardener
changes, why that design was chosen, caveats, and recent use.

[![AWS hardener status with installed Target and embedded security reference](/docs/assets/hardened-tools.png)](/docs/assets/hardened-tools.png)

**Security basis.** A hardener removes a known plaintext or ambient-credential
path and replaces it with a route Automic Vault can identify and authorize. The
route is Tool-specific: AWS can issue short-lived STS credentials; Docker can
bind access to a registry operation; GitHub can classify read and write API
operations. Tool semantics provide narrower authority than generic environment
injection.

**Workflow.** Read the complete embedded reference, check applicability with
`av hardeners --json`, run `av harden TOOL`, then run `av doctor TOOL`. Confirm
`command -v TOOL` resolves to the protected launcher described by the hardener.
Keep the original credential until the protected read path succeeds; remove it
only after verification.

**State changes.** Depending on the Tool, hardening can move a credential into
Custody, install a signed vendor distribution, replace a command with a small
launcher, change protected ownership, or configure a native credential-helper
route. Run the hardener as the current user and elevate only the steps that ask
for `sudo`.

**Limits and rollback.** Hardening protects the credential route, not the Tool's
intent. A Tool can still disclose a Value after receiving it. Read each
hardener's rollback notes. In 3.16.0, `av unharden` exists only for Homebrew.

### Authorization Gates

Authorization Gates are the operator's view of policy. Each Gate identifies the
request type, protected Secret patterns, allowed Targets, the default rule for
all other apps, Hardened Runtime requirements, and exact per-launcher overrides.

[![GitHub Secret Gate with default policy and a verified ChatGPT override](/docs/assets/authorization-gates.png)](/docs/assets/authorization-gates.png)

**Security basis.** A Gate evaluates the complete request envelope. The same
Secret Name can therefore be Read Only for one Verified Launcher, Approval
Required for every other app, and unavailable to a Target whose runtime or path
does not match. Per-launcher policy narrows authority while live identity and
request validation remain in force.

**Workflow.** Select the Gate for the Tool, inspect Targets and Secret patterns,
then review **All Other Apps** before adding an override. Begin at the least
powerful Access Level that supports the workflow. Trigger a harmless read and
inspect Authorization History to confirm the matching rule.

**Failure modes.** A denial after an app or Tool update can mean the selected
binary, code signature, runtime, or enrolled generation changed. A missing Gate
can mean the Tool is not installed or its hardener has not established the route.
Fix the Tool-specific Gate mismatch instead of substituting broad Direct Access.

### Blessed Scripts

A Blessing binds a reviewed script to its canonical path, SHA-256 digest,
interpreter, Script Declaration, Secret Names, declared Capabilities, and
optional Launcher Endorsements. The app shows the exact enrolled state and can
revoke or replace it.

[![Blessed deployment script with digest, Secret Names, capabilities, and calling-app policy](/docs/assets/blessed-scripts.png)](/docs/assets/blessed-scripts.png)

**Security basis.** Scripts are mutable text and usually run through a powerful
interpreter. Automic Vault therefore approves a verified snapshot rather than
trusting the filename. Execution uses a checked `/dev/fd/N` snapshot so a file
cannot be swapped between verification and execution. `AV_SCRIPT_PATH` and
`AV_SCRIPT_DIR` identify the canonical source.

**Workflow.** Put the absolute `av inject` shebang first, place the optional
Script Declaration immediately after it, review requested Secret Names and
capability ceilings, then run `av bless PATH`. Use `--endorse-launcher` only when
the exact Verified Launcher should receive automic authorization for the script.

**Changes and revocation.** Editing, replacing, or moving the script invalidates
the Blessing. Re-blessing is a new security decision; review the displayed diff.
Revocation removes policy but does not undo external actions from earlier runs.

**Limits.** A capability is a ceiling, not a grant. A blessed script can still
misuse every operation inside its approved ceiling, and an interpreter remains a
large Target. Keep scripts short, deterministic, and narrow.

### Launcher Bundles

A Launcher Bundle packages one regular, single-file Mach-O CLI into a signed,
Hardened Runtime app and installs a command link for it. The detail view exposes
the bundle identifier, signing mode, installed location, command, selected-source
and signed-payload hashes, entitlements, and enrolled generation.

[![Enrolled Launcher Bundle with installed command, pinned hashes, signing, and entitlements](/docs/assets/launcher-bundles.png)](/docs/assets/launcher-bundles.png)

**Security basis.** A mutable developer CLI often lacks the stable app identity
needed for launcher policy. Bundling creates an exact signed snapshot, installs
it under protected ownership, and enrolls that generation. Automic Vault verifies
the digest, signature, enrollment, and runtime again when it is used.

**Workflow.** Choose the actual Mach-O executable, name the bundle and command,
review compatibility exceptions, prepare the snapshot, approve installation,
and verify the installed hashes in the detail view. Rebuild and re-enroll after
an update; do not silently replace the payload in place.

**Compatibility exceptions.** JIT, unsigned executable memory, and disabled
library validation widen the attack surface. Enable only the exception the CLI
provably requires. A payload with different entitlements represents a different
review decision.

**Deletion and limits.** Deleting revokes enrollment and related launcher rules
before the bundle is moved to Trash. A Launcher Bundle establishes identity and
integrity. It supplies no trust judgment, safety review, or sandbox.

### Secrets

Secrets is the inventory of Secret Names and their Value sources. The app shows
availability and source labels, but never redisplays stored Values. One Secret
Name can have a Global Value and multiple Project Values.

[![A harmless sample Secret with its hidden Global Value, availability, and Direct Access state](/docs/assets/secrets.png)](/docs/assets/secrets.png)

**Security basis.** Operators can reason about names, sources, selection, and
authority without turning routine administration into Disclosure. Replace is a
write-only operation: enter the new Value, but do not reveal the old one.

**Workflow.** Search by Secret Name, verify the selected Value sources, inspect
availability, and review Direct Secret Access. Use `av save` for terminal entry;
use the app to replace, delete, rename, or change availability. After renaming,
recheck scripts, Gates, and integrations that requested the old name.

**Destructive changes.** Deleting the final Value removes the Secret and its
Direct Rules. A rename changes the requested name and can break consumers. These
actions do not remove copies already received by Targets or stored elsewhere.

**Limits.** Availability is not authorization, and a Secret Name is not a
credential type. Automic Vault does not infer that two differently named Values
are equivalent or rotate an external credential when a stored Value is replaced.

### Active Proxies

Active Proxies lists live proxy sessions with Target, PID, authorized Secret
Names, start time, request count, allowed origins, and individual requests.

[![Harmless live proxy session for a sleep process and sample Secret Name](/docs/assets/active-proxy.png)](/docs/assets/active-proxy.png)

**Security basis.** `av proxy` gives the Target random Secret References and a
session Proxy Credential instead of raw Values. Destination rules are created
only after approval and stay in memory, scoped to the session and origin.

**Workflow.** Confirm the Target and Secret Names in the session Approval, watch
origins appear as the Target uses them, and terminate the session when the task
ends. An unexpected origin is a reason to stop and investigate, not a prompt to
approve broadly.

**Termination.** Terminating ends the registered session, references, Proxy
Credential, and memory-only rules. It does not recall a bearer credential from a
destination that already received it or terminate unrelated Target state.

**Limits.** A Target may bypass configured proxies or open another network path.
Proxying narrows delivery and supports origin-specific decisions; it is not
network containment.

### Authorization History

Authorization History records recent allowed and denied requests with decision,
decision source, command, reason, Verified Launcher, Secret Names and selected
sources, Gate Client, Target, runtime, and working directory.

[![Authorization History filtered to a complete sample proxy decision](/docs/assets/authorization-history.png)](/docs/assets/authorization-history.png)

**Security basis.** A decision without its inputs is not explainable. History
keeps enough of the request envelope to answer why a rule matched, why a human
was asked, and which Value source was selected. An allowed Secret Use is persisted
and verified before release.

**Workflow.** Filter by Tool, launcher, command, Secret Name, or decision. Compare
the **Decision source** and reason with current Gate policy. For a denial, fix the
first mismatched invariant: Target, runtime, launcher, Value source, or operation.
Do not widen every rule.

**Assurance boundary.** History is local and bounded. It is not append-only,
tamper-proof, remotely replicated, or guaranteed to contain every event after an
administrator changes local state. Export security evidence elsewhere when the
audit requirement exceeds this local operator record.

### Doctor

Doctor verifies the installed protected route: ownership, launchers,
dependencies, Target selection, exact file content, permissions, configuration,
and PATH precedence. Healthy Tools disappear from the problem list; failures
include a reason and remediation.

[![Doctor with no unresolved installation problems](/docs/assets/doctor.png)](/docs/assets/doctor.png)

**Security basis.** Policy is only as strong as the route that reaches it. A
correct Gate cannot protect a command if PATH resolves to an unprotected binary,
a launcher is writable, or the expected credential remains in plaintext.

**Workflow.** Run `av doctor` after installation, hardening, Tool updates, PATH
changes, and policy failures. Use `av doctor TOOL --json` in diagnostics, but
present the human remediation before changing ownership or files.

**Limits.** Doctor checks known invariants for supported Tools. It is not a
malware scan, filesystem integrity monitor, code review, or proof that every
process on the Mac is healthy.

### Settings

Settings controls human Approval routes, feedback for automic authorization,
retained launcher provenance, GPG Signing, `av list` policy, and version/runtime
information. Each control changes a different boundary; enabling one does not
implicitly enable another.

Use Settings after reading the corresponding section below. Security-sensitive
changes require Approval or system authentication where the control demands it.

## Approval and authority

### Touch ID Approval

Touch ID Approval authorizes an exact request on the Mac with a fresh biometric.
It accepts neither the login password nor Apple Watch fallback, and pointer or
keyboard automation cannot activate the allow action.

[![Touch ID Approval disabled, with its explicit local-authority guarantee](/docs/assets/touch-id-approval.png)](/docs/assets/touch-id-approval.png)

**Why it exists.** A local approval button can share the same input surface as an
agent. Fresh Touch ID supplies a human gesture the agent cannot synthesize while
keeping the decision at the Local Execution Boundary.

**Failure modes.** Touch ID availability, enrollment, lockout, and hardware state
can make Approval unavailable. Disabling the setting returns to the configured
non-biometric route; it does not create a password fallback inside Touch ID
Approval.

### iPhone Approval

An eligible iPhone on the same iCloud Keychain account can carry human Approval
while the Mac remains the Local Execution Boundary.

[![iPhone Approval disabled with physical-separation guidance](/docs/assets/iphone-approval.png)](/docs/assets/iphone-approval.png)

**Security basis.** When an eligible phone route is enabled, the Mac exposes no
local pointer or keyboard allow action. The phone requires Face ID or Touch ID.
iPhone Mirroring and Show on Mac are treated as paths that can expose controls to
an agent; Approval is unavailable through those surfaces.

**Recovery.** Recovery uses system authentication, rotates the account key, and
invalidates registered phones and Macs. Treat recovery as a security event and
re-enroll only devices you control.

**Availability.** Network, relay, iCloud Keychain, device lock, and biometric
state can prevent the phone from carrying Approval. Unavailability is not a
reason for the Mac to manufacture a weaker local allow action.

### Automic Authorization feedback

Policy-authorized operations can show a notification, flash the menu bar, or
show nothing. This controls feedback, not authority.

[![Automic Authorization feedback options with Flash Menu Bar selected](/docs/assets/automic-authorization.png)](/docs/assets/automic-authorization.png)

Authorization History remains populated in every mode. Approval prompts and
policy-denial notices are unaffected. Choose quieter feedback only after the
team knows where to inspect History; silence is not an audit control.

### Temporary Access Grants

For a supported agent workflow, the Approval menu can grant ten minutes of
memory-only **Write Access** instead of approving only once.

[![A GitHub write request whose approval menu can issue a task-scoped temporary grant](/docs/assets/temporary-access-grant.png)](/docs/assets/temporary-access-grant.png)

The grant binds to the exact Tool-specific Gate, Verified Launcher, accepted
runtime, and Agent Task Context. It excludes Direct Access, Secret mutation,
Disclosure, elevated operations, and unknown operations. The task label narrows
matching but is forgeable context, not identity. The Verified Launcher and live
request checks remain essential.

End a grant from the menu bar when the task finishes. Grants expire after ten
minutes and disappear on app restart. A grant cannot retroactively authorize a
request outside its captured scope.

### Detached Processes

Detached Processes controls **Retained Launcher Provenance**: whether an eligible
live descendant may keep the verified launcher chain after its original parent
exits.

[![Detached Processes off by default with the authority-extension warning](/docs/assets/detached-processes.png)](/docs/assets/detached-processes.png)

**Security tradeoff.** Enabling extends authority after the observed parent
chain disappears. Same-user code injection can pass that retained authority to
injected code. An enrolled Launcher Bundle payload is one unit for this setting.

**Scope.** Retention is execution-scoped. It keeps neither an old authorization
decision nor blanket authority for new processes or Gates. Enabling requires
Approval; disabling is immediate. Leave it off unless a real daemon or detached
worker cannot preserve the original launcher chain another way.

### GPG Signing

GPG Signing stores an armored OpenPGP private key in Secret Custody and routes
Git through `av-gpg` and `av gpg-sign`. Git receives a detached signature, never
the private key.

[![GPG Signing Execution Gate with exact launcher overrides set to Allow Signing](/docs/assets/gpg-signing.png)](/docs/assets/gpg-signing.png)

```sh
git config --global gpg.program av-gpg
git config --global gpg.format openpgp
git config --global commit.gpgSign true
```

Settings can import a key or generate an alternate EdDSA key. The private key is
never displayed; the public key can be copied. Alternate access can be limited
to exact Verified Launchers. The Execution Gate offers **Approval Required** and
**Allow Signing**. Approval binds to the payload SHA-256; `av gpg-sign` reads at
most 16 MiB and returns GnuPG-compatible status plus the detached signature.

**Limits.** A valid signature proves possession of the signing authority for
that payload, not that the commit is safe or reviewed. Protect Git configuration
and verify the repository and payload shown by the workflow.

### Secret Name Access

Exact Verified Apps may run `av list` without an Approval window; all other apps
require Approval.

[![Secret Name Access with two exact verified apps allowed to run av list](/docs/assets/secret-name-access.png)](/docs/assets/secret-name-access.png)

This capability lists Secret Names only. It does not read, change, apply, or
disclose Values and grants no Direct Access. Remove an app when its listing use
ends; a similarly named or newly signed app does not inherit the exact rule.

### About and menu bar

About reports the running version and GUI PATH captured before shell startup.
Use both when diagnosing a mismatch between the app and an interactive shell.

[![About showing Automic Vault 3.16.0 and the pre-shell GUI PATH](/docs/assets/about.png)](/docs/assets/about.png)

The menu bar opens the main window, checks for updates, quits the service, and
surfaces live Secret Uses and Temporary Access Grants without displaying Values.
Quitting ends memory-only grants and proxy state; it does not undo operations or
revoke Values already delivered to Targets.

## Secrets, Values, and selection

```sh
av save GH_TOKEN
av save --project-directory=. GH_TOKEN
av save --project-directory=/absolute/project AWS_PROFILE
```

### Saving safely

A Secret Name is a letter or underscore followed by letters, digits, or
underscores. `av save` canonicalizes an existing Project Directory, rejects the
filesystem root, reads one hidden non-empty Value from `/dev/tty`, trims its line
ending, and restores terminal echo even on failure. It does not read stdin, so a
pipeline neither supplies a Value nor provides a safe import mechanism.

Save the replacement before deleting the old credential. Test a harmless read
through the protected route, inspect History, then remove the plaintext source.
For a supported Tool, prefer its hardener because the hardener knows the native
credential format and can validate the migration.

### Value selection

For each requested name, Automic Vault selects the nearest Project Value at or
above the physical canonical working directory on the same filesystem. If none
matches, it selects the Global Value. The selection happens before policy so the
Authorization Request can identify the chosen source.

Project Directory is a selector, not project identity, a repository trust signal,
or an authorization boundary. Symlinks and logical shell paths do not create a
second identity. A selected Value read failure never falls back to a broader
Global Value; fallback after failure could silently substitute the wrong account.

### Availability

Availability is independent of authorization. **When Unlocked** requires an
unlocked Keychain. **Available While Locked** permits an already-authorized app
to use the Value after the first unlock following boot. Neither setting grants a
request, widens a Gate, or bypasses Approval.

### Direct Secret Access

The Direct Secret Gate binds exact Secret Names to one Verified Launcher, but is
broad with respect to Target and arguments. It permits Secret Application only;
it does not list, mutate, or disclose Values. Prefer a Tool-specific Gate whose
classifier understands read, write, host, registry, or other operation semantics.

## Access Levels

| Access Level | Authority |
| --- | --- |
| Approval Required | Every matching request needs human Approval. |
| Read Only | Apply Secrets only to operations the Tool-specific Gate classifies as read-only. |
| Read & Update | Homebrew-only authority for reads and the supported update path. |
| Local Write | Permit supported local writes without broader remote authority. |
| Write Access | Permit write operations recognized by that Tool-specific Gate. |
| Full Access | Strongest supported Gate authority, potentially including elevated Application or Disclosure where explicitly defined. |
| Direct Access | Apply exact names through the Direct Gate for one Verified Launcher; no Target or argument classifier. |

Access Levels are Gate vocabulary, not interchangeable global roles. **Write
Access** for GitHub and **Write Access** for another Tool are evaluated by
different classifiers. Unknown operations fail closed or require Approval rather
than inheriting the nearest-sounding label.

New Secret Gates default to Read Only; GPG Signing to Approval Required;
Homebrew to Read & Update; Direct access to Approval Required.

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

### Reentrant Blessed Scripts

A reentrant Blessed Script pauses deterministic work for agent judgment, then
resumes through fixed entry points under the same Blessing. See
[Reentrant Blessed Scripts](../reentrant-scripts/) for prompt handoffs,
capability design, Secret exposure, state, validation, and retries.

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

## Reentrant Blessed Scripts

A reentrant Blessed Script is a workflow pattern built from an ordinary
[Blessing](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md#blessing).
The script performs deterministic work until it needs judgment, prints a prompt,
and exits. An agent supplies the requested input and invokes a fixed entry point
to continue.

Automic Vault evaluates each invocation against the same Script Declaration and
makes a new Authorization Decision. An earlier invocation grants no authority
to the next one. The Blessing also cannot carry shell state, environment
variables, or open file descriptors across the gap.

Use reentry when a workflow needs bounded judgment, such as writing release
notes, choosing among reviewed deployment targets, or classifying a failure.
Keep a deterministic workflow in one invocation when no judgment is required.

### Build a small state machine

Give the script a short list of entry points. Each entry point should accept a
validated operation identifier such as a release version or deployment ID.
Reject unknown actions and extra arguments.

```sh
SELF="${AV_SCRIPT_PATH:-$0}"
ACTION="${1:-continue}"
VERSION="${2:-}"

[[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || {
  echo "usage: $SELF {continue|agent:github-context|agent:cdn-status} VERSION" >&2
  exit 64
}

case "$ACTION" in
  agent:github-context) github_context ;;
  agent:cdn-status) cdn_status ;;
  continue) continue_release ;;
  *) echo "error: unknown action: $ACTION" >&2; exit 64 ;;
esac
```

Use `AV_SCRIPT_PATH` when the script prints its own reentry command. Automic
Vault sets it to the canonical source path while executing the verified
snapshot. `$0` may point at `/dev/fd/N` and will not provide a stable command
for the agent.

Every invocation starts a new process. Store required non-secret state in a
protected run directory or recover it from the destination service. Do not rely
on the previous shell process.

### Return the prompt to the agent

Print the handoff prompt to standard output. An agent that invoked the script
through a terminal receives that output in the command result, so the script
does not need an agent-specific API or MCP server. Send diagnostics to standard
error so a wrapper can distinguish them from the prompt.

Exit with a documented nonzero status after printing the prompt. Status 75,
`EX_TEMPFAIL` on macOS, tells a caller that the operation paused before
completion. An exit status of zero can cause a parent task to report success and
discard the pending handoff.

Long command output may be truncated. After creating and validating the protected
run directory, save the same prompt there and print its path as the last line:

```sh
agent_prompt() {
  umask 077
  local prompt="$RUN_DIR/next.md" tmp
  tmp="$(mktemp "$RUN_DIR/.next.XXXXXX")"

  cat >"$tmp" <<EOF
Write concise release notes for $REPOSITORY $VERSION to:
  $NOTES

For recent GitHub context, run:
  "$SELF" agent:github-context "$VERSION"

For current CDN state, run:
  "$SELF" agent:cdn-status "$VERSION"

Do not run gh or aws outside these entry points. Do not include Secret Values.
Resume with:
  "$SELF" continue "$VERSION"
EOF

  mv -f -- "$tmp" "$prompt"
  cat "$prompt"
  printf '\nPrompt saved at: %s\n' "$prompt"
  exit 75
}
```

If a human launched the script, they can paste the printed block into the agent
conversation. If the agent launched it, tell the agent in the initial prompt to
treat status 75 and the script's output as the next task.

### Craft the initial agent prompt

The initial prompt should establish the workflow boundary before the agent runs
anything. Include:

- the goal and the exact first command;
- the working directory and immutable operation identifier;
- the rule that the Blessed Script owns gated Tools and Secret Use;
- the status-75 handoff protocol and the required resume behavior;
- stop conditions for an unexpected prompt, state mismatch, or denied request.

For example:

```text
Prepare release 1.2.3 from the repository root.

Start by running:
  ./scripts/release continue 1.2.3

The Blessed Script owns all gh and aws operations. Do not run those Tools
directly. If the script exits 75, follow the prompt it prints, write only the
requested output file, then run the exact resume command from that prompt.
Stop and report the output if the script reports a state mismatch, requests a
different version, or names an entry point not listed in its first prompt.
```

Avoid broad requests such as “finish the release.” A broad request invites the
agent to search for another route when the script pauses or denies an operation.
The initial prompt should make the script the only authority-bearing interface
for the workflow.

### Craft each handoff prompt

A handoff prompt should stand on its own. Agent context can be compacted or lost
during a long task. Include the operation identifier and repeat the boundary
that matters for the next step.

Name these details:

- the exact artifact to produce, including its path and format;
- the decision criteria and size or schema limits;
- fixed context entry points the agent may invoke;
- the exact command that resumes deterministic work;
- commands and data the agent must not access;
- conditions that require the agent to stop instead of guessing.

Keep volatile context out of the prose when the agent can fetch a fresh view
through a fixed entry point. A prompt that embeds yesterday's deployment state
can send the next invocation down the wrong branch.

### Choose capabilities before writing prompts

A Script Declaration lists the Authorization Gates the script may use and the
maximum [Capability](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md#capability)
at each gate. Declare the weakest capability that covers every branch. A
capability is a ceiling; the gate still classifies and authorizes each concrete
operation.

```sh
# --- automic-vault
# capabilities:
#   gh: write
#   aws: read-only
# ---
```

Review capabilities across all entry points. Recovery, cleanup, status, and
retry branches can request more authority than the main operation. Remove a
branch that needs unrelated authority or place it in another Blessed Script.

One write-capable branch raises the declaration ceiling for that gate across the
whole script. Split context gathering from publication when a reviewer should
be able to bless or endorse them independently. A separate read-only script can
serve context while the publishing script retains Approval Required or a narrow
Launcher Endorsement.

Capabilities govern Automic Vault Authorization Gates. Ordinary file reads,
interpreter behavior, and ungated network clients remain outside that boundary.
Keep the script short enough to review and avoid calling alternate Tools that
bypass the declared gates.

### Keep Secret Values away from the agent step

Prefer a Tool-specific Gate over direct environment injection. Tool-specific
Gates can classify the operation and apply only the credential that Tool needs.
Direct `av inject +NAME` places the raw Secret Value in the interpreter's
environment, where script branches and child processes can read it.

End the secret-bearing process before asking the agent for input. The agent then
works between invocations and receives only the prompt, bounded context, and
non-secret state. The next invocation obtains its own Authorization Decision
before Secret Application.

Do not write Secret Values, bearer tokens, proxy credentials, authorization
headers, or complete command environments into prompts or run-state files.
Avoid `set -x`, `env`, verbose HTTP traces, and unfiltered Tool responses in
agent-facing entry points. Select the fields the agent needs and redact output
at its source.

Secret Application gives the Target control of the Value after release. A
Blessing cannot stop an authorized Tool or dependency from logging or returning
it. Choose a narrower Target and operation when the Tool exposes a safer route.

### Inventory what the agent may need later

Walk through the workflow from each pause to the next side effect. For every
agent decision, list the evidence required to make it and decide who supplies
that evidence:

| Need | Safer interface | Avoid |
| --- | --- | --- |
| Recent changes | Fixed subcommand returning bounded commit fields | General shell access for repository discovery |
| Remote release state | Fixed Tool query with selected JSON fields | Arbitrary `gh` or API commands |
| Artifact identity | Script-produced path, size, and digest | Asking the agent to locate “the latest” file |
| Prior failure | Sanitized log or `agent:last-failure` entry point | Debug traces containing environments or headers |
| Resume state | Per-run state plus a fresh remote check | State held only in conversation history |

Long workflows often pause on branches that the happy path never visits. Plan
for a remote object that exists, a CI job that has not finished, an expired
session, a partially uploaded artifact, and a changed local checkout. Give the
agent a fixed inspection command for any case where judgment can help. Make the
script fail with a precise diagnostic when only the operator can resolve the
state.

Context entry points should return the minimum fields required for a decision.
Use fixed repository, account, region, bucket, and query values in the script.
Validate any selector the agent supplies. Do not accept a free-form Tool command
or query language as an argument because that turns a reviewed entry point into
a general capability proxy.

Treat issue bodies, release notes, logs, and remote metadata as untrusted input.
They may contain instructions aimed at the agent. Label them as reference data
in the prompt, trim fields that carry no decision value, and keep their contents
out of shell evaluation.

### Persist non-secret workflow state

Use a run directory keyed by a validated operation identifier. It may contain:

- immutable inputs such as repository and version;
- artifact paths, sizes, and cryptographic digests;
- the current handoff prompt and expected output path;
- verified remote identifiers and completed-step markers;
- sanitized failure details needed for the next decision.

Create the directory with owner-only permissions. Reject symlinks and files
owned by another user. Bound file sizes and write state through a temporary file
followed by an atomic rename. State files are inputs at the next trust boundary;
validate them again when reentering.

Keep Secret Values out of state. Fetch volatile authorization and remote status
again on each invocation. A stored “uploaded” marker does not prove that the
remote object still matches, so compare its digest or immutable identifier
before advancing.

### Validate agent output as untrusted input

Ask the agent to write a fixed file rather than place substantial content in a
command argument. The script controls the path and can enforce file properties
before it reads the content.

Check the expected type, owner, symlink status, byte limit, encoding, and schema.
Apply destination-specific rules, such as an allowed deployment target or
release-note heading. Reject unknown fields when structured output drives a
privileged action.

Pass validated content as data. Use options such as `--notes-file` instead of
shell interpolation. Never `eval`, `source`, or execute agent output. Do not let
an output file choose the next entry point, Tool command, Secret Name, account,
or destination unless the script validates it against a reviewed allowlist.

Recheck local artifacts and remote state after validation. Both can change while
the agent works. Refuse the operation when the fresh state conflicts with the
state the agent used.

### Make resume and retry safe

The `continue` entry point should tolerate interruption after any remote side
effect. Before creating an object, query the destination:

- continue when the object is absent;
- verify and skip when it exists with the expected identity and digest;
- stop when it exists with different contents or ownership.

Use service idempotency keys, conditional writes, and immutable object names
where available. Record a completed step only after checking the remote result.
A retry must not replace a conflicting object to make progress.

Regenerate time-sensitive prompts and context on reentry. Credentials, Approval
eligibility, CI state, signed URLs, and locks can expire while the agent works.
The new invocation should discover that state and either proceed, print another
bounded prompt, or fail closed.

### Example reentry sequence

1. The agent runs `./release continue 1.2.3` from the initial prompt.
2. The script finds no notes, prints the handoff prompt, saves it, and exits 75.
3. The agent invokes the listed context entry points and writes the fixed notes file.
4. The agent runs the exact `continue` command from the handoff prompt.
5. Automic Vault makes a new Authorization Decision. The script validates the
   notes and fresh remote state, then performs the next deterministic step.
6. If the process stops after a side effect, the next `continue` verifies that
   result and resumes without duplicating or overwriting it.

The [full defensive release script](https://github.com/automic-vault/automic-vault/blob/main/docs/examples/reentrant-release.sh)
shows input validation, bounded context commands, digest checks, conditional S3
writes, and idempotent retries.

### Review checklist

- Every action and argument has a fixed, validated shape.
- The initial prompt names the first command and the reentry protocol.
- Each handoff prompt names one output, bounded context, and one resume command.
- The Script Declaration uses the weakest gate capabilities that cover all branches.
- Agent-facing output contains no Secret Values or general Tool access.
- Run-state files contain no credentials and receive trust-boundary validation.
- Agent output stays data and cannot select arbitrary commands or destinations.
- Each side effect has a remote verification and conflict path.
- Repeating `continue` is safe after interruption.
- Unexpected state stops the workflow with a precise diagnostic.

### FAQ

#### How does this differ from telling the agent to call a sequence of scripts?

A reentrant Blessed Script keeps the workflow's control flow in the exact code
reviewed by the Blessing:

- The script evaluates conditions deterministically. The agent supplies bounded
  judgment or data instead of deciding how an `if` statement should branch.
- The script enforces step order and checks preconditions. The agent cannot skip
  a required step or run later steps first.
- One state machine can select different reviewed paths from validated inputs
  and verified external state without asking the agent to assemble a new sequence.

A series of scripts still fits independent steps where the agent should choose
what runs next. Use one reentrant script when order and branch selection belong
in the reviewed automation.

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

`av inject` preserves an existing environment value by default and warns. Remove
the export at its source, or use `--replace-existing-env` only after confirming
that Automic Vault should override it. Do not suppress the warning without
understanding which credential the Target would otherwise receive.

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

This manual was checked against the CLI parser, implementations, app UI,
catalogs, tests, and canonical security documents for 3.16.0. For an installed
build prefer `av --version`, `av help`, `av detectors --json`, and
`av hardeners --json`.

- [CLI source](https://github.com/automic-vault/automic-vault/blob/3.16.0/src/cli/mod.rs)
- [App and CLI source](https://github.com/automic-vault/automic-vault/tree/3.16.0/src)
- [Detectors](https://github.com/automic-vault/automic-vault/tree/3.16.0/src/detectors)
- [Hardeners](https://github.com/automic-vault/automic-vault/tree/3.16.0/src/isotopes)
- [Domain Language](https://github.com/automic-vault/automic-vault/blob/main/docs/domain-language.md)
- [Architecture](https://github.com/automic-vault/automic-vault/blob/main/docs/architecture.md)

Report discrepancies in the [issue tracker](https://github.com/automic-vault/automic-vault/issues).
