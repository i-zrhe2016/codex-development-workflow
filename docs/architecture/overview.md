# Architecture Overview

## Scope

This repository packages a main-agent-led Codex development-workflow
orchestrator with optional bounded delegation and its specialist skills. The
orchestrator owns stage routing and quality gates; specialist procedures
remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Coordinates the single Requirement-to-Plan-to-PR-to-Merge lifecycle, Plan/Ticket/Slice decomposition, bounded verification, and delivery gates. |
| Delegation | Optional bounded implementation work after branch creation; it never creates a second delivery path or bypasses the PR gate. |
| `explorer` / `worker` | Built-in read-heavy exploration and execution roles used only for delegated, bounded tasks. |
| `.codex/agents/reviewer.toml` | Optional project-scoped supplemental reviewer for explicitly high-risk changes; it is outside the default path. |
| `.codex/config.toml` | Enables subagents and caps spawned-agent concurrency at three for this project. |
| `plan-to-ticket` | Creates exactly one Plan for every requirement, splits it into behavior Tickets, decomposes each Ticket into dependency-ordered Slices with explicit scope and acceptance criteria, then persists the Plan and child Ticket Issues before branch work. |
| GitHub Issues connector | Stores the durable Plan/Ticket records; the Plan owns status, dependency index, branch, base, and PR metadata while child Tickets own behavior and acceptance metadata. |
| `test-workflow` | Runs the selected verification level and reports bounded evidence. |
| `repo-current-state` | Maintains the compact, verified recovery point after merge, branch cleanup, and default-branch synchronization. |
| `context-efficiency` | Optional context-loading aid for large or unfamiliar repositories; not a workflow stage. |
| `auto-deploy` | Discovers the deployment contract, gates automatic releases, verifies health, and coordinates safe rollback. |
| `docs/skills/` | Specialist README, architecture, usage, and supporting documentation. |
| `scripts/install-all.sh` | Installs the root orchestrator and local specialist bundles. |
| `references/skill-map.md` | Maps each managed bundle to its local source and Codex destination. |
| `data-document-redaction` | Scans the files staged for the next commit before publication and repeats the scan after blocking review fixes that change staged content. |
| `github-push-when-ready` | Guards feature-branch publication through Commit, Push, and PR readiness. |
| `pr-review` | Owns the single PR merge decision and returns `PASS` or `BLOCKED`. |

The main agent centrally owns requirements, architecture, planning, dependency
ordering, integration, and final judgment. The optional Delegation Gate may
route independent exploration, testing, or isolated implementation to bounded
workers. Supplemental review is outside the default path and requires explicit
high-risk scope. Dependent or overlapping work remains sequential, and the
main agent must not duplicate active delegated work.

## Development process

### Component responsibilities and records

![Component responsibilities and durable records](../diagrams/components.svg)

Editable source: [`components.puml`](../diagrams/components.puml). Skills are
main-agent procedures, not independently running services. Solid arrows show
invocation or record ownership; the main agent retains integration and gate decisions.

### End-to-end lifecycle

![Codex Development Workflow development process](../diagrams/architecture.svg)

Editable source: [`architecture.puml`](../diagrams/architecture.puml).

### Macro stages

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
  -> Deploy if needed
```

All change types—Docs, Code, Tests, Config, Refactor, Bugfix, Feature,
Dependency, and CI/CD—use the same Plan-branch and PR lifecycle. Planning
depth and test level may vary, but no category may direct-push around the PR
gate. Every requirement is recorded as exactly one Plan Issue with one or more
child Ticket Issues before branch work; split Ticket Slices only after each
boundary is clear, and treat a single-behavior requirement as one Plan with one
Ticket and one implicit Slice.

If `plan-to-ticket` is used, it persists one Plan Issue and all child Ticket
Issues before the Plan branch is created. Each Slice loads only the context
needed for its acceptance criteria. A wrong design assumption returns to Plan
or causes a Slice split.

### Ticket-to-Slice hierarchy

The detailed Plan/Ticket lifecycle is split into three linked views so each
return edge has a clear scope and exit condition:

![Ticket planning and dependency loop](../diagrams/ticket-lifecycle.svg)

Source: [`ticket-lifecycle.puml`](../diagrams/ticket-lifecycle.puml).

![Slice implementation and validation loop](../diagrams/ticket-slice-loop.svg)

Source: [`ticket-slice-loop.puml`](../diagrams/ticket-slice-loop.puml).

![Plan PR fix and review loop](../diagrams/ticket-review-loop.svg)

Source: [`ticket-review-loop.puml`](../diagrams/ticket-review-loop.puml).

Dependency waits resume only after fresh evidence; a failed Slice returns to
diagnosis and affected validation, while a design conflict returns to planning.
PR findings are fixed in one batch on the same branch and republished before
review. Recovery returns to the recorded failed stage, never a later gate.
Only the single verified Plan merge permits `done` and Plan/Ticket Issue closure.
There is no outer per-Ticket merge loop. `planned`, `in_progress`, `blocked`,
and `in_review` remain open states; `Status` is workflow metadata, not a claim
that GitHub provides these workflow states automatically.

A Plan is one coherent requirement or feature delivery boundary and owns one branch, PR, and merge. A
Ticket is an independently reviewable behavior or capability boundary inside
that Plan. A Slice is an execution-ready unit within a Ticket, with its own
scope, dependencies, acceptance criteria, test strategy, test level, test
cases, and validation command. Establish the Plan boundary, then Ticket
boundaries, then dependency-ordered Slices. All Tickets and Slices for one Plan
share its implementation branch; Ticket dependencies control work order within
the Plan, while Slice dependencies control order within a Ticket. Tiny work is
one Plan with one Ticket and one implicit Slice.

### Persistent ticket authority

GitHub Issues are the sole durable authority for Plans and Tickets created by
`plan-to-ticket`. Every requirement has exactly one Plan Issue holding the overall plan and
linking to one or more child Ticket Issues. The Plan retains `Status`, `Branch`,
`Base`, `PR`, and completion metadata; each child Ticket retains its Plan link,
goal, scope, dependencies, acceptance criteria, validation, and Slice plan but
does not own a branch or PR. The workflow blocks when required Issue reads or
writes fail; it does not create a local Markdown mirror or treat chat output as
completion.

`Repo_Current_State.md` remains a compact recovery pointer to the active Issue,
not a backlog or second ticket database.

### Plan branch

Every requirement owns one Plan branch created or resumed before editing, after its Plan
and child Ticket Issues exist. The Plan branch is named
`<type>/<plan-id>-<short-description>`. Ticket dependencies are completed and
validated on that branch; no prerequisite Ticket merge is required. Parallel
workers use isolated worktrees or return patches/findings for integration, and
never create a second delivery branch. The Plan Issue is the one-to-one owner
of its branch: record `Branch` and `Base` before editing, set Plan
`Status: in_progress` when work starts, and require the Plan PR head/base to
match those fields.

### Delegation gate

Delegation is optional and may occur after branch creation during
implementation. The main agent delegates only tasks with a clear goal, scope
and exclusions, ownership boundary, dependencies, acceptance criteria,
validation, and expected result summary. Parallel write tasks must not share
files, interfaces, schemas, migrations, or configuration. Delegation never
bypasses Test, Redaction when applicable, Commit, Push, PR, `pr-review`, or
Merge. Prefer a single delegation level.

### Slice execution

```text
Acceptance criteria -> Test strategy -> Minimal change
                    -> Focused validation -> Fix / Refactor
                    -> Slice complete
```

Test-first is preferred for meaningful behavioral changes, bug fixes,
regressions, API behavior, core business logic, data processing, and high-risk
code. It is not forced for documentation, configuration, dependency updates,
styling, typo fixes, simple refactors, or exploratory work.

### Bounded verification

| Level | Purpose |
|---|---|
| `minimal` | Tiny and non-behavioral changes. |
| `focused` | Default evidence for one Slice. |
| `regression` | Bug fixes and cross-module risk. |
| `full` | High-risk or release verification. |

After the selected level passes, stop unless the acceptance criteria, failure
evidence, affected boundaries, release requirements, or the user justify an
escalation.

### Pull-request review gate

![Open Code Review execution and recovery](../diagrams/review-execution.svg)

Editable source: [`review-execution.puml`](../diagrams/review-execution.puml).

`pr-review` is invoked immediately after `github-push-when-ready` reports a
created or updated PR ready. It is the only policy owner for the merge decision:
`PASS` permits merge, while `BLOCKED` returns to the fix/test/redaction/commit/
push loop. The [`pr-review` Skill](../../skills/pr-review/SKILL.md) defines
blocking criteria and when a complete or bounded review is appropriate; the
[runner reference](../../skills/pr-review/references/review-execution.md)
documents only execution recovery mechanics.

The runner invokes Alibaba Open Code Review's `ocr review` command and keeps its
logs and state local. The first review covers the complete PR, while eligible
bounded fixes may use the runner's incremental execution. Current tests and CI
remain separate evidence and must pass before merge.

`Understand -> Plan -> Record Plan + Tickets + Slices -> Plan Branch -> Implement -> Test -> Redaction if applicable -> Commit -> Push -> Create/Update Plan PR -> pr-review -> Fix/Test/Redaction/Commit/Push/pr-review loop when blocked -> Merge once -> Delete branch -> Update main -> Close Plan + Tickets -> State/Docs -> Deploy if needed`

### Project-scoped Codex configuration

`.codex/config.toml` enables subagents and limits this project to three
concurrently open spawned-agent threads, excluding the main thread.
`.codex/agents/reviewer.toml` provides an optional supplemental reviewer only
for explicitly high-risk changes; it is not part of the default PR path. The
installer copies managed skills only; these project-scoped files remain in the
checkout where Codex runs.

### Staged-output redaction gate

Run the gate on the files staged for the next commit and repeat it after any
blocking review fix that changes staged content. The scan reports `pass`,
`findings`, `needs_review`, `noop`, or `error`; only `pass` and `noop` continue,
and a recorded skip is allowed only when the staged change carries no sensitive
surface.

The packaged specialist covers the staged commit set only. Document, PDF,
Office, OCR, repository-wide, and non-Git export sanitization are out of scope
and need project-specific tooling and review.

## Installation flow

1. Obtain a checkout of this repository and run `scripts/install-all.sh`.
2. The installer validates each local `SKILL.md` and copies the configured bundle into `${CODEX_HOME:-$HOME/.codex}/skills` or `--dest PATH`.
3. Existing marked skills are skipped unless `--update` is used; unmarked paths
   are preserved unless `--update --adopt-legacy` explicitly moves them to a
   recoverable backup first.
4. Restart Codex to discover installed skills.

The installer and [`references/skill-map.md`](../../references/skill-map.md)
must remain aligned.

## Boundaries

- The orchestrator defines stages and gates; specialist skills define detailed procedures.
- Every requirement has exactly one Plan with at least one Ticket; a single-behavior requirement is one Ticket with one implicit Slice, and every Plan uses one branch and PR.
- Tests provide evidence inside a Slice; `pr-review` is the mandatory PR-stage merge gate after the branch is published.
- `Repo_Current_State.md` is the recovery point, not a session transcript or full backlog.
- Redaction is conditional and scoped to the staged commit set; it is not a mandatory transformation of every artifact.
- State / Docs are updated after merge, source-branch deletion, and default-branch synchronization.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Specialist skills are vendored under `skills/` and updated through this repository's normal review and version-control process.
