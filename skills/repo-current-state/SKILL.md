---
name: repo-current-state
description: "Maintain a concise, verified snapshot of repository facts in docs/Repo_Current_State.md. Use to read, refresh, create, reconcile, or validate current-state documentation. Exclude history, backlog, detailed architecture, and approvals."
---

# Repo Current State

Keep `docs/Repo_Current_State.md` a small index of repository truth now. Verify claims against code, tests, configuration, Git, or authoritative documents. Evidence takes precedence over conversation and existing notes. Replace obsolete facts, mark uncertainty, and never guess.

## Read and update

At work start, read relevant repository instructions and the state file if present. Treat `Last verified` as a freshness hint, then check only the facts relevant to the task. A whole-repository audit is unnecessary unless requested.

Refresh the snapshot when capabilities, constraints, active work, or known failures materially change. Include a meaningful update with the same change that it describes. Skip formatting-only changes and other work that does not affect represented facts.

Resolve conflicting evidence in this order: executed checks and observable behavior; current code and configuration; Git state; applicable architecture or decision documents; the existing snapshot; conversation memory. Omit claims that cannot be verified or mark them `Unverified`.

## Shape

Use the sections that provide useful orientation, omitting empty sections:

```markdown
# Repository Current State

Last verified: <YYYY-MM-DD> @ <short-commit-or-working-tree>

## Current Focus
## Implemented
## In Progress
## Known Issues / Failing Checks
## Constraints
## Architecture Snapshot
## Next
```

Keep Current Focus to the active work unit rather than a roadmap. Record existing capabilities under Implemented, incomplete started work under In Progress, and unresolved reproducible issues under Known Issues. Constraints describe technical or compatibility limits, not permissions. Architecture Snapshot contains only a few orientation facts and links to detail. Next may link to the immediate work item when one exists.

## Freshness and scope

Use today's date only when actually refreshing or validating. Use the short commit when the clean tree and evidence support it; before a commit, use `working tree`, never a guessed future hash. Remove stale facts rather than retaining a chronology. Keep history in Git, detailed architecture in focused docs, future work in the repository's tracker, and test results in their natural reports.

Prefer a few hundred tokens. Roughly 150 lines is a signal to move detail to specialized documents. Completion reports state whether the snapshot changed, what evidence was checked, and any remaining unverified facts.
