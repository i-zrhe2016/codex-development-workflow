---
name: codex-development-workflow
description: "Entry point for repository-wide Codex development. Route every change through a feature branch, tests, applicable redaction, commit, push, PR, automatic review, merge, cleanup, and state update, with Ticket/Slice planning when needed."
---

# Codex Development Workflow

Use this skill as the entry point for repository development. The main agent
owns requirements, architecture, planning, Ticket/Slice decomposition,
integration, delivery gates, and final judgment. Every change follows the same
feature-branch and PR lifecycle; only planning depth, test level, and whether a
Ticket is needed may vary. Specialist skills provide procedures for the work
they own.

## Core workflow

```text
Requirement
    -> Understand repo
    -> Plan
    -> Slice / Ticket if needed
    -> Create branch
    -> Implement
    -> Test
    -> Redaction scan if applicable
    -> Commit
    -> Push branch
    -> Create / Update PR
    -> Automatic Review
    -> Blocking findings?
       -> yes: Fix -> Test -> Redaction -> Commit -> Push -> Automatic Review again
       -> no: Merge PR -> Delete branch -> Update main -> Close Ticket
    -> Update State / Docs
    -> Deploy if needed
```

## One delivery path for every change

Docs, code, tests, configuration, refactors, bug fixes, features, dependency
updates, and CI/CD changes all use the same path:

1. Create or resume a feature branch before editing.
2. Implement the planned change and run the selected tests.
3. Run the redaction scan when the artifact set may contain sensitive content.
4. Commit and push the branch, then create or update its PR.
5. Start Automatic Review immediately after the PR is created or updated; do
   not wait for user confirmation.
6. If review finds a blocking issue, fix it and repeat Test, applicable
   Redaction, Commit, Push, and Automatic Review.
7. Merge only after review passes, delete the source branch, update the base
   branch, close the Ticket when one exists, and then update State / Docs.

The delivery path never has a direct-push exception for documentation, small
fixes, configuration, or other change categories. A single behavior may use
one Slice without a Ticket, but it still requires a branch and PR.

## Ticket-to-Slice hierarchy

- A **Ticket** is a behavior or capability boundary that can be reviewed and
  delivered independently. It owns one Issue, one implementation branch, and
  its related tests and documentation.
- A **Slice** is an execution-ready unit inside a Ticket. It carries its own
  scope, dependencies, acceptance criteria, test strategy, test level, test
  cases, and validation command.
- For a large or multi-behavior request, split the requirements into Tickets
  first, then split each Ticket into dependency-ordered Slices. Do not create
  Slices before the Ticket boundaries are clear.
- Keep all Slices for one Ticket on that Ticket's branch. Ticket dependencies
  control when a branch may start; Slice dependencies control execution order
  within the branch.
- A single-behavior request may remain one Slice without a Ticket or Issue;
  this changes only planning overhead, never the branch or PR gate.

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

When `plan-to-ticket` is used, each Ticket carries its canonical GitHub Issue
link and execution metadata; its Slices inherit the Ticket's Issue, branch, and
base while carrying their own execution contract. The parent plan Issue and all
initial Ticket Issues must exist before implementation branches are created; a
failed Issue operation blocks the workflow and has no Markdown or chat-only
fallback.

Only start dependency-ready Slices. The main agent may execute one Slice
itself, or the delegation gate may start multiple independent Slices with
disjoint ownership boundaries. Load only the files, documentation, and state
needed for each Slice. Do not implement future-slice features or unrelated
refactors. Record each result before selecting the next Slice.

## Optional bounded delegation during implementation

After the feature branch exists and before or during implementation, the main
agent may evaluate whether bounded delegation is useful. Delegation is optional;
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

- Create or resume a feature branch before editing for every change, regardless
  of whether the change is documentation, code, configuration, a refactor, a
  bug fix, a feature, a dependency update, or CI/CD work.
- For Ticketed work, use one branch per Ticket:
  `<type>/<ticket-id>-<short-description>`.
- For a single Slice without a Ticket, use a descriptive feature branch such as
  `<type>/<short-description>`.
- Create new branches from the updated default branch. Start dependent Ticket
  branches after their prerequisite Tickets are merged.
- Keep a Ticket's implementation, tests, and related documentation on its
  branch. Internal Slices share that branch.
- Before editing, verify the current branch and working tree.
  Preserve unrelated or uncommitted work.
- Parallel ticket workers must use separate Git worktrees and branches.
  Never switch branches in a working directory shared by active workers.
- Before committing and pushing a change, complete its acceptance checks and
  relevant integration checks. Every change must have a PR; there is no direct
  default-branch delivery path.
- Treat each ticket Issue and implementation branch as a one-to-one pair.
  Before the first edit, record the exact `Branch` and `Base` values on the
  Issue and set `Status: in_progress`; when resuming, verify the branch still
  matches the Issue.
- Keep all internal Slices for one ticket on that branch. Do not share one
  implementation branch across tickets or create a branch per Slice.
- The ticket PR's head and base must match the Issue's `Branch` and `Base`.
  When the PR opens, record its `PR` and set `Status: in_review`; after the
  verified merge, set `Status: done` and close the Issue.
- Track implementation readiness separately from merge status. A passing
  change is ready to open or update a PR; it is delivered only after merging.
- After Automatic Review passes, merge the PR, delete the source branch, update
  the default branch, close the Ticket when one exists, and then update State /
  Docs.
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

## Automatic Review policy

Automatic Review is mandatory after every change's PR is created or updated and
before merge. It is not performed inside a Slice or before the branch is
published. Use the complete PR diff, branch boundary, and available CI results
as the review context. Start the selected review path immediately without
waiting for user confirmation.

- Before committing and pushing, run the change's acceptance checks and
  relevant integration or regression checks.
- Commit and push the feature branch, then create or update its PR before
  Automatic Review.
- Review the complete PR diff, including every Slice in a Ticket when Ticketed.
- If findings block merge, fix them and repeat Test, applicable Redaction,
  Commit, Push, and Automatic Review on the updated PR.
- When multiple Tickets come together, add broader integration or regression
  checks across them in addition to each Ticket's own checks.
- For the PR-stage gate, use the Codex CLI review command against the actual
  base branch:

  ```bash
  codex review --base <actual-base-branch>
  ```

  This complete-range command is the mandatory Automatic Review path after
  every PR creation or update. `codex review --uncommitted` is only for a
  narrow pre-commit working-tree check, and `codex review --commit SHA` is only
  for a single-commit check; neither replaces the complete PR review. These
  commands do not select the optional supplemental `.codex/agents/reviewer.toml`.

  The project-scoped reviewer may be run separately for additional read-only
  findings, but it never replaces `codex review`:

  ```text
  Use the project-scoped `reviewer` subagent to inspect the current PR diff and
  branch boundary. Return only actionable supplemental findings with file
  references.
  ```

- If Automatic Review finds a blocking problem, fix it, rerun affected tests
  and the applicable redaction scan, then update the PR and run Automatic
  Review again. If the finding changes scope or design, return to Plan.
- Automatic Review never replaces tests, compiler diagnostics, linting, or
  static analysis.

This workflow supports optional bounded delegation. It does not require
multiple agents, parallel implementations, or agent handoffs for every task.

## Specialist skills

Invoke a specialist only when its trigger applies. Follow its own `SKILL.md`;
do not duplicate its detailed procedure here.

- `context-efficiency`: large, unfamiliar, or context-heavy repository
  exploration; it is an optional context-loading aid, not a workflow stage.
- `plan-to-ticket`: complex, multi-ticket, multi-slice, or dependency-driven
  work; split requirements into Tickets before generating their Slices.
  Generated Slices must satisfy the Slice contract above, persist the plan and
  Tickets to GitHub Issues before branch work, and expose enough boundaries for
  the delegation gate to make a safe decision.
- `test-workflow`: execute the selected validation level and report bounded
  evidence.
- `repo-current-state`: reconcile verified state after merge, branch cleanup,
  and default-branch synchronization.
- `data-document-redaction`: classify the complete change set before staging
  or any sharing, export, upload, or publication boundary when sensitive
  surfaces may exist.
- `github-push-when-ready`: before branch publication, commit, push, PR,
  merge, or branch cleanup.
- `auto-deploy`: when deployment, release automation, rollout verification, or
  authorized rollback is in scope.

If a required specialist is unavailable locally, report it instead of silently
replacing its workflow.

## Completion gates

For every change, regardless of its file type or size:

1. Create or resume a feature branch before editing.
2. Implement the change and run its selected tests.
3. Classify the complete output set and run `data-document-redaction` when
   potentially sensitive surfaces are in scope; continue only on `pass` or a
   recorded no-sensitive-surface skip.
4. Invoke `github-push-when-ready`, commit, push the branch, and create or
   update the PR.
5. Start Automatic Review immediately after the PR is created or updated.
6. On blocking findings, repeat Fix -> Test -> Redaction if applicable ->
   Commit -> Push -> Automatic Review until the findings are resolved.
7. Merge only after Automatic Review passes, delete the source branch, update
   the default branch, and close the linked Ticket when one exists.
8. Update `docs/Repo_Current_State.md` and other State / Docs after the merge
   and default-branch update when verified project state changed.
9. When deployment is requested, invoke `auto-deploy` for target-specific
   preflight, execution, verification, and rollback handling.

When a ticket is produced by `plan-to-ticket`, update its status and branch/PR
metadata at the workflow boundaries defined by that skill. Keep tickets open
through `in_review`; set `done` and close them only after the linked PR is
verified merged.

## Repo state as a recovery point

Read `docs/Repo_Current_State.md` at the beginning of planning. Keep it as a
compact, verified recovery point containing the current focus, implemented
capabilities, in-progress Slice, known failures, constraints, architecture
orientation, and next Slice. After merge, branch cleanup, and default-branch
update, refresh it when verified project state changed. Link to the active
GitHub Issue for Ticket detail; do not turn it into a session transcript,
complete backlog, or test report.

## Redaction gate contract

Apply the gate to the complete artifact set before committing or publishing it,
and repeat it after any blocking review fix before the next commit. This
includes source files, documentation, logs, configs, screenshots, exports,
filenames, and metadata.

- Classify the recipient, purpose, required utility, and whether reversibility
  is allowed. Assume non-reversible handling unless the task explicitly needs
  controlled traceability.
- If no potentially sensitive surface is in scope, record the inspected scope
  and the reason the gate was skipped, then continue.
- If a potentially sensitive surface is in scope, follow
  [`docs/workflow/redaction.md`](docs/workflow/redaction.md) and the
  `data-document-redaction` skill. The specialist owns format-specific
  detection, transformation, hidden-surface checks, and validation.
- Continue to commit, push, or share only after a `pass` result and a safe
  delivery report. A `needs_review` or `blocked` result stops the boundary
  transition and records the concrete gap.
- Reports contain types, counts, location categories, hashes, tool versions,
  coverage, and residual risks only. Never include original values, mappings,
  credentials, or full matching context.

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
