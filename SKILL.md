---
name: codex-development-workflow
description: "Entry point for repository-wide Codex development. Use a main-agent staged workflow with optional bounded delegation to classify work, plan small slices, execute with evidence-based testing, integrate, review, and deliver without forcing strict TDD on every change."
---

# Codex Development Workflow

Use this skill as the entry point for non-trivial repository development. The
main agent owns requirements, architecture, planning, decomposition,
integration, and final judgment. It may delegate bounded work after Slicing
when doing so materially improves speed, context isolation, or review quality;
specialist skills provide procedures for the work they own.

## Core workflow

```text
Requirement
    -> Classify
    -> Understand current repo
    -> Plan
    -> Slice
    -> Persist plan/tickets to GitHub Issues
    -> Delegate if useful
    -> Create/resume ticket branch
    -> Execute slice(s)
    -> Next slice?
    -> Integration tests
    -> Update state/docs
    -> Classify outputs
    -> Redact when needed
    -> Commit/Push
    -> Open PR
    -> Review
    -> Fix findings / Re-test
    -> Merge
    -> Close ticket
    -> Optional Deploy / Verify / Rollback
```

Use the lightest path that preserves correctness:

- **Tiny:** classify, make a concise plan, treat the request as one slice, run
  minimal validation, and prepare the change for the single PR-stage review.
- **Normal:** understand the relevant repository area, make a minimal plan,
  execute one or more slices (delegating only when the gate allows it), and
  run focused validation.
- **Complex:** understand the repository, plan dependency-ordered Slices with
  `plan-to-ticket`, evaluate delegation after Slicing, execute each ticket's
  Slices with their own acceptance and test strategy, then run broader
  integration checks when multiple tickets come together before PR review.

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

When `plan-to-ticket` is used, the Slice also carries its canonical GitHub
Issue link and execution metadata, including its implementation branch and
base branch. The parent plan Issue and all initial ticket Issues must exist
before implementation branches are created; a failed Issue operation blocks the
workflow and has no Markdown or chat-only fallback.

Only start dependency-ready Slices. The main agent may execute one Slice
itself, or the delegation gate may start multiple independent Slices with
disjoint ownership boundaries. Load only the files, documentation, and state
needed for each Slice. Do not implement future-slice features or unrelated
refactors. Record each result before selecting the next Slice.

## Optional delegation gate

After `Plan -> Slice` and before execution, the main agent evaluates whether
delegation is useful. Delegation is optional; the default path remains a
single agent executing the Slice itself.

Use delegation only for a bounded, independently executable task. Suitable
targets include repository exploration, independent research, test or
regression analysis, an isolated implementation Slice, or an independent
review. Prefer the built-in `explorer` for read-heavy investigation and
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

## Branch per ticket

- Before implementation, create or resume one branch per ticket:
  `<type>/<ticket-id>-<short-description>`.
- Create new ticket branches from the updated default branch.
  Start dependent tickets after their prerequisite tickets are merged.
- Keep the ticket's implementation, tests, and related documentation
  on the same branch. Internal implementation steps share that branch.
- Before editing, verify the current branch and working tree.
  Preserve unrelated or uncommitted work.
- Parallel ticket workers must use separate Git worktrees and branches.
  Never switch branches in a working directory shared by active workers.
- Before committing and pushing a ticket, complete its acceptance checks and
  relevant integration checks. After its PR is opened, perform the single
  ticket review before merge. Reuse the existing testing, redaction, and
  publication skills.
- Treat each ticket Issue and implementation branch as a one-to-one pair.
  Before the first edit, record the exact `Branch` and `Base` values on the
  Issue and set `Status: in_progress`; when resuming, verify the branch still
  matches the Issue.
- Keep all internal Slices for one ticket on that branch. Do not share one
  implementation branch across tickets or create a branch per Slice.
- The ticket PR's head and base must match the Issue's `Branch` and `Base`.
  When the PR opens, record its `PR` and set `Status: in_review`; after the
  verified merge, set `Status: done` and close the Issue.
- Track implementation readiness separately from merge status.
  A passing ticket is ready to open a PR; it is delivered after merging.
- After an authorized merge, follow the existing branch cleanup
  procedure and update the default branch before starting dependent work.
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

## Review policy

Review is one main-agent-owned stage after the ticket PR is opened and before
it is merged. It is not performed inside a Slice, during integration, or before
commit/push. A ticket may contain multiple Slices, but all Slices within the
ticket must pass their selected checks before its PR is opened. Use the complete
PR diff, branch boundary, and available CI results as the review context.
Choose one review path—the built-in `codex review` command or the project
`reviewer`—rather than running both as routine gates.

- Before committing and pushing each ticket, run its acceptance checks and
  relevant ticket-level integration or regression checks.
- Commit/push the feature branch and open its PR before the single review.
- Review the complete PR diff for the ticket, including every Slice within
  that ticket, after the PR is opened and before merge.
- Fix review findings and rerun the affected checks before merging. Do not add
  a second routine review after the fixes.
- When multiple tickets come together, add broader integration or regression
  checks across those tickets in addition to each ticket's own checks.
- Use the Codex CLI review command when available:

  ```bash
  codex review --uncommitted
  codex review --base BRANCH
  codex review --commit SHA
  ```

  These commands are one review path and do not select the project-scoped
  `.codex/agents/reviewer.toml`. To use that custom reviewer as the single
  review path, start an interactive Codex session from the project root and ask:

  ```text
  Use the project-scoped `reviewer` subagent to inspect the current PR diff and
  branch boundary. Wait for its read-only result and return only actionable
  findings with file references.
  ```

- If review finds a blocking problem, fix it, rerun affected tests, and update
  the PR before merge. If the finding changes scope or design, return to Plan.
- Review never replaces tests, compiler diagnostics, linting, or static
  analysis.

This workflow supports optional bounded delegation. It does not require
multiple agents, parallel implementations, or agent handoffs for every task.

## Specialist skills

Invoke a specialist only when its trigger applies. Follow its own `SKILL.md`;
do not duplicate its detailed procedure here.

- `context-efficiency`: large, unfamiliar, or context-heavy repository
  exploration; it is an optional context-loading aid, not a workflow stage.
- `plan-to-ticket`: complex, multi-slice, or dependency-driven work; generated
  Slices must satisfy the Slice contract above, persist the plan and tickets to
  GitHub Issues before branch work, and expose enough boundaries for the
  delegation gate to make a safe decision.
- `test-workflow`: execute the selected validation level and report bounded
  evidence.
- `repo-current-state`: reconcile verified state after a meaningful slice or
  integrated change.
- `data-document-redaction`: classify the complete change set before staging
  or any sharing, export, upload, or publication boundary when sensitive
  surfaces may exist.
- `github-push-when-ready`: before commit or push.
- `auto-deploy`: when deployment, release automation, rollout verification, or
  authorized rollback is in scope.

If a required specialist is unavailable locally, report it instead of silently
replacing its workflow.

## Completion gates

For each ticket, after all Slices within that ticket pass their selected level:

1. Run integration or regression checks appropriate to that ticket, including
   browser/E2E only for relevant user-visible behavior.
2. If multiple tickets are being delivered together, run broader integration or
   regression checks across the combined change as well.
3. Update `docs/Repo_Current_State.md` and other docs only when verified
   behavior, architecture, dependencies, deployment, or important state
   changed.
4. Classify the complete output set.
5. If potentially sensitive surfaces exist, invoke
   `data-document-redaction` and continue only on `pass`.
6. Invoke `github-push-when-ready` before committing, pushing, or opening the
   PR.
7. Commit/push the ticket branch and open its PR.
8. Perform the single PR-stage review, fix findings, and rerun affected checks.
9. Merge the PR only after the review and re-test pass, then update and close
   the linked ticket Issue.
10. When deployment is requested, invoke `auto-deploy` for target-specific
   preflight, execution, verification, and rollback handling.

When a ticket is produced by `plan-to-ticket`, update its status and branch/PR
metadata at the workflow boundaries defined by that skill. Keep tickets open
through `in_review`; set `done` and close them only after the linked PR is
verified merged.

## Repo state as a recovery point

Read `docs/Repo_Current_State.md` at the beginning of planning. Keep it as a
compact, verified recovery point containing the current focus, implemented
capabilities, in-progress slice, known failures, constraints, architecture
orientation, and next Slice. Link to the active GitHub Issue for ticket detail;
do not turn it into a session transcript, complete backlog, or test report.

## Redaction gate contract

Apply the gate to the complete artifact set before staging, committing,
sharing, or publishing it. This includes source files, documentation, logs,
configs, screenshots, exports, filenames, and metadata.

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
