---
name: repo-current-state
description: "Maintain verified, concise repository memory in docs/Repo_Current_State.md. Read at work start; create, refresh, reconcile, or validate on request; include material state changes in the same PR as the work. Exclude history, plans, detailed architecture, and approvals."
---

# Repo Current State

Keep `docs/Repo_Current_State.md` a small index of repository truth **now**.
Verify claims against code, tests, configuration, Git, or authoritative files;
repository evidence overrides chat and existing state. Replace obsolete facts,
record uncertainty, and never guess.

## Read and update triggers

At planning/implementation start, read `AGENTS.md` and the state file if present.
`Last verified` is a freshness hint, not proof: progressively verify task-relevant
facts, reconciling material staleness before relying on them. No whole-repository
scan merely to validate every line.

Refresh when capabilities, constraints, active work, or known failures materially
change, after the Plan/coherent work unit passes required tests and before the
same Plan PR is created or updated. State is part of the publication batch, not
a post-merge follow-up:

`Implement Plan -> Test -> Update Repo_Current_State.md if represented state changed -> Redaction -> Commit/Push -> Create/Update Plan PR -> Automatic Review -> Fix loop if needed -> Merge once -> Cleanup -> Validate merged state`

Do not create a separate post-merge state-only branch/PR for facts that belong
to the delivered work; return missing state updates to the Plan branch before
merge. Never commit state changes directly to the default branch. Skip
formatting-only or other changes that do not affect represented state.

## Evidence priority

Resolve conflicts in descending order:

1. Executed tests/builds and observable runtime behavior.
2. Current code/configuration.
3. Git state and current commit/branch.
4. Still-applicable architecture/decision documents.
5. Existing state file.
6. Conversation memory.

Mark insufficiently evidenced items `Unverified` or omit them.

## Shape and section rules

```markdown
# Repository Current State

Last verified: <YYYY-MM-DD> @ <commit-or-working-tree>

## Current Focus
- <current Plan milestone, Ticket, or "None">

## Implemented
- <important capability that exists now>

## In Progress
- <work actually started but not complete>

## Known Issues / Failing Checks
- <specific unresolved issue or failing check>

## Constraints
- <current technical or compatibility constraint>

## Architecture Snapshot
- <only the high-level facts needed to orient an agent>
- See `<path>` for detailed architecture when applicable.

## Next
- <link to the immediate next GitHub Issue/work item, if known>
```

Omit empty bullets; use `None` only when absence is useful information.

- **Current Focus:** preferably one active milestone/work unit, never a roadmap.
- **Implemented:** meaningful existing capabilities, not files/functions changed;
  remove facts no longer true.
- **In Progress:** only started, incomplete work; move completed capabilities to
  Implemented and remove abandoned work.
- **Known Issues / Failing Checks:** unresolved reproducible facts relevant to
  future work, with check/symptom when known. Speculative risks belong in review
  output or Tickets.
- **Constraints:** current compatibility, interface, migration, dependency, or
  other implementation restrictions; never permission grants (deployment,
  secrets, spending, etc.).
- **Architecture Snapshot:** a few orientation facts; link architecture, ADR,
  or module docs for detail.
- **Next:** immediate Plan/Ticket Issue link, not a backlog or full Plan.

## Freshness and reconciliation

Always maintain `Last verified`:

- Use the current short SHA when available, the tree is clean, and the verified
  commit did not change this file.
- For an update before the implementation commit, use `working tree`, never a
  guessed future SHA. Keep that marker in the update's commit; its own SHA is
  self-referential. Later clean-tree verification may substitute the actual SHA.
- A PR-bundled state update may retain `working tree` or the verified base/parent
  SHA when the final commit SHA is not yet knowable, never a guessed future SHA.
- Use today's date only on actual update/validation. Mark specific unverifiable
  items `Unverified` or remove them.

On refresh/validation: read existing state; inspect minimum evidence; identify
stale, missing, duplicate, or misplaced facts; replace with current truth; remove
obsolete completed/in-progress items; update metadata; re-read for contradictions
and scope creep. Git preserves history; do not keep stale text for context or
create additional state files without an explicit request.

## Boundaries and size

Keep history in Git/`CHANGELOG.md`, detailed architecture in
`docs/ARCHITECTURE.md`, rationale in ADRs/decision docs, future work in GitHub
Issues, test evidence in CI/test reports, and approvals in their external
authority/protected workflow. No session transcripts, research logs, or archives.
With `plan-to-ticket`, Issues are the sole durable Plan/Ticket authority: links
are allowed; duplicated backlog, metadata, or progress are not.

Prefer a few hundred tokens, short bullets and links; collapse duplicates and
remove resolved issues/obsolete constraints. Avoid per-bullet timestamps,
narratives, and chronological logs. Roughly 150 lines signals content belongs
in specialized documents.

## Output

In a repository, create/update the file directly when tools permit. For text-only
requests, return only the complete proposed Markdown. Completion reports contain
only created/updated/already current status, verification evidence, and remaining
`Unverified` items.
