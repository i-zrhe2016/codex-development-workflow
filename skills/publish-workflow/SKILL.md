---
name: publish-workflow
description: "Perform only user-authorized commit, push or PR creation/update for a verified change, through documentation impact, staged redaction and Conventional Commit readiness. Stop at the requested action boundary; never merge."
---

# Publish Workflow

Owns **verified change -> requested publication boundary**. The user decides
commit, push and PR creation/update timing and scope. Commit-only stops after
the commit; push-only stops after the push; creating/updating a PR requires that
action's authorization. A readiness assessment recommends actions but grants
no permission. Local verification may stop normally without publication; waiting
for the user's decision is not BLOCKED. Prior authorization persists within its
stated batch/actions; added feature scope alone does not extend it.

When the user controls the overall flow, publish-workflow may explain the safe
publication sequence and consequences of each boundary, but must not pick
commit/push/PR actions, message scope, review timing or merge readiness for the
user without explicit authorization.

A change may be one functionality or an explicitly planned multi-function batch.
Before publication, every Ticket's acceptance and the batch's relevant
integration/regression checks must pass; any failure blocks the batch. Final
Plan/branch/PR acceptance uses three fresh independent verifiers for the whole
current scope before publication or PR readiness can pass. Expanded
unmerged Plan scope follows `plan-to-ticket`: retain branch/base/PR and evidence,
set Plan `in_progress` and revalidate impacted acceptance plus batch readiness.
The existing PR is not ready for expanded scope until revalidated, the final
three-verifier gate passes and an authorized update succeeds; never create a
per-feature PR.

Invoke applicable capabilities in order for the requested actions:

1. `repo-documentation`: impact check; update canonical docs/index or record no
   documentation change.
2. `repo-current-state`: when the verified change materially affects the compact
   repository recovery truth, update `docs/Repo_Current_State.md` on the same
   Plan branch and include it in the PR-bound commit. If no represented state
   changed, record that no state update is needed. Do not defer required state
   updates to a separate post-merge PR.
3. Before a commit, `data-document-redaction`: stage only the batch's verified
   functionality, tests and documentation, preserving out-of-Plan user changes;
   prefer explicit pathspecs/hunks under `github-push-when-ready`. Scan staged
   files. Proceed only on `pass`, `noop` or recorded no-sensitive-surface skip.
   `findings`/`needs_review` block: sanitize reported files, re-stage/re-scan; fix
   scanner `error` first. Push-only checks the prior staged gate evidence for
   commits being published; do not invent an empty commit or bypass the gate.
4. `github-push-when-ready`: perform only authorized actions, using Conventional
   Commits and its batch commit/PR description rules. For commit-only, suppress
   optional auto-push hooks and use equivalent guarded commit commands; do not
   use a combined commit/push script. Push-only must not create a commit or PR.
   Validate any Plan metadata; persistence is a planning decision, not a
   publication precondition. Return `PR ready` only after an authorized PR
   creation/update succeeds and current-scope checks, including the final
   three-verifier gate, pass.

Report branch, action results and any existing PR URL, then stop at the requested
boundary. No merge, branch deletion or Issue closure (`integrate-workflow`);
no product edits. Failed checks return to `develop-workflow`/`verify-workflow`.
Never weaken branch, redaction, security, permission or release gates.
