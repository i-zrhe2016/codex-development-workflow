---
name: develop-workflow
description: "Implement, fix, refactor or modify repository content from an executable Slice to Development Complete with focused local validation. Stops before delivery verification, publication, Issue closure and state refresh."
---

# Develop Workflow

Owns **context -> implementation -> Development Complete**.

When the user controls the overall flow, development executes only the approved
Slice/Ticket scope. It may surface the next workflow step, blockers, risks and
available choices, but must not choose new scope, re-planning, verification,
publication or merge actions for the user.

1. Load only affected files, direct dependencies, relevant tests and repository
   state. Confirm the smallest useful local validation before editing.
2. Follow the role boundary below. The coordinator dispatches ready Tickets;
   the implementation worker executes all assigned Slices in dependency order.
   Keep overlapping writes, unresolved dependencies, shared interfaces/schemas/
   migrations/config and shared test state sequential.
3. Where practical, use meaningful failing tests first for behavior changes,
   bugs/regressions, APIs, core logic, data processing or high risk. Validate
   docs/config/dependencies/styling/typos/simple refactors directly; no forced RED.
4. Make the minimum change satisfying acceptance; run focused checks and fix
   clear failures. Refactor only within the Slice after acceptance passes.
5. The worker reports checkpoints/results; the coordinator integrates each wave
   and recomputes readiness. Wrong design assumptions require re-planning,
   not patch expansion.

## Coordinator and implementation worker

These rules apply even when the target has no `AGENTS.md` (the installer does
not install it); when present, it owns the full scheduling policy.

- Coordinator: do not implement Tickets directly. Dispatch one fresh
  implementation agent per Ticket, including docs/config/test and inline
  one-Slice work; it owns all that Ticket's Slices in dependency order. Never
  reuse across Tickets.
- Dispatched implementation worker: execute the assigned Ticket, including
  local validation; never spawn agents or perform independent delivery verification.
- Codex dispatch must use `spawn_agent` with `fork_turns="none"`; other hosts
  require equivalent fresh agents and independent context. Without that ability,
  report BLOCKED, with no coordinator fallback.
- Hand off only role, current Ticket goal/scope/non-goals, Slice dependencies/
  acceptance, relevant files/ownership, Plan branch/base and verified prerequisite
  results, validation commands and expected summary; no parent conversation or
  unrelated history. Same-Ticket follow-up is allowed; interrupted/failed workers
  require a fresh replacement with verified checkpoints.
- Context isolation does not isolate files. Serialize conflicts or use safe
  ownership with isolated worktrees/returned patches on the shared Plan branch;
  never create Ticket branches. Do not duplicate active worker work.
- After Development Complete, the coordinator uses a separate fresh verifier
  for all Ticket scenarios, never the implementer or another Ticket's verifier.
  Ordinary per-Ticket verification uses one verifier; final Plan/branch/PR
  acceptance later uses three fresh independent verifiers for the whole scope.
  Verification failures return here for fixes, then a new verifier rechecks the
  affected function, retaining prior failure evidence and the flaky-test gate.
  The coordinator owns integration, stage gates and final judgment.

**Development Complete:** acceptance is implemented and local validation passes.
Report Slice, changed files, commands/results, unresolved risks and follow-up work.
It does not trigger commit, push, PR creation/update or merge. After independent
verification, local verified functionality may stop normally pending the user's
publication decision; that wait is not BLOCKED. New scope in an unmerged Plan
requires `plan-to-ticket`'s Plan/Ticket updates before implementation edits.

`verify-workflow` owns delivery verification breadth; publish/integrate own
commit/push/PR/merge, Issue closure and state refresh. No post-delivery evaluation,
unrelated refactors, formatting sweeps, dependency upgrades or future-Slice work.
