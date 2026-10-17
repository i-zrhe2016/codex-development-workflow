Status: in_progress
Branch: docs/intent-first-handoff
Base: main
PR: null
Tickets: [intent-first-handoff-01]

<!-- codex-plan-id: intent-first-handoff -->

# Plan: Intent-first Agent Handoff Contract

## Goal
Put the user's business intent and observable outcome before technical task
details so development agents understand why the work matters.

## Scope and validation
Update only the minimum task contract in AGENTS.md Context Management,
with a README documentation-index link to this required Plan.
Preserve existing context isolation, lazy reading, concise return handoffs,
role, dependency, ownership and checkpoint requirements. Add no agents or
Skills. Record this requirement before implementation; check the focused diff
and whitespace locally. The user subsequently authorized commit, push, PR
creation and merge for this Plan's existing scope.

## Ticket index
- [intent-first-handoff-01](#intent-first-handoff-01)

### intent-first-handoff-01
<!-- codex-ticket-id: intent-first-handoff-01 -->
Title: Lead agent task handoffs with business intent and observable outcome
Status: in_progress
Dependencies: []
Write Ownership: AGENTS.md Context Management minimum task contract; README Plan link
Acceptance:
- The contract lists Intent, Outcome, Scope, Constraints, Acceptance, Context
  and Validation in that order.
- Intent explains why the user needs the work; Outcome describes observable
  change; Constraints identifies interfaces, data structures and behavior to
  preserve.
- Existing role, non-goal, dependency, ownership, branch/base, prerequisite,
  checkpoint and validation information remains represented.
- Outcome describes observable change; Acceptance defines how to verify it.
  Keep entries concise and relevant to the task. Context uses file paths and
  reading entrypoints with brief dependency/checkpoint summaries; Constraints
  may state "No additional constraints" when appropriate.
- No new Agent or Skill is added or invoked; no other repository rules change.
Context: AGENTS.md Context Management; this Plan.
Validation: Review the focused diff and run git diff --check; both must pass.
Evidence Summary: Local implementation and focused review complete; all 51
repository tests pass. Publication and merge now authorized.
No independent verifier dispatched, per the user's explicit
small-change/no-additional-Agent instruction.

## Evidence
- [intent-first-handoff-01] Requirement persisted before implementation edits.
  Initial worktree clean on main. User explicitly requested a small rule-only
  change with no additional Agent or Skill; perform local review directly.
- [intent-first-handoff-01] Local branch creation initially failed because the
  sandbox denied writing .git refs; the approved retry succeeded. No content
  edits were lost.
- [intent-first-handoff-01] Implemented all seven fields in the requested order.
  Focused diff review confirmed original role, Ticket goal, ownership,
  non-goals, dependencies, branch/base, prerequisite/checkpoint and validation
  information is preserved. Only the minimum task contract changed; context
  isolation, lazy reading and return handoffs remain intact. Documentation-only
  change; no runtime tests added or required. git diff --check passed.
- [intent-first-handoff-01] User authorized PR creation and merge for the existing
  scope. Origin/main matches the branch base at 667b4fe. Publication validation
  will run the repository CI commands; no additional Agent or Skill is invoked.
- [intent-first-handoff-01] Publication validation: shell syntax checks passed.
  The literal CI command stopped because this host has no `python` alias;
  reran compilation and tests with Python 3.14.4 via `python3`. Compilation
  passed; 51 tests ran with one failure: the new Plan was not reachable from
  README. Preserve this failure; add only the required documentation-index link
  and rerun the suite. No behavioral scope expansion.
- [intent-first-handoff-01] Publication revalidation PASS: shell syntax and
  Python compilation passed; all 51 regression/contract tests passed in 35.567s
  using Python 3.14.4. README reachability failure is resolved. Focused review
  confirms the seven-field contract and preserved metadata; whitespace checks
  passed. Reviewed the exact publication files; no credentials or secrets found.
