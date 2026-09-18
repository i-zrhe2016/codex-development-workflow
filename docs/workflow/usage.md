# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for repository work. It
keeps planning at the Plan/Ticket/Slice levels, but uses one delivery path for
every change type.

## Staged workflow

```text
Requirement
  -> Understand repo
  -> Plan
  -> Record Plan + Tickets + Slices
  -> Create Plan branch
  -> Implement all Plan Tickets
  -> Test
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> pr-review
  -> PASS: Merge the Plan PR once
  -> BLOCKED: Fix / Test / Redaction / Commit / Push / pr-review loop
  -> Delete branch
  -> Update main
  -> Close Plan + Tickets
  -> Update State / Docs
  -> Optional external release handoff (outside this workflow)
  -> Evaluate workflow
  -> Reusable improvement? -> one bounded follow-up change or finish
```

The pipeline is identical for Docs, Code, Tests, Config, Refactor, Bugfix,
Feature, Dependency, and CI/CD changes. Every requirement is recorded as
exactly one Plan Issue with one or more child Ticket Issues before the Plan
branch starts; only planning depth and test level vary, and no category may
direct-push around the PR gate.

## External deployment handoff

Deployment is outside this repository's workflow and does not invoke a bundled
deployment Skill. When separately authorized, the Plan owner hands the target
project's release owner the immutable artifact and source commit, target
environment and authorization, and documented deployment, health-check, and
rollback instructions. The external release owner performs and verifies the
rollout or rollback; record the external release result or incident link as
completion evidence with the delivery.

## Ticket-to-Slice hierarchy

Every requirement gets exactly one Plan Issue and at least one Ticket Issue.
When a requirement crosses multiple behaviors or has dependencies, use this
order:

1. Define the single requirement boundary and create its Plan Issue.
2. Split the requirement into independently reviewable behavior Tickets.
3. Define each Ticket's scope, dependencies, acceptance boundary, and Issue.
4. Split each Ticket into dependency-ordered, independently verifiable
   Slices.

All Tickets and Slices for one Plan share the Plan's implementation branch.
Ticket dependencies determine execution order within the Plan; Slice
dependencies determine the execution order within a Ticket. A
single-behavior requirement is one Ticket containing one Slice, and it still
requires the Plan branch and one PR.

For every Slice, define:

```text
Goal, Scope, Out of scope, Dependencies, Acceptance criteria,
Relevant context/files, Test strategy, Test level, Test cases,
Validation command
```

Only start dependency-ready Slices. The main agent may execute a Slice itself
or delegate independent Slices with disjoint ownership boundaries. If an
implementation assumption is wrong, stop and return to Plan or split the
Slice instead of growing the patch.

## Persistent plan and ticket handoff

When `plan-to-ticket` creates a plan or ticket, GitHub Issues are the mandatory
durable source of truth. Create or update one Plan Issue and every required
child Ticket Issue before the Plan branch starts. The Plan Issue always exists,
including for a one-Ticket requirement. The Plan Issue retains:

- `Status`: `planned`, `in_progress`, `blocked`, `in_review`, or `done`;
- `Branch`, `Base`, `PR`, and child Ticket index metadata;
  - the requirement goal, milestones, completion rule, and delivery contract.

Each child Ticket Issue retains its Plan link, `Status`, `Dependencies`, goal,
scope, acceptance criteria, Slice plan, and validation contract. It does not
own `Branch`, `Base`, `PR`, or a separate merge.

The Plan Issue contains the overall requirement plan and links to every Ticket
Issue. Chat output contains convenience links only.
`docs/Repo_Current_State.md` may link to the active Issue but must not become a
duplicate plan or backlog.

Search for stable plan/ticket markers before creating Issues so retries reuse
existing records. If the GitHub connector, repository target, authentication,
or required write fails, mark the operation blocked and stop; do not fall back
to local Markdown or an unpersisted chat response.

Update the Plan as work progresses: `in_progress` when its branch starts,
`blocked` for a blocking dependency or environment problem, `in_review` when
the single Plan PR is opened, and `done`/closed only after that PR is verified
merged. Update child Ticket status and acceptance evidence during execution;
set all child Tickets to `done` and close them with the Plan after the one
merge.

## Branch per plan

Before implementation, create or resume one Plan branch for every requirement.
Use `<type>/<plan-id>-<short-description>` and create it from the updated
default branch. Ticket dependencies are completed and validated on this branch;
they do not require prerequisite Ticket merges. Keep the Plan's implementation,
tests, and related documentation on this branch; all Tickets and internal
Slices share it.

Verify the current branch and working tree before editing and preserve
unrelated or uncommitted work. Parallel workers use isolated worktrees or
return patches/findings for integration on the Plan branch; never create a
second delivery branch for a Ticket. Before committing and pushing, complete
the Plan's acceptance and relevant integration checks. After creating or
updating the Plan PR, invoke `pr-review` without waiting for user confirmation.
A passing Plan is ready for merge, not delivered; on `BLOCKED`, fix findings and
repeat Test, applicable Redaction, Commit, Push, and `pr-review` before the one
merge. The Plan Issue and implementation branch are a one-to-one pair; record
and verify the Plan's `Branch`/`Base` values, and require the Plan PR head/base
to match them.

## Optional delegation gate

After the Plan branch exists and before or during implementation, the main
agent may use bounded delegation when it materially improves speed, context
isolation, or review quality. A single-agent execution remains the default.
Delegation does not create a second delivery path or bypass any PR gate.

Delegate only a bounded, independently executable task. Good candidates are
repository exploration, independent research, test or regression analysis, or
an isolated implementation Slice. Keep dependent or
overlapping work sequential; parallel write tasks must not touch the same
files, interfaces, schemas, migrations, or shared configuration.

Every delegated task includes its goal, scope and exclusions, ownership
boundary, dependencies, acceptance criteria, validation, and expected result
summary. Workers return findings, changes, test results, and unresolved risks,
not raw logs. Prefer one delegation level and keep integration and final
judgment with the main agent.

## Slice execution and verification

Use test-first development for behavior changes, bug fixes, regressions, API
behavior, core business logic, data processing, and high-risk code when a
meaningful failing test can be produced. For docs, configuration, dependency
updates, styling, typo fixes, simple refactors, and exploratory work, use
direct focused validation without forcing RED/GREEN.

Choose one bounded verification level:

| Level | Use |
|---|---|
| `minimal` | Tiny changes, docs, configuration, styling, simple scripts. |
| `focused` | Default; checks directly tied to Slice acceptance criteria. |
| `regression` | Bug fixes, cross-module changes, demonstrated regression risk. |
| `full` | High-risk, release gates, or explicit requirements. |

Run the smallest set that provides sufficient evidence. Stop after the chosen
level passes unless acceptance criteria, failure evidence, affected boundaries,
release requirements, or the user justify escalation. Report the level,
commands, result, evidence, and escalation reason.

## Pull-request review

After the publication Skill reports `PR ready`, invoke the
[`pr-review`](../../skills/pr-review/SKILL.md) Skill. It is the single merge
decision gate and returns `PASS` or `BLOCKED`; its runtime instructions own the
blocking criteria, review scope, and fix loop. The recoverable runner and its
execution reference are implementation details of that Skill.

An optional project-scoped supplemental reviewer is outside the default path
and may be used only when an explicitly high-risk change calls for it.

Read `docs/Repo_Current_State.md` at the start of planning. After merge, source
branch deletion, and default-branch synchronization, update it when verified
project state changed. Use it as a compact recovery point for current focus,
implemented behavior, in-progress Slice, known failures, constraints, and the
next Slice. It is not a session transcript, full backlog, or test report.

## Post-delivery workflow evaluation

Run one lightweight retrospective after delivery and after any requested
deployment result is known. It evaluates the workflow rather than re-reviewing
the code, so it is not a merge gate.

Look only for evidence from the completed work:

- avoidable rework, failed assumptions, or repeated review findings;
- planning, context loading, or delegation that was too heavy or too weak;
- tests or redaction that were disproportionate to risk;
- repeated manual work that should be automated;
- unclear, duplicated, or missing workflow instructions.

Record a compact result:

```text
Keep: what worked and should remain
Improve: one highest-value reusable improvement, or none
Evidence: concrete event from this delivery
Action: none | follow-up change | report for later
```

Apply self-improvement only when the lesson is reusable and evidence-backed.
Prefer simplifying or removing redundant steps before adding new process. Never
weaken branch/PR, `pr-review`, redaction, security, permission, or release
gates for convenience.

A low-risk improvement that stays within the existing workflow intent may start
automatically as one separate follow-up repository change. It must begin from
the updated default branch and repeat the normal branch, validation, redaction,
PR, `pr-review`, and merge lifecycle. Policy, permission, security,
release behavior, and broad project-scope changes are reported instead of
self-applied.

Only one automatic follow-up improvement may be created per delivered user
request. Its own evaluation cannot recursively create another automatic
improvement. If there is no meaningful evidence-backed improvement, finish
without inventing work or backlog entries.

## Output classification and redaction

Stage the intended change, then invoke `data-document-redaction` and follow
[redaction.md](redaction.md) before creating the commit. Repeat the scan after
any blocking review fix that changes staged content, before the next commit.

The scan returns `pass`, `findings`, `needs_review`, `noop`, or `error`. Only
`pass` and `noop` continue; record the inspected scope and skip only when the
staged change carries no sensitive surface. `findings`, `needs_review`, and
`error` stop the boundary transition until the reported gap is resolved.

The gate covers the staged commit set only. Document, PDF, Office, OCR,
repository-wide, and non-Git export sanitization are out of scope and need
project-specific tooling and review.

## Completion order

`Understand -> Plan -> Record Plan + Tickets + Slices -> Plan Branch -> Implement -> Test -> Redaction if applicable -> Commit -> Push -> Create/Update Plan PR -> pr-review -> Fix/Test/Redaction/Commit/Push/pr-review loop -> Merge once -> Delete branch -> Update main -> Close Plan + Tickets -> State/Docs -> Optional external release handoff (outside this workflow) -> Evaluate workflow -> optional one bounded follow-up improvement`

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
