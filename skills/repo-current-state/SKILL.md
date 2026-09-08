---
name: repo-current-state
description: Maintain a concise, repository-native `docs/Repo_Current_State.md` as the verified current-state memory for an AI-assisted software project. Use when starting work that needs current repo context, after a ticket or meaningful change is completed, before commit/push when repository state changed, or when the user asks to create, refresh, reconcile, or validate the repository current-state document. Verify claims against repository evidence, prevent stale-state drift, and keep history, plans, architecture detail, and approvals out of this file.
---

# Repo Current State

Maintain `docs/Repo_Current_State.md` as a small, factual snapshot of what the repository is true **now**.

## Core Contract

Treat the repository as the system of record and this file as a compact index into that reality.

- Verify important claims against code, tests, configuration, Git state, or other authoritative repository files.
- Do not trust chat history or an existing state file when repository evidence disagrees.
- Rewrite obsolete state instead of accumulating historical entries.
- Keep the file small enough to read at the beginning of an agent session.
- Record uncertainty explicitly. Never fill gaps with guesses.
- Keep implementation history in Git/changelog, architecture rationale in ADRs or architecture docs, and future work in tickets/issues.

## When Reading State

At the beginning of planning or implementation:

1. Read `AGENTS.md` if present.
2. Read `docs/Repo_Current_State.md` if present.
3. Treat its `Last verified` metadata as a freshness hint, not proof.
4. Verify only the facts needed for the current task against the repository.
5. If the state file is materially stale, reconcile it before relying on it for planning.

Do not scan the entire repository just to validate every line. Validate progressively around the current task.

## When Updating State

Update the file after a ticket or coherent work unit has passed the required tests/review and materially changes repository capabilities, constraints, active work, or known failures.

Prefer this order:

`Implement -> Test -> Review -> Update Repo_Current_State.md -> Commit/Push`

Keep the state update in the same coherent commit as the implementation when it documents that change.

Do not update the file for trivial formatting-only edits or changes that do not affect the project state represented here.

## Source Priority

Resolve conflicts in this order:

1. Executed test/build results and observable runtime behavior.
2. Current code and configuration.
3. Git state and the current commit/branch.
4. Architecture/decision documents that are still applicable.
5. Existing `Repo_Current_State.md`.
6. Conversation memory.

If evidence is insufficient, write `Unverified` or omit the claim.

## Required Shape

Create or maintain this compact structure:

```markdown
# Repository Current State

Last verified: <YYYY-MM-DD> @ <commit-or-working-tree>

## Current Focus
- <current milestone, ticket, or "None">

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
- <immediate next ticket/work item, if known>
```

Omit empty bullets. Use `None` only when the absence itself is useful information.

## Section Rules

### Current Focus

Keep one active milestone or work unit when possible. Do not turn this into a roadmap.

### Implemented

Record meaningful capabilities, not every file or function. Remove entries that are no longer true.

Prefer:

- GitHub OAuth login is available through the existing authentication flow.

Avoid:

- Added `oauth.ts`.
- Changed 14 files.

### In Progress

Only list work that has actually started and remains incomplete. Move completed work to `Implemented`; remove abandoned work.

### Known Issues / Failing Checks

Record unresolved, reproducible facts relevant to future work. Include the failing check or symptom when known.

Do not list speculative risks here; put those in review output or tickets.

### Constraints

Record constraints that affect implementation choices now, such as compatibility boundaries, required interfaces, migration restrictions, or dependency limitations.

Do not treat this section as authorization. Never store deploy approval, secret-access approval, spending authority, or other permission grants here.

### Architecture Snapshot

Keep only a few orientation-level facts. Link to `docs/ARCHITECTURE.md`, ADRs, or module docs instead of duplicating detailed design.

### Next

Point to the immediate next ticket/issue when known. Do not duplicate the full backlog or plan.

## Freshness and Drift Control

Always maintain a `Last verified` line.

- If the working tree is clean, use the current short commit SHA when available.
- If the file is updated before the implementation commit, use `working tree` rather than inventing the future commit SHA.
- Use the current date only when actually updating or validating the file.
- If a section cannot be verified, mark the specific item `Unverified` or remove it.

When stale information is found:

1. Verify the current repository truth.
2. Replace the stale entry with the current fact.
3. Remove obsolete completed/in-progress items.
4. Do not preserve stale text merely for historical context.

Git history already preserves the old version.

## Boundaries

`Repo_Current_State.md` is **not**:

- a changelog
- a session transcript
- a research log
- a full architecture document
- a decision rationale archive
- a complete backlog
- a test report archive
- an authorization or approval record

Route those concerns elsewhere:

- history -> Git / `CHANGELOG.md`
- architecture -> `docs/ARCHITECTURE.md`
- rationale -> ADRs / decision docs
- future work -> GitHub Issues / tickets
- test evidence -> CI/test reports
- approvals -> the appropriate external authority or protected workflow

## Size Discipline

Prefer a few hundred tokens of high-value state over exhaustive detail.

- Keep bullets short.
- Collapse duplicated facts.
- Link to detailed docs instead of copying them.
- Remove resolved issues and obsolete constraints.
- Avoid timestamps per bullet, narrative prose, and chronological logs.

If the file grows beyond roughly 150 lines, treat that as a signal that content belongs in more specialized documents.

## Reconciliation Workflow

When asked to refresh or validate the file:

1. Read the existing state file if present.
2. Inspect the minimum repository evidence needed to validate its claims.
3. Identify stale, missing, duplicated, or misplaced items.
4. Rewrite the document to current truth.
5. Update `Last verified`.
6. Re-read the final file for contradictions and scope creep.

Do not create extra state files unless the user explicitly asks.

## Output Behavior

When operating inside a repository, create or update `docs/Repo_Current_State.md` directly when tools permit.

When the user asks only for text, return the complete proposed Markdown content and nothing else.

When reporting completion, state only:

- whether the file was created, updated, or already current
- what evidence was used to verify it
- any items left `Unverified`
