---
name: develop-workflow
description: "Implement, fix, refactor or modify repository content from an executable Slice to Development Complete with focused local validation. Stops before delivery verification, publication, Issue closure and state refresh."
---

# Develop Workflow

Owns **context -> implementation -> Development Complete**.

1. Load only affected files, direct dependencies, relevant tests and repository
   state. Confirm the smallest useful local validation before editing.
2. Apply `AGENTS.md` adaptive scheduling to ready Slices/tasks: choose self or
   delegation, useful concurrency and available agents at runtime. Keep
   overlapping writes, unresolved dependencies and shared interfaces/schemas/
   migrations/config sequential.
3. Where practical, use meaningful failing tests first for behavior changes,
   bugs/regressions, APIs, core logic, data processing or high risk. Validate
   docs/config/dependencies/styling/typos/simple refactors directly; no forced RED.
4. Make the minimum change satisfying acceptance; run focused checks and fix
   clear failures. Refactor only within the Slice after acceptance passes.
5. Integrate each wave before the next; recompute readiness from fresh evidence.
   Wrong design assumptions require re-planning, not patch expansion.

**Development Complete:** acceptance is implemented and local validation passes.
Report Slice, changed files, commands/results, unresolved risks and follow-up work.

`verify-workflow` owns delivery verification breadth; publish/integrate own
commit/push/PR/merge, Issue closure and state refresh. No post-delivery evaluation,
unrelated refactors, formatting sweeps, dependency upgrades or future-Slice work.
