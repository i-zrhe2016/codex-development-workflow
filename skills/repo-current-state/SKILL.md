---
name: repo-current-state
description: "Maintain the repository-specific docs/Repo_Current_State.md recovery snapshot and its reconciliation record. Use when verified repository truth materially changes or when the snapshot must be reconciled. Codex performs repository investigation natively; this Skill only defines the snapshot schema, evidence boundary, and update contract."
---

# Repository Current State Contract

Target: `docs/Repo_Current_State.md`.

The file is a compact recovery snapshot of verified repository truth, not a changelog, backlog, plan, test archive, or reasoning trace.

## Required shape

Keep these sections:

- `Last verified`
- `Current Focus`
- `Implemented`
- `In Progress`
- `Known Issues / Failing Checks`
- `Constraints`
- `Architecture Snapshot`
- `Next`

Prefer concise factual bullets and links to canonical detail.

## Evidence boundary

Only write claims supported by current repository evidence such as tracked files, configuration, Git/GitHub state, or authoritative Issues. Omit or explicitly qualify unverified claims.

Do not copy Plan/Ticket bodies, historical change logs, detailed test output, or authorization data into the snapshot.

## Reconciliation record

For every development task, record in the authoritative Issue:

- `Repo Current State: updated — docs/Repo_Current_State.md`, or
- `Repo Current State: no-change — <concrete reason>`.

Update the snapshot only when repository truth materially changed. Do not churn the file for every task.

## Freshness

`Last verified` identifies the branch/change context used for the latest reconciliation. Remove stale statements when evidence no longer supports them.
