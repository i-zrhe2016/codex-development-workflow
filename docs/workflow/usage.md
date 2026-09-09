# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for repository work. It
keeps architecture and scope at the Plan/Slice level while keeping validation
inside each Slice.

## Staged workflow

```text
Requirement -> Classify -> Understand -> Plan -> Slice
           -> Persist plan/tickets to GitHub Issues -> Delegate if useful
           -> Execute/Test -> Next Slice? -> Integration tests -> Review
           -> State / Docs -> Redaction if needed -> Commit / Push
           -> Optional Deploy / Verify / Rollback
```

- **Tiny:** use a concise plan and one implicit Slice.
- **Normal:** plan the relevant area and execute one or more focused Slices.
- **Complex:** use `plan-to-ticket` for dependency-ordered Slices, evaluate the
  delegation gate, and load only the context required by each Slice.

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

## Optional delegation gate

After `Plan -> Slice` and before `Execute/Test`, the main agent asks whether
delegation materially improves speed, context isolation, or review quality. A
single-agent execution remains the default.

Delegate only a bounded, independently executable task. Good candidates are
repository exploration, independent research, test or regression analysis, an
isolated implementation Slice, and independent review. Keep dependent or
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

Review is owned by the main agent and covers the integrated result, not every
individual Slice. After integration/regression checks, the main agent may ask
the read-only `reviewer` for an independent check, then reviews the final safe
diff and makes the decision. A blocking finding requires an affected test
rerun; repeat review when the fix materially changes behavior.

`codex review --uncommitted` is the built-in diff-review path; it does not select
the project-scoped custom reviewer. To use `.codex/agents/reviewer.toml`, ask an
interactive Codex session from the project root to use the `reviewer` subagent
and wait for its read-only findings before the main agent makes the decision.

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

`Integration tests -> Self review -> Repo state/docs if needed -> Output classification -> Redaction if needed -> Commit/Push -> Optional Deploy/Verify/Rollback`

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
