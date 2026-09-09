# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for repository work. It
keeps architecture and scope at the Plan/Ticket/Slice levels while keeping
validation inside each Slice.

## Staged workflow

```text
Requirement -> Classify -> Understand -> Plan -> Ticket(s) if needed
           -> Slice(s) per Ticket
           -> Persist plan/tickets to GitHub Issues -> Delegate if useful
           -> Create/resume ticket branch
           -> Execute/Test -> Next Slice? -> Integration tests
           -> State / Docs -> Redaction if needed -> Commit / Push -> Open PR
           -> Review -> Fix findings / Re-test -> Merge -> Close ticket
           -> Optional Deploy / Verify / Rollback
```

- **Tiny:** use a concise plan and one implicit Slice without Ticket overhead.
- **Normal:** create the smallest behavior Ticket when the work needs multiple
  steps, then split it into one or more focused Slices.
- **Complex:** use `plan-to-ticket` to split the requirements into
  dependency-ordered behavior Tickets first, then split each Ticket into its
  Slices; evaluate the delegation gate and load only the context required by
  each Slice.

## Ticket-to-Slice hierarchy

When a request is large, crosses multiple behaviors, or has dependencies, use
this order:

1. Split the requirements into independently reviewable behavior Tickets.
2. Define each Ticket's scope, dependencies, acceptance boundary, and Issue.
3. Split each Ticket into dependency-ordered, independently verifiable
   Slices.

All Slices for one Ticket share that Ticket's implementation branch. Ticket
dependencies determine branch readiness; Slice dependencies determine the
execution order within the branch. A tiny request may remain one implicit
Slice without a Ticket or Issue.

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

Before implementation, create or resume one branch per ticket using
`<type>/<ticket-id>-<short-description>`. Create new ticket branches from the
updated default branch, and start dependent tickets only after their
prerequisites are merged. Keep the ticket's implementation, tests, and related
documentation on that branch; internal implementation steps share it.

Verify the current branch and working tree before editing and preserve
unrelated or uncommitted work. Parallel ticket workers use separate Git
worktrees and branches; never switch branches in a working directory shared by
active workers. Before committing and pushing, complete the ticket's
acceptance and relevant integration checks. After opening its PR, perform the
single review of its complete diff before merge. A passing ticket is ready to
open a PR, not delivered; fix findings and re-test before merging, then close
the ticket and follow the existing publication skill's cleanup procedure. The
ticket Issue and implementation branch are a one-to-one pair: record and verify
the Issue's `Branch`/`Base` values, and require the PR head/base to match them.

## Optional delegation gate

After `Plan -> Ticket -> Slice` and before `Execute/Test`, the main agent asks
whether delegation materially improves speed, context isolation, or review
quality. A single-agent execution remains the default.

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

Review is one main-agent-owned stage after the ticket PR is opened and before
merge, not an internal Slice or pre-PR stage. All Slices within the ticket must
pass before the PR is opened. Use the complete PR diff, branch boundary, and
available CI results; choose either the built-in `codex review` or the
project-scoped `reviewer` as the single review path. When multiple tickets come
together, add broader integration/regression checks across them in addition to
each ticket's own checks. Fix findings and rerun affected tests before merge;
do not add a second routine review.

`codex review --base main` is the built-in PR diff-review path; it does not
select the project-scoped custom reviewer. To use
`.codex/agents/reviewer.toml`, ask an interactive Codex session from the
project root to use the `reviewer` subagent as the single review path and wait
for its read-only findings before the main agent makes the decision.

Read `docs/Repo_Current_State.md` at the start of planning and update it after
meaningful verified work. Use it as a compact recovery point for current focus,
implemented behavior, in-progress Slice, known failures, constraints, and the
next Slice. It is not a session transcript, full backlog, or test report.

## Output classification and redaction

Classify the complete final output set before staging or committing and before
every separate sharing, export, upload, or publication boundary. Include
source, docs, logs, configs, images, screenshots, exports, filenames, and
metadata.

Record recipient/environment, purpose, required utility, and whether controlled
reversibility is allowed. Default to non-reversible handling.

If no potentially sensitive surface exists, record the inspected scope and skip
reason. Otherwise invoke `data-document-redaction` and follow
[redaction.md](redaction.md). Only `pass` advances; `needs_review` and
`blocked` stop the boundary transition.

## Completion order

`Ticket checks -> Broader integration when needed -> Repo state/docs -> Output classification -> Redaction if needed -> Commit/Push -> Open PR -> Review -> Fix findings/Re-test -> Merge -> Close ticket -> Optional Deploy/Verify/Rollback`

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
