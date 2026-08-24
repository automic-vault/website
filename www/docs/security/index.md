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
