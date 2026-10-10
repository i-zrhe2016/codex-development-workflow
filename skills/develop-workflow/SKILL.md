---
name: develop-workflow
description: "Implement, fix, refactor or modify repository content for a persisted Ticket through Development Complete with focused local validation. Stops before delivery verification, publication, Issue closure and state refresh."
---

# Develop Workflow

Owns **context -> implementation -> Development Complete**.

When the user controls the overall flow, development executes only the approved
Ticket scope. It may surface the next workflow step, blockers, risks and
available choices, but must not choose new scope, re-planning, verification,
publication or merge actions for the user.

1. Load only affected files, direct dependencies, relevant tests and repository
   state. Confirm the smallest useful local validation before editing.
2. Follow the role boundary below. Keep unresolved dependencies and overlapping
   writes, shared interfaces/schemas/migrations/config, and shared test state
   sequential.
3. Where practical, use meaningful failing tests first for behavior changes,
   bugs/regressions, APIs, core logic, data processing or high risk. Validate
   docs/config/dependencies/styling/typos/simple refactors directly; no forced RED.
4. Make the minimum change satisfying Ticket acceptance; run focused checks and
   fix clear failures. Keep all work within the persisted Ticket.
5. The worker reports checkpoints/results; the coordinator integrates each wave
   and recomputes readiness. Wrong design assumptions require re-planning,
   not patch expansion.

## Ticket owners and workers

These minimum execution rules apply even without `AGENTS.md`; when present, it
owns the full scheduling policy.

- Main agent: own requirements, dependencies, scheduling, integration, stage
  gates and final judgment. Directly dispatch one fresh implementation owner
  per Ticket, including docs/config/test; also dispatch
  independent verifiers and fresh repair implementers.
- Ticket owner: retain context across the Ticket and local repairs. Validate
  changes and report at integrated-wave and Development
  Complete checkpoints. Owners never spawn agents or perform independent
  acceptance verification.
- Optional module assistants may work only to fixed interfaces with
  non-overlapping file and shared-test-state ownership. Parallel writes require
  isolated workspaces and returned patches for main integration. Dependent
  Tickets may prepare read-only, but delivery writes wait for prerequisite
  independent PASS.
- Count all active agents against actual host capacity. The repository sets no
  fixed concurrency cap or total/lifetime agent quota. A direct main-to-worker
  dispatch requires two available slots; queue when exhausted. No leaf-slot
  reservation applies. Workers never spawn agents.
- Codex main agent, before dispatch: identify **this active entrypoint's** path
  from the explicit user-selected/dispatched path first, otherwise its loaded
  catalog location (resolve aliases). Project `.agents/skills` copies are valid
  installed Skills. Read only the catalog-discovered
  `codex-development-workflow/SKILL.md` sibling under that same installation root
  (the parent of this Skill directory). Duplicate names do not authorize
  switching to another, possibly stale, global copy. Apply that root's **Codex
  worker model routing** policy to each direct dispatch. Ambiguous active-copy
  association, missing/unreadable sibling, absent routing section or unsupported
  settings blocks dispatch. Inspect named-role settings only when selecting a
  role; do not explore generic/global defaults. Dispatched workers do not route
  models. Claude selection is unchanged.
- For every Codex dispatch, explicitly request the selected model and effort
  with `fork_turns="none"`; other hosts need equivalent fresh independent
  workers. If unavailable, report BLOCKED without main-agent fallback. Requested
  settings are dispatch metadata, not proof of runtime identity; report observed
  identity only when exposed.
- Keep the main agent long-lived and thin. Hand off only role, current
  Ticket goal, scope/non-goals, dependencies and acceptance, files and
  ownership, Plan branch/base, verified prerequisites and validation summary.
  Do not include parent conversation or unrelated history. Replace interrupted
  workers from verified checkpoints and preserve failure evidence/counts.
- Serialize dependencies and conflicting/shared-state work. Never create
  Ticket branches or switch a directory used by active workers. Integrate waves
  and recompute readiness. Verification failures return to implementation,
  followed by a new verifier for affected functionality. Preserve flaky-test
  evidence and the Test Quality Gate.
- The initial implementation failure does not count as a repair round. After
  two consecutive failed same-problem repair rounds, stop Luna writes to that
  problem and dispatch a fresh Sol/high repair implementer. Later unrelated work
  remains on Luna. Final Plan acceptance is a separate fresh verifier, except
  one NEW verifier may satisfy Ticket and final gates for a one-Ticket Plan only
  when full scope, artifact/version, configuration and deployment surface match
  exactly. The main agent owns the Test Quality Gate and stage decision.
- Record durable Ticket Issue checkpoints at integrated waves, Development
  Complete, acceptance failures, and pause/retirement. A required Issue write
  failure is BLOCKED. Do not create per-step acknowledgements or gates.

**Development Complete:** acceptance is implemented and local validation passes.
Report Ticket, changed files, commands/results, unresolved risks and follow-up work.
It does not trigger commit, push, PR creation/update or merge. After independent
verification, local verified functionality may stop normally pending the user's
publication decision; that wait is not BLOCKED. New scope in an unmerged Plan
requires `plan-to-ticket`'s Plan/Ticket updates before implementation edits.

`verify-workflow` owns delivery verification breadth; publish/integrate own
commit/push/PR/merge, Issue closure and state refresh. No post-delivery evaluation,
unrelated requirements, refactors, formatting sweeps or dependency upgrades.
