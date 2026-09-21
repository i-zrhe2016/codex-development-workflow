# Architecture Overview

> Type: Architecture
> Status: Active
> Scope: Component responsibilities, development lifecycle, and installation flow of this repository's workflow package

## Scope

This repository packages a main-agent-led development-workflow orchestrator for
Codex and Claude Code with optional bounded delegation and its specialist
skills. The orchestrator owns stage routing and quality gates; specialist
procedures remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Coordinates the single Requirement-to-Plan-to-PR-to-Merge lifecycle, Plan/Ticket/Slice decomposition, bounded verification, and delivery gates. |
| Delegation | Optional bounded implementation work after branch creation; it never creates a second delivery path or bypasses the PR gate. |
| Subagent selection | The host picks the subagent from each agent definition's `description`; no document maps a task class to an agent. |
| `.codex/config.toml` | Enables subagents and caps spawned-agent concurrency at three for this project (Codex only). |
| `plan-to-ticket` | Creates exactly one Plan for every requirement, splits it into behavior Tickets, decomposes each Ticket into dependency-ordered Slices with explicit scope and acceptance criteria, then persists the Plan and child Ticket Issues before branch work. |
| GitHub Issues connector | Stores the durable Plan/Ticket records; the Plan owns status, dependency index, branch, base, and PR metadata while child Tickets own behavior and acceptance metadata. |
| `test-workflow` | Maps acceptance criteria to evidence, selects mandatory risk dimensions, and closes the Test Quality Gate only when required verification is satisfied. |
| `repo-current-state` | Maintains the compact, verified recovery point after merge, branch cleanup, and default-branch synchronization. |
| `repo-documentation` | Governs documentation as one canonical document per fact: the documentation impact check, canonical ownership, the documentation index, duplicate and orphan detection, document lifecycle, and the diagram policy. |
| `docs/skills/` | Specialist README, architecture, usage, and supporting documentation. |
| `scripts/install-all.sh` | Installs the root orchestrator and local specialist bundles. |
| `references/skill-map.md` | Maps each managed bundle to its local source and both host destinations. |
| `data-document-redaction` | Scans the files staged for the next commit before publication and repeats the scan after subsequent fixes that change staged content. |
| `github-push-when-ready` | Guards feature-branch publication through Commit, Push, and PR readiness. |

The main agent centrally owns requirements, architecture, planning, dependency
ordering, integration, and final judgment. Bounded delegation may route
independent exploration, testing, or isolated implementation to subagents; the
host selects which one, and [`AGENTS.md`](../../AGENTS.md#multi-agent-delegation)
owns the policy. Dependent or overlapping work remains sequential, and the main
agent must not duplicate active delegated work.

## Development process

### Component responsibilities and records

![Workflow components and authorities](../diagrams/components.svg)

Source: [`components.puml`](../diagrams/components.puml)

Skills are main-agent procedures, not independently running services. The
diagram separates lifecycle orchestration, specialist responsibilities, GitHub
Issues as Plan/Ticket authority, GitHub as publication surface, and repository
documentation as persisted project knowledge.

### End-to-end lifecycle

![End-to-end workflow lifecycle](../diagrams/architecture.svg)

Source: [`architecture.puml`](../diagrams/architecture.puml)

### Macro stages

```text
Requirement
  -> Understand repo
  -> Plan
  -> Record Plan + Tickets + Slices
  -> Create Plan branch
  -> Implement all Plan Tickets
  -> Test Quality Gate
  -> Documentation impact check
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> Merge the Plan PR once
  -> Delete branch
  -> Update main
  -> Close Plan + Tickets
  -> Update State / Docs
  -> If separately authorized: external release handoff (outside this workflow)
  -> Evaluate workflow
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

![Plan / Ticket lifecycle](../diagrams/ticket-lifecycle.svg)

Source: [`ticket-lifecycle.puml`](../diagrams/ticket-lifecycle.puml)

![Slice implementation and validation loop](../diagrams/ticket-slice-loop.svg)

Source: [`ticket-slice-loop.puml`](../diagrams/ticket-slice-loop.puml)

Dependency waits resume only after fresh evidence; a failed Slice returns to
diagnosis and affected validation, while a design conflict returns to planning.
A failed validation or publication step returns to the recorded failed stage, never a later gate.
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

### Delegation

Delegation is optional and may occur after branch creation during
implementation. The main agent delegates only tasks with a clear goal, scope
and exclusions, ownership boundary, dependencies, acceptance criteria,
validation, and expected result summary. Parallel write tasks must not share
files, interfaces, schemas, migrations, or configuration. Delegation never
bypasses Test, Redaction when applicable, Commit, Push, PR, or
Merge. Prefer a single delegation level. The host selects the subagent by
`description`; the policy lives in
[`AGENTS.md`](../../AGENTS.md#multi-agent-delegation).

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


### Host-specific project configuration

Each host reads its own agent definitions. 
### Staged-output redaction gate

Run the gate on the files staged for the next commit and repeat it after any
subsequent fix that changes staged content. The scan reports `pass`,
`findings`, `needs_review`, `noop`, or `error`; only `pass` and `noop` continue,
and a recorded skip is allowed only when the staged change carries no sensitive
surface.

The packaged specialist covers the staged commit set only. Document, PDF,
Office, OCR, repository-wide, and non-Git export sanitization are out of scope
and need project-specific tooling and review.

## Installation flow

1. Obtain a checkout of this repository and run `scripts/install-all.sh` with `--target codex` (default) or `--target claude`.
2. The installer validates each local `SKILL.md` and copies the configured bundle into the target destination (`${CODEX_HOME:-$HOME/.codex}/skills` or `$HOME/.claude/skills`) or `--dest PATH`.
3. Existing marked skills are skipped unless `--update` is used; unmarked paths
   are preserved unless `--update --adopt-legacy` explicitly moves them to a
   recoverable backup first.
4. Restart the host to discover installed skills.

The installer and [`references/skill-map.md`](../../references/skill-map.md)
must remain aligned. The
[installation and update guide](../deployment/installation.md) owns the
procedure.

## Boundaries

- The orchestrator defines stages and gates; specialist skills define detailed procedures.
- Every requirement has exactly one Plan with at least one Ticket; a single-behavior requirement is one Ticket with one implicit Slice, and every Plan uses one branch and PR.
- Tests provide evidence inside a Slice; the Plan PR remains the publication and merge boundary.
- `Repo_Current_State.md` is the recovery point, not a session transcript or full backlog.
- `repo-documentation` owns documentation governance; `repo-current-state` owns
  only the recovery snapshot.
- Redaction is conditional and scoped to the staged commit set; it is not a mandatory transformation of every artifact.
- State / Docs are updated after merge, source-branch deletion, and default-branch synchronization.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Specialist skills are vendored under `skills/` and updated through this repository's normal version-control process.
