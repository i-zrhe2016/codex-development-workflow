---
name: develop-workflow
description: "Implement or modify repository content from an executable requirement or Slice. Use for feature, bug-fix, refactor, configuration, documentation, or test changes. Make the minimum scoped change, run focused local validation, and stop at Development Complete; do not publish or merge."
---

# Develop Workflow

Take executable work to **Development Complete**.

## Flow

1. Load only the affected files, direct dependencies, relevant tests, current state, and applicable `AGENTS.md`.
2. If several dependency-ready Slices are independent, use the adaptive execution-wave rules in `AGENTS.md`; keep overlapping writes and shared interfaces/config/schema work sequential.
3. Choose the cheapest useful local validation before editing.
4. Use test-first development when a meaningful failing test helps prove behavior or high-risk logic. For docs, config, styling, dependency, typo, and simple refactor work, use focused direct validation instead of ceremonial RED/GREEN.
5. Make the minimum change that satisfies the current Slice.
6. Run focused validation, fix clear in-scope failures, and refactor only after acceptance passes.
7. Recompute dependencies after material results. If implementation reveals a wrong design assumption, stop and return to planning instead of expanding scope.

## Complete when

The Slice acceptance criteria are implemented and focused local validation passes. Report changed files, commands/results, and unresolved risk.

Stop here. Full acceptance verification belongs to `verify-workflow`; commit/push/PR belongs to `publish-workflow`; merge and state reconciliation belong to `integrate-workflow`.
