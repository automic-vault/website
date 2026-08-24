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
