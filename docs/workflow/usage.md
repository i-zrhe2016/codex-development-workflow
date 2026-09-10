# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for repository work. It
keeps planning at the Plan/Ticket/Slice levels, but uses one delivery path for
every change type.

## Staged workflow

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
  -> Fix / Test / Redaction / Commit / Push / Review loop when blocked
  -> Merge PR
  -> Delete branch
  -> Update main
  -> Close Ticket
  -> Update State / Docs
  -> Deploy if needed
```

The pipeline is identical for Docs, Code, Tests, Config, Refactor, Bugfix,
Feature, Dependency, and CI/CD changes. Planning depth, test level, and whether
a Ticket is useful may vary; no category may direct-push around the PR gate.

## Ticket-to-Slice hierarchy

When a request is large, crosses multiple behaviors, or has dependencies, use
this order:

1. Split the requirements into independently reviewable behavior Tickets.
2. Define each Ticket's scope, dependencies, acceptance boundary, and Issue.
3. Split each Ticket into dependency-ordered, independently verifiable
   Slices.

All Slices for one Ticket share that Ticket's implementation branch. Ticket
dependencies determine branch readiness; Slice dependencies determine the
execution order within the branch. A single-behavior request may remain one
Slice without a Ticket or Issue, but it still requires a feature branch and PR.

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
durable source of truth. Create or update one parent plan Issue and one Issue
per ticket before implementation branches start. Each ticket Issue retains:

- `Status`: `planned`, `in_progress`, `blocked`, `in_review`, or `done`;
- `Branch`, `Base`, `Dependencies`, and `PR` metadata;
- the goal, scope, acceptance criteria, and validation contract.

The plan Issue contains the overall plan and links to the ticket Issues. Chat
output contains convenience links only. `docs/Repo_Current_State.md` may link
to the active Issue but must not become a duplicate plan or backlog.

Search for stable plan/ticket markers before creating Issues so retries reuse
existing records. If the GitHub connector, repository target, authentication,
or required write fails, mark the operation blocked and stop; do not fall back
to local Markdown or an unpersisted chat response.

Update each Issue as work progresses: `in_progress` when branch work starts,
`blocked` for a blocking dependency or environment problem, `in_review` when a
PR is opened, and `done`/closed only after the PR is verified merged.

## Branch per ticket

Before implementation, create or resume a feature branch for every change.
Ticketed work uses one branch per Ticket named
`<type>/<ticket-id>-<short-description>`; a single Slice without a Ticket uses
`<type>/<short-description>`. Create branches from the updated default branch,
and start dependent Ticket branches only after their prerequisites are merged.
Keep a Ticket's implementation, tests, and related documentation on its branch;
internal Slices share it.

Verify the current branch and working tree before editing and preserve
unrelated or uncommitted work. Parallel ticket workers use separate Git
worktrees and branches; never switch branches in a working directory shared by
active workers. Before committing and pushing, complete the change's
acceptance and relevant integration checks. After creating or updating its PR,
start Automatic Review without waiting for user confirmation. A passing change
is ready for merge, not delivered; fix findings and repeat Test, applicable
Redaction, Commit, Push, and Automatic Review before merging. For Ticketed
work, the Ticket Issue and implementation branch are a one-to-one pair: record
and verify the Issue's `Branch`/`Base` values, and require the PR head/base to
match them.

## Optional delegation gate

After the feature branch exists and before or during implementation, the main
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

## Review and recovery

Automatic Review is the built-in `codex review` command. It is mandatory after
the PR is created or updated and before merge, not an internal Slice or pre-PR
stage. Use the complete PR diff, branch boundary, and available CI results;
run `codex review --base <base-branch>` immediately without waiting for user
confirmation. Blocking findings repeat Fix -> Test -> Redaction if applicable
-> Commit -> Push -> `codex review` on the updated PR.

The first review covers the full PR. Batch each round's fixes, then review all
new commits against the last assessed head when their impact is bounded; verify
the original findings are resolved. Base/history changes, interface or security
boundary changes, cross-module behavior, and uncertain impact require full review.
Use the [recoverable review runner](../../skills/github-push-when-ready/references/review-execution.md)
to stream and retain logs, reuse matching results, and avoid duplicate processes.

The project-scoped `.codex/agents/reviewer.toml` is optional supplemental
read-only analysis. It may be invoked from an interactive Codex session, but it
never replaces the mandatory `codex review` gate.

Read `docs/Repo_Current_State.md` at the start of planning. After merge, source
branch deletion, and default-branch synchronization, update it when verified
project state changed. Use it as a compact recovery point for current focus,
implemented behavior, in-progress Slice, known failures, constraints, and the
next Slice. It is not a session transcript, full backlog, or test report.

## Output classification and redaction

Classify the complete output set before committing and before every separate
sharing, export, upload, or publication boundary. Repeat the scan after any
blocking review fix before the next commit. Include
source, docs, logs, configs, images, screenshots, exports, filenames, and
metadata.

Record recipient/environment, purpose, required utility, and whether controlled
reversibility is allowed. Default to non-reversible handling.

If no potentially sensitive surface exists, record the inspected scope and skip
reason. Otherwise invoke `data-document-redaction` and follow
[redaction.md](redaction.md). Only `pass` advances; `needs_review` and
`blocked` stop the boundary transition.

## Completion order

`Understand -> Plan -> Slice/Ticket if needed -> Branch -> Implement -> Test -> Redaction if applicable -> Commit -> Push -> Create/Update PR -> Automatic Review -> Fix/Test/Redaction/Commit/Push/Review loop -> Merge -> Delete branch -> Update main -> Close Ticket -> State/Docs -> Deploy if needed`

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
