---
name: codex-development-workflow
description: "Entry point for repository-wide Codex development. Record exactly one Plan per requirement with one or more Tickets, then route the Plan through one branch, tests, applicable redaction, commit, push, PR, pr-review, merge, cleanup, state update, and post-delivery process evaluation."
---

# Codex Development Workflow

Use this skill as the entry point for repository development. The main agent
owns requirements, architecture, planning, Plan/Ticket/Slice decomposition,
integration, delivery gates, process evaluation, and final judgment. Every
requirement has exactly one Plan Issue, and each Plan contains one or more
Ticket Issues before implementation starts. The Plan owns the single branch,
PR, and merge; only planning depth and test level may vary. Specialist skills
provide procedures for the work they own.

## Core workflow

```text
Requirement
    -> Understand repo
    -> Plan
    -> Record Plan + Tickets + Slice plan (GitHub Issues)
    -> Create Plan branch
    -> Implement all Plan Tickets
    -> Test
    -> Redaction scan if applicable
    -> Commit
    -> Push branch
    -> Create / Update PR
    -> pr-review
    -> PASS: Merge the Plan PR once -> Delete branch -> Update main -> Close Plan + Tickets
    -> BLOCKED: Fix -> Test -> Redaction -> Commit -> Push -> pr-review again
    -> Update State / Docs
    -> External deployment handoff if separately authorized
    -> Evaluate workflow
    -> Reusable improvement?
       -> yes: Start one follow-up improvement through this same workflow
       -> no: Finish
```

## One delivery path for every change

Docs, code, tests, configuration, refactors, bug fixes, features, dependency
updates, and CI/CD changes all use the same path:

1. Record exactly one Plan Issue and all required child Ticket Issues for the
   requirement, then create or resume the Plan branch before editing.
2. Implement the planned Tickets and run the selected tests.
3. Stage the intended files and run the redaction scan; continue on `pass`, or
   on a recorded skip when the staged change carries no sensitive surface.
4. Commit and push the branch, then create or update its PR.
5. Invoke `pr-review` immediately after the PR is created or updated; do not
   wait for user confirmation.
6. If `pr-review` returns `BLOCKED`, fix the findings and repeat Test, applicable
   Redaction, Commit, Push, and `pr-review`.
7. Merge the Plan PR only after `pr-review` returns `PASS`, delete the source
   branch, update the base branch, close the Plan and its child Tickets, and
   then update State / Docs.
8. After delivery, evaluate the workflow and start
   at most one bounded follow-up improvement when the evidence is reusable.

The delivery path never has a direct-push exception for documentation, small
fixes, configuration, or other change categories. Every requirement, however
small, has exactly one Plan containing at least one Ticket; a single-behavior
requirement is one Ticket containing one implicit Slice, and it still requires
one branch, one PR, and one merge.

## Ticket-to-Slice hierarchy

- A **Plan** is one coherent requirement or feature delivery boundary. It owns
  one Plan Issue, one implementation branch, one PR, and one merge.
- A **Ticket** is a behavior or capability boundary inside a Plan. It owns one
  child Issue, its related tests and documentation, and no independent branch,
  PR, or merge.
- A **Slice** is an execution-ready unit inside a Ticket. It carries its own
  scope, dependencies, acceptance criteria, test strategy, test level, test
  cases, and validation command.
- Every requirement has exactly one Plan Issue and at least one Ticket Issue
  before branch work starts. A single-behavior requirement is one Ticket with a
  single Slice; larger work adds more Tickets and Slices under the same Plan.
- Establish the Plan boundary, split the requirement into Tickets, and then split
  each Ticket into dependency-ordered Slices. Do not create Slices before the
  Ticket boundaries are clear.
- Keep all Tickets and their Slices on the Plan branch. Ticket dependencies
  control execution order within the Plan; Slice dependencies control order
  inside a Ticket. Neither creates a separate branch or merge.
- Planning depth scales with the requirement. Smaller Tickets reduce planning
  detail, never the Plan's single branch, PR, or merge gate.

Planning controls architecture and scope. Testing controls implementation
evidence. Neither replaces the other.

## Slice contract

Each normal or complex slice must be independently understandable and contain:

```text
Goal
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

The Plan carries its canonical GitHub Issue link and execution metadata
(`Status`/`Branch`/`Base`/`PR`); every Ticket carries its child Issue link, Plan
link, `Status`, dependencies, acceptance contract, and Slice plan. Ticket and
Slice work inherit the Plan's branch and base while carrying their own execution
contracts. Every requirement records exactly one Plan Issue and at least one Ticket Issue;
all required Issues must exist before the Plan branch is created. A failed
Issue operation blocks the workflow and has no Markdown or chat-only fallback.

Only start dependency-ready Slices. The main agent may execute one Slice
itself, or the delegation gate may start multiple independent Slices with
disjoint ownership boundaries. Load only the files, documentation, and state
needed for each Slice. Do not implement future-slice features or unrelated
refactors. Record each result before selecting the next Slice.

## Optional bounded delegation during implementation

After the Plan branch exists and before or during implementation, the main agent
may evaluate whether bounded delegation is useful. Delegation is optional;
the default path remains a single agent executing the Slice itself. Delegation
does not create a second delivery path or bypass the branch, test, redaction,
commit, push, PR, review, and merge gates.

Use delegation only for a bounded, independently executable task. Suitable
targets include repository exploration, independent research, test or
regression analysis, or an isolated implementation Slice. Prefer the built-in
`explorer` for read-heavy investigation and
`worker` for an isolated implementation Slice. Keep dependent or overlapping
work sequential.

Parallel write tasks require clearly separated ownership boundaries. They must
not modify the same files, interfaces, schemas, migrations, or shared
configuration. A Slice with unresolved dependencies stays with the main agent
or waits until its dependencies are complete.

For every delegated task, provide:

- goal;
- scope and out-of-scope;
- relevant files or ownership boundary;
- dependencies;
- acceptance criteria;
- validation;
- expected result summary.

The main agent must not duplicate work delegated to an active subagent. Workers
return material findings, changes, test results, and unresolved risks rather
than raw logs. Prefer one delegation level; subagents do not create further
subagents unless explicitly required.

## Branch before implementation

- Create or resume the Plan branch before editing for every change, regardless
  of whether the change is documentation, code, configuration, a refactor, a
  bug fix, a feature, a dependency update, or CI/CD work.
- Record the Plan Issue and child Ticket Issues before branching, then use one
  branch per Plan: `<type>/<plan-id>-<short-description>`.
- Create the Plan branch from the updated default branch. Ticket dependencies
  are completed and validated on that branch; they do not require prerequisite
  merges or new branches.
- Keep the Plan's implementation, tests, and related documentation on its
  branch. All Tickets and internal Slices share that branch.
- Before editing, verify the current branch and working tree.
  Preserve unrelated or uncommitted work.
- Parallel workers must use isolated worktrees or return patches/findings for
  integration on the Plan branch. Never switch branches in a working directory
  shared by active workers, and never create a second delivery branch for a
  Ticket.
- Before committing and pushing a change, complete its acceptance checks and
  relevant integration checks. Every change must have a PR; there is no direct
  default-branch delivery path.
- Treat each Plan Issue and implementation branch as a one-to-one pair. Before
  the first edit, record the exact `Branch` and `Base` values on the Plan Issue
  and set Plan `Status: in_progress`; when resuming, verify the branch still
  matches the Plan Issue.
- Keep all Tickets and Slices for one Plan on that Plan branch. Do not share a
  Plan branch across Plans or create a branch per Ticket or Slice.
- The Plan PR's head and base must match the Plan Issue's `Branch` and `Base`.
  When the single Plan PR opens, record its `PR` and set Plan
  `Status: in_review`; after the verified merge, set the Plan and all child
  Tickets to `Status: done` and close them.
- Track implementation readiness separately from merge status. A passing
  change is ready to open or update a PR; it is delivered only after merging.
- After `pr-review` returns `PASS`, merge the one Plan PR, delete the source
  branch, update the default branch, close the Plan and child Tickets, and then
  update State / Docs.
- If a ticket needs to be abandoned, preserve its work and re-plan.
  Do not automatically delete unmerged branches or reset user changes.

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
   validation pass. A delegated worker then returns changed files, commands,
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

Run the smallest verification set that provides sufficient evidence. After the
selected level passes, stop by default. Do not add suites, edge cases, or
broader checks unless the acceptance criteria, a failure, an affected boundary,
release requirements, or the user justifies escalation. The report should name
the level used, commands, result, evidence, and any escalation reason.

## Pull-request review gate

After `github-push-when-ready` reports the Plan PR ready, invoke `pr-review`
immediately. `PASS` permits merge. `BLOCKED` requires the main agent to batch
the findings, fix them, run affected tests and applicable redaction, commit,
push, and invoke `pr-review` again.

`pr-review` is the sole owner of review scope, execution, assessment, and the
decision about whether the PR can merge. Do not merge before it returns
`PASS`.

This workflow supports optional bounded delegation. It does not require
multiple agents, parallel implementations, or agent handoffs for every task.

## Post-delivery evaluation and bounded self-improvement

Run one lightweight process evaluation after the change is delivered. This is
not a merge gate and must not
delay an otherwise complete delivery.

Evaluate only evidence from the completed work:

- avoidable rework, failed assumptions, and repeated review findings;
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
validation, redaction, commit/push, PR and `pr-review`, merge/cleanup, and
any requested Skill installation or synchronization. Use the measured command
boundaries rather than estimates, report the total separately, and identify
whether network or reviewer latency dominated the run. Timing is observational
and does not add a new delivery gate; do not persist session-specific timing
logs or include credentials, tokens, or private endpoint values in the report.

Self-improvement is bounded by these rules:

1. Improve the workflow only when the lesson is reusable across future work and
   supported by concrete evidence. Task-specific preference is not enough.
2. Prefer simplifying, merging, or removing redundant steps before adding a new
   stage, agent, skill, document, or persistent record.
3. Never weaken branch/PR, `pr-review`, redaction, security, permission,
   or release gates merely to reduce friction.
4. A concrete, low-risk improvement that stays within the current workflow's
   intent may start automatically as one new follow-up change. Changes to
   policy, permissions, security posture, release behavior, or broad project
   scope are reported instead of self-applied.
5. A follow-up improvement is a normal repository change: start from the
   updated default branch and repeat Plan -> Branch -> Test -> applicable
   Redaction -> Commit -> Push -> PR -> `pr-review` -> Merge. Never edit
   the completed branch, installed skill, or default branch as a side effect of
   evaluation.
6. Start at most one automatic follow-up improvement per delivered user
   request. The follow-up may be evaluated, but its evaluation must not
   automatically create another improvement change.
7. If no meaningful improvement is supported by evidence, finish without
   inventing work or creating backlog noise.

The purpose of the loop is to make future executions simpler and more reliable,
not to maximize process, documentation, or agent activity.

## Specialist skills

Invoke a specialist only when its trigger applies. Follow its own `SKILL.md`;
do not duplicate its detailed procedure here.

- `context-efficiency`: large, unfamiliar, or context-heavy repository
  exploration; it is an optional context-loading aid, not a workflow stage.
- `plan-to-ticket`: every requirement receives a Plan/Ticket/Slice breakdown;
  create exactly one Plan Issue and one or more child Ticket Issues before
  generating their Slices. Generated Slices must satisfy the Slice contract
  above, persist the Plan and Tickets to GitHub Issues before branch work, and
  expose enough boundaries for the delegation gate to make a safe decision.
- `test-workflow`: execute the selected validation level and report bounded
  evidence.
- `repo-current-state`: reconcile verified state after merge, branch cleanup,
  and default-branch synchronization.
- `data-document-redaction`: scan the files staged for the next commit before
  publishing, and again after a blocking review fix that changes staged
  content.
- `github-push-when-ready`: before branch publication, commit, push, or PR
  readiness.
- `pr-review`: after a PR is created or updated; the single merge decision gate.

If a required specialist is unavailable locally, report it instead of silently
replacing its workflow.

## Completion gates

For every change, regardless of its file type or size:

1. Record exactly one Plan Issue and all child Ticket Issues, then create or
   resume the Plan branch before editing.
2. Implement the change and run its selected tests.
3. Stage the intended change and run `data-document-redaction`; continue only
   on `pass`, `noop`, or a recorded no-sensitive-surface skip.
4. Invoke `github-push-when-ready`, commit, push the Plan branch, and create or
   update the single Plan PR until it is ready for review.
5. Invoke `pr-review` immediately. Merge only after it returns `PASS`.
6. On `BLOCKED`, repeat Fix -> Test -> Redaction if applicable -> Commit -> Push
   -> `pr-review` until it returns `PASS`.
7. After `PASS`, merge the Plan PR once, delete the source branch, update the
   default branch, and close the Plan and its linked Tickets.
8. Update `docs/Repo_Current_State.md` and other State / Docs after the merge
   and default-branch update when verified project state changed.
9. Run the post-delivery workflow evaluation. If one bounded, evidence-backed
    reusable improvement qualifies for automatic self-improvement, start it as
    a separate follow-up change through the same branch/PR lifecycle.

Update the Plan's `Status`/`Branch`/`Base`/`PR` metadata at the workflow
boundaries defined by the Plan Issue contract. Update each Ticket's status,
Plan link, dependencies, and acceptance evidence at its boundaries, but do not
give a Ticket independent branch or PR metadata. Keep child Tickets open
through `in_review`; set them to `done` and close them only after the single
Plan PR is verified merged.

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
blocking review fix that changes staged content before the next commit.

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
it does not clone specialist repositories. Codex uses
`${CODEX_HOME:-$HOME/.codex}/skills` by default. Restart Codex after
installation.
