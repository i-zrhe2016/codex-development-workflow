---
name: repo-current-state
description: "Maintain docs/Repo_Current_State.md as a concise verified snapshot of repository truth. Use to create, read, refresh, reconcile, or validate current project state. Verify claims against repository evidence, remove stale facts, and keep history, detailed architecture, backlog, test archives, and approvals elsewhere."
---

# Repo Current State

Maintain `docs/Repo_Current_State.md` as small current-state memory, not history.

## Rules

- Repository evidence outranks the state file and conversation memory.
- Verify only facts needed for the current task; do not scan the whole repository by default.
- Rewrite stale facts instead of appending history.
- Record uncertainty as `Unverified` or omit it; never guess.
- Keep Plan/Ticket detail in GitHub Issues, history in Git/changelog, architecture detail in architecture docs/ADRs, and test evidence in test/CI output.
- Read the file at planning/implementation start when present. Refresh after merge/cleanup/default-branch sync only when project capabilities, constraints, active work, or known failures materially changed.

## Evidence priority

1. Executed tests/build/runtime behavior
2. Current code/configuration
3. Git state/commit
4. Applicable architecture/decision docs
5. Existing state file
6. Conversation memory

## Shape

```markdown
# Repository Current State

Last verified: <YYYY-MM-DD> @ <commit-or-working-tree>

## Current Focus
- <active Plan/Ticket or None>

## Implemented
- <important capability that exists now>

## In Progress
- <started but incomplete work>

## Known Issues / Failing Checks
- <specific unresolved fact>

## Constraints
- <current implementation constraint>

## Architecture Snapshot
- <few orientation facts; link detailed docs>

## Next
- <immediate Issue/work item link if known>
```

Omit empty bullets. Keep entries factual and short.

## Refresh flow

1. Read existing state if present.
2. Inspect the minimum evidence needed to validate relevant claims.
3. Replace stale/misplaced content and remove obsolete entries.
4. Update `Last verified`.
5. Re-read for contradictions.

For a clean tree, use the current short commit when appropriate. For an update that is itself uncommitted or would be self-referential, use `working tree` or the already-verified base/parent commit instead of inventing a future/self SHA.

If refreshing this tracked file after a merge requires a new edit, publish that edit through a new branch/PR; never write it directly to the default branch.

Keep the file compact; if it grows toward ~150 lines, move detail to its canonical document.
