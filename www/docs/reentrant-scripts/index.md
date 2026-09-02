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
