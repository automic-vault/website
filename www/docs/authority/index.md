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
