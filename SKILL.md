---
name: codex-development-workflow
description: "Entry point for repository development. Route each request to the stage workflow that owns it — plan, develop, verify, publish, or integrate — or run the full orchestration end to end when a complete delivery is explicitly authorized. Shared invariants: the risk-aware Test Quality Gate, the staged redaction gate, Conventional Commits, and never weakening a branch, security, permission, or release gate to reduce friction."
---

# Development Workflow

This skill is the entry point for repository development. It routes a request
to the stage workflow that owns it, and it carries the invariants that apply
whichever stage runs. An explicitly authorized end-to-end delivery may instead
run the full orchestration described here.

The main agent owns requirements, architecture, the planning and persistence
decision, dependency ordering, adaptive execution-wave scheduling, integration,
delivery gates, process evaluation, and final judgment. Stage workflows decide
*when* a stage runs; capability skills define *how* it is performed. Agent
assignment is an execution choice inside a stage, never a replacement for the
stage topology or its gates.

## Routing

| Request | Stage workflow |
|---|---|
| Plan, design, investigate, or decompose a requirement before code changes | `plan-workflow` |
| Implement, fix, refactor, or otherwise change repository content | `develop-workflow` |
| Verify, validate, check acceptance criteria, or confirm a branch before publication | `verify-workflow` |
| Commit, push, open or update a pull request, or prepare a branch for review | `publish-workflow` |
| Merge, clean up, close a Plan or its Tickets, or reconcile repository state | `integrate-workflow` |
| An explicitly authorized end-to-end delivery | the full orchestration below |

Feature, Bug, Refactor, and Docs are profiles of these stages, not additional
workflows: they change the verification breadth and whether a plan is persisted,
and they add no new stage or directory.

Read the routed stage's `SKILL.md` and follow it. Each stage states its own
responsibility and its explicit non-responsibility; do not let a stage perform
another stage's work. When the request spans several stages and a complete
delivery is authorized, use the full orchestration.

## Shared invariants

These hold in every stage, including the full orchestration:

- Branch, redaction, security, permission, and release gates are never weakened
  to reduce friction.
- One commit carries one purpose, and its message follows Conventional Commits
  1.0.0.
- The staged redaction gate runs before every commit; see
  `## Redaction gate contract`.
- PASS requires the risk-aware **Test Quality Gate**, not merely a green focused
  test run.
- Verified state is reconciled after merge, not before it.
- Do not implement future work, unrelated refactors, formatting sweeps, or
  dependency upgrades inside another change.

## Fixed control flow, adaptive execution

Use a **static control plane / dynamic execution plane** model.

The control plane is fixed:

```text
plan-workflow -> develop-workflow -> verify-workflow
              -> publish-workflow -> integrate-workflow
```

When the full orchestration is authorized, the stage order, ownership,
completion contracts, branch/PR discipline, Test Quality Gate, redaction gate,
and merge boundary are invariant. Multi-agent execution may not skip, reorder,
or redefine them.

Inside the stage that currently owns the work, the main agent decides the
execution topology at runtime. It may execute work itself, delegate one bounded
task, or run several dependency-ready tasks concurrently when their ownership
boundaries are disjoint. The host concurrency limit is a ceiling, not a target.

For each scheduling wave:

1. Build the ready set from tasks whose dependencies are satisfied.
2. Exclude tasks with unresolved file, interface, schema, migration, or shared
   configuration overlap.
3. Choose the smallest useful mix of main-agent work and delegated work based
   on speed, context isolation, independent evidence, implementation quality,
   risk, and available concurrency.
4. Select the best available built-in or project-defined subagent from the task
   contract and the agent description; do not hard-code task classes to names.
5. Integrate material results before crossing the current stage gate.
6. Recompute the ready set after each material result, failure, dependency
   change, or integration step.

Do not pre-assign the whole Plan to agents. A subagent may produce findings,
implementation, or verification evidence, but it may not change the workflow
topology, advance a stage gate, publish or merge on behalf of the main agent, or
override the main agent's final judgment. Follow the adaptive scheduling policy
in `AGENTS.md`.

## Full orchestration

Use this only when the user explicitly authorizes a complete end-to-end
delivery. Otherwise run the routed stage alone.

```text
Requirement
    -> plan-workflow       (understand, design, decompose, persistence decision)
    -> develop-workflow    (implement to Development Complete)
    -> verify-workflow     (verification scope, level, and conclusion)
    -> publish-workflow    (documentation impact, redaction, commit, push, PR ready)
    -> integrate-workflow  (merge once, cleanup, close Issues, state and docs)
    -> Evaluate workflow
    -> Reusable improvement?
       -> yes: Start one follow-up improvement through this same orchestration
    -> no: Finish
```

An external deployment handoff is outside this workflow and does not invoke a
bundled deployment Skill. When separately authorized, hand off the immutable
artifact and source commit, target environment and authorization, and the
documented deployment, health-check, and rollback instructions to the target
project's release owner. That owner performs and verifies the rollout or
rollback; completion evidence is the external release result or incident link
recorded with the delivery.

### Persisted plans inside a full orchestration

A delivery that spans several sessions, several Tickets, or several
dependencies persists its Plan and child Tickets as GitHub Issues before branch
work starts. A small, single-session delivery keeps its plan inline. When a plan
is persisted, it owns one branch, one pull request, and one merge for all of its
Tickets, and its metadata stays current at the boundaries below.

## Ticket-to-Slice hierarchy

Planning begins with a Requirement Contract that preserves the original user
intent as stable Requirement IDs plus Must Not, Non-goal, Constraint,
Assumption, and Open Question boundaries. The Requirement Fidelity Gate must
pass before decomposition, and Requirement IDs remain traceable through
Tickets, Slices, acceptance criteria, and verification evidence.

- A **Plan** is one coherent requirement or delivery boundary. When persisted,
  it owns one Plan Issue, one implementation branch, one pull request, and one
  merge.
- A **Ticket** is a behavior or capability boundary inside a Plan. It owns one
  child Issue, its related tests and documentation, and no independent branch,
  pull request, or merge.
- A **Slice** is an execution-ready unit inside a Ticket. It carries its own
  scope, dependencies, acceptance criteria, test strategy, test level, test
  cases, and validation command.
- Establish the Plan boundary, split the requirement into Tickets, and then
  split each Ticket into dependency-ordered Slices. Do not create Slices before
  the Ticket boundaries are clear.
- Keep all Tickets and their Slices on the Plan branch. Ticket dependencies
  control execution order within the Plan; Slice dependencies control order
  inside a Ticket. Neither creates a separate branch or merge.
- Planning depth scales with the requirement. Smaller Tickets reduce planning
  detail, never the persisted Plan's single branch, pull request, or merge.

Planning controls architecture and scope. Verification controls implementation
evidence. Neither replaces the other.

## Slice contract

Each Slice must be independently understandable and contain:

```text
Goal
Requirement coverage
Scope
Out of scope
Dependencies
Acceptance criteria
Relevant context/files
Test strategy
Test level
Test cases
Validation command
```

A persisted Plan carries its canonical GitHub Issue link and execution metadata
(`Status`/`Branch`/`Base`/`PR`); every persisted Ticket carries its child Issue
link, Plan link, `Status`, dependencies, acceptance contract, and Slice plan.
Ticket and Slice work inherit the Plan's branch and base while carrying their
own execution contracts. When persistence applies, every required Issue exists
before the Plan branch is created, and a failed Issue operation blocks the
workflow with no Markdown or chat-only fallback.

Only start dependency-ready Slices. The main agent may execute one Slice
itself, or run several independent Slices with disjoint ownership boundaries.
Load only the files, documentation, and state needed for each Slice. Do not
implement future-slice features or unrelated refactors. Record each result
before selecting the next Slice.

## Adaptive agent orchestration

After the Plan branch exists, and whenever the current stage contains several
bounded tasks, the main agent dynamically chooses whether delegation is useful.
Single-agent execution remains valid and is preferred when it is simpler.

Use the Slice contract as the scheduling contract during implementation. A
dependency-ready Slice becomes a candidate for the next execution wave only
when its ownership boundary is clear. Independent read-only investigation,
isolated implementation, and bounded verification may be delegated; dependent
or overlapping work remains sequential.

The main agent decides at runtime:

- whether to delegate at all;
- which ready tasks to execute itself;
- how many subagents to use up to the host concurrency ceiling;
- which available subagent best matches each task;
- when to stop parallel work and return to sequential integration.

Parallel write tasks must not modify the same files, interfaces, schemas,
migrations, or shared configuration. When write isolation is uncertain, prefer
read-only delegation or have the subagent return findings or a patch for
main-agent integration.

Every delegated task includes:

- goal;
- scope and out-of-scope;
- relevant files or ownership boundary;
- dependencies;
- acceptance criteria;
- validation;
- expected result summary.

The main agent must not duplicate active delegated work. Subagents return
material findings, changed files or patches, test results, and unresolved risks
rather than raw logs. Integrate the current wave before scheduling the next
wave, then recompute dependency readiness from fresh evidence.

Prefer one delegation level; subagents do not create further subagents unless
explicitly required. Publication, merge, stage-gate decisions, and final
judgment remain with the main agent.

## Branch and PR discipline

Published work goes through a branch and a pull request; there is no direct
default-branch delivery path for a published change.

- A persisted Plan owns exactly one implementation branch, one pull request,
  and one merge, named `<type>/<plan-id>-<short-description>`. All of its
  Tickets and Slices share that branch.
- Create the Plan branch from the updated default branch. Ticket dependencies
  are completed and validated on that branch; they require no prerequisite
  merge and no new branch.
- Verify the current branch and working tree before editing. Preserve unrelated
  or uncommitted work.
- Parallel workers use isolated worktrees or return patches and findings for
  integration on the same branch. Never switch branches in a working directory
  shared by active workers, and never create a second delivery branch for a
  Ticket.
- Before publishing, complete the change's acceptance checks and relevant
  integration checks.
- Treat each persisted Plan Issue and implementation branch as a one-to-one
  pair. Record the exact `Branch` and `Base` on the Plan Issue and set Plan
  `Status: in_progress` before the first edit; when resuming, verify the branch
  still matches the Plan Issue.
- The pull request head and base must match the Plan's `Branch` and `Base`.
  Record the pull request on the Plan Issue and set `Status: in_review` when it
  opens; after the verified merge, set the Plan and all child Tickets to
  `Status: done` and close them.
- Track implementation readiness separately from merge status. A passing change
  is ready to open or update a pull request; it is delivered only after merging.
- If a Ticket needs to be abandoned, preserve its work and re-plan. Do not
  automatically delete unmerged branches or reset user changes.

## Slice execution loop

For each self-executed or delegated Slice:

1. Read its goal, boundaries, dependencies, acceptance criteria, relevant
   context, test strategy, test level, test cases, and validation command.
2. Confirm the smallest useful verification set before editing.
3. For a behavior change, bug fix, regression, API behavior, core business
   logic, data processing, or high-risk code, write or adjust a meaningful
   test first and confirm it fails when possible.
4. For documentation, configuration, dependency updates, CSS/UI styling,
   typo fixes, simple refactors, or exploratory work, do not force a RED test;
   use the smallest relevant validation instead.
5. Make the minimum implementation change.
6. Run the selected checks and fix failures directly when the cause is
   clear.
7. Refactor only within the slice and only after its acceptance criteria pass.
8. Mark the Slice complete only when its acceptance criteria and selected
   validation pass. A delegated agent then returns changed files, commands,
   results, risks, and follow-up work as its expected result summary for the
   main agent.
9. If a design assumption is wrong, stop expanding the patch and return to
   Plan or split the slice.

## Test levels and bounded verification

Select one level per slice:

| Level | Use |
|---|---|
| `minimal` | Tiny changes, docs, configuration, styling, and simple scripts. |
| `focused` | Default; tests directly tied to the slice acceptance criteria. |
| `regression` | Bug fixes, cross-module changes, or a demonstrated regression risk. |
| `full` | High-risk changes, release gates, or an explicit requirement. |

Run the smallest verification set that provides sufficient evidence, but do
not equate a GREEN level with completion. Map every acceptance criterion to
executed evidence and select mandatory test dimensions from the behavior and
risk. Boundary, negative, integration/contract, regression, property/fuzz,
mutation/test-strength, browser/E2E, and isolation/flaky checks are required
when applicable; record a concrete N/A reason when a high-value dimension does
not apply. Stop only when the Test Quality Gate is satisfied. Coverage is
diagnostic only, and retry cannot convert an unexplained flaky failure to PASS.
The report should name the level, matrix, quality-gate dimensions, commands,
results, evidence, N/A reasons, and any escalation reason.


## Post-delivery evaluation and bounded self-improvement

Run one lightweight process evaluation after the change is delivered. This is
not a merge gate and must not
delay an otherwise complete delivery.

Evaluate only evidence from the completed work:

- avoidable rework, failed assumptions, and repeated delivery failures;
- planning, context loading, or delegation that was too heavy or too weak;
- tests or redaction that were disproportionate to the actual risk;
- repeated manual steps that are good automation candidates;
- workflow instructions that were unclear, duplicated, or missing.

Keep the result compact:

```text
Keep: what worked and should remain
Improve: one highest-value reusable improvement, or none
Evidence: concrete event from this delivery
Action: none | follow-up change | report for later
```

## Timing a requested workflow run

When the user explicitly asks for timing, capture monotonic wall-clock duration
for each externally observable gate: Plan/Ticket setup and Plan branch creation, implementation,
validation, redaction, commit/push, PR, merge/cleanup, and
any requested Skill installation or synchronization. Use the measured command
boundaries rather than estimates, report the total separately, and identify
the dominant latency source. Timing is observational
and does not add a new delivery gate; do not persist session-specific timing
logs or include credentials, tokens, or private endpoint values in the report.

Self-improvement is bounded by these rules:

1. Improve the workflow only when the lesson is reusable across future work and
   supported by concrete evidence. Task-specific preference is not enough.
2. Prefer simplifying, merging, or removing redundant steps before adding a new
   stage, agent, skill, document, or persistent record.
3. Never weaken branch/PR, redaction, security, permission,
   or release gates merely to reduce friction.
4. A concrete, low-risk improvement that stays within the current workflow's
   intent may start automatically as one new follow-up change. Changes to
   policy, permissions, security posture, release behavior, or broad project
   scope are reported instead of self-applied.
5. A follow-up improvement is a normal repository change: start from the
   updated default branch and repeat Plan -> Branch -> Test -> applicable
   Redaction -> Commit -> Push -> PR -> Merge. Never edit
   the completed branch, installed skill, or default branch as a side effect of
   evaluation.
6. Start at most one automatic follow-up improvement per delivered user
   request. The follow-up may be evaluated, but its evaluation must not
   automatically create another improvement change.
7. If no meaningful improvement is supported by evidence, finish without
   inventing work or creating backlog noise.

The purpose of the loop is to make future executions simpler and more reliable,
not to maximize process, documentation, or agent activity.

## Repo state as a recovery point

Read `docs/Repo_Current_State.md` at the beginning of planning. Keep it as a
compact, verified recovery point containing the current focus, implemented
capabilities, in-progress Slice, known failures, constraints, architecture
orientation, and next Slice. After merge, branch cleanup, and default-branch
update, refresh it when verified project state changed. Link to the active
GitHub Issue for Ticket detail; do not turn it into a session transcript,
complete backlog, or test report.

## Redaction gate contract

Run the gate on the files staged for the next commit, and repeat it after any
subsequent fix that changes staged content before the next commit.

- Stage the intended change, then run the `data-document-redaction` scanner and
  follow [`docs/workflow/redaction.md`](docs/workflow/redaction.md).
- Continue on `pass` or `noop`; record the inspected scope and skip only when
  the staged change carries no sensitive surface.
- `findings`, `needs_review`, and `error` stop the boundary transition.
  Sanitize only the reported files, stage the corrections, and re-scan until
  `pass`; fix the cause first when the scan itself could not run.
- The specialist reports finding types, file paths, and line numbers only.
  Never include original values, mappings, credentials, or full matching
  context.
- The scan protects the next commit; it is not proof that the repository or its
  history is free of secrets. Document, PDF, Office, OCR, and non-Git export
  sanitization are out of scope for this package.

## Stage workflows and specialist skills

Stage workflows decide *when* a stage runs. Capability skills define *how* it is
performed. Invoke a skill only when its trigger applies, follow its own
`SKILL.md`, and do not duplicate its detailed procedure here.

Stage workflows:

- `plan-workflow`: requirement to executable work definition, including the
  persistence decision.
- `develop-workflow`: context to minimal implementation to Development Complete.
- `verify-workflow`: verification trigger and level, invoking `test-workflow`,
  then a bounded conclusion.
- `publish-workflow`: documentation impact check, staged redaction, commit,
  push, and pull-request readiness. It stops at PR ready and never merges.
- `integrate-workflow`: merge once, delete the branch, update the default
  branch, close the Plan and its Tickets, and reconcile state and documentation.

Capability skills:

- `plan-to-ticket`: Plan/Ticket/Slice decomposition and, whenever a plan is
  persisted, the persistence contract for the Plan Issue and its child Ticket
  Issues. Generated Slices must satisfy the Slice contract above and expose
  enough boundaries for a safe delegation decision.
- `test-workflow`: execute the selected validation level and report bounded
  evidence.
- `repo-current-state`: reconcile verified state after merge, branch cleanup,
  and default-branch synchronization.
- `repo-documentation`: run its documentation impact check for every change,
  and whenever the user asks to normalize, audit, or organize documentation;
  update the canonical owner document and the documentation index, or record
  that no documentation change is needed.
- `data-document-redaction`: scan the files staged for the next commit before
  publishing, and again after a blocking review fix that changes staged
  content.
- `github-push-when-ready`: before branch publication, commit, push, or PR
  readiness.

If a required skill is unavailable locally, report it instead of silently
replacing its workflow.

## Completion gates

For an explicitly authorized end-to-end delivery:

1. Record the Plan and its child Tickets when the persistence trigger applies,
   then create or resume the Plan branch before editing.
2. Implement the change and run its selected verification.
3. Run the `repo-documentation` impact check. Update the canonical owner
   document and the documentation index, or record that no documentation change
   is needed.
4. Stage the intended change and run `data-document-redaction`; continue only
   on `pass`, `noop`, or a recorded no-sensitive-surface skip.
5. Invoke `github-push-when-ready`, commit, push the branch, and create or
   update the pull request until it is ready to merge.
6. Merge the pull request once, delete the source branch, update the default
   branch, and close the Plan and its linked Tickets.
7. Update `docs/Repo_Current_State.md` and other State / Docs after the merge
   and default-branch update when verified project state changed.
8. Run the post-delivery workflow evaluation. If one bounded, evidence-backed
   reusable improvement qualifies, start it as one separate follow-up change
   through this same orchestration.

Update the Plan's `Status`/`Branch`/`Base`/`PR` metadata at the workflow
boundaries defined by the Plan Issue contract. Update each Ticket's status,
Plan link, dependencies, and acceptance evidence at its boundaries, but do not
give a Ticket independent branch or PR metadata. Keep child Tickets open
through `in_review`; set them to `done` and close them only after the pull
request is verified merged.

## Installation

Install the complete workflow skill set from a full checkout of this
repository:

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
```

Update existing installations with:

```bash
bash scripts/install-all.sh --update
```

The installer copies the root skill and `skills/` bundles from this checkout;
it does not clone specialist repositories. Select the host with `--target`
(`codex` is the default; `claude` installs for Claude Code), and repeat that
target when updating — `--update` without `--target` always updates the Codex
destination. Restart the host after installation. The repository's own
`docs/deployment/installation.md` carries the destinations and the full
procedure; that guide is not part of this installed bundle.
