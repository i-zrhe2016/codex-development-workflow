# Architecture Overview

> Type: Architecture
> Status: Active
> Scope: Component responsibilities, development lifecycle, and installation flow of this repository's workflow package

## Scope

This repository packages a main-agent-led development-workflow orchestrator for
Codex and Claude Code with a fixed workflow topology and adaptive multi-agent
execution. The orchestrator owns stage routing and quality gates; specialist
procedures remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Routes each request to the stage workflow that owns it — `plan-workflow`, `develop-workflow`, `verify-workflow`, `publish-workflow`, or `integrate-workflow` — carries the invariants shared by all stages, and provides the optional full orchestration for an explicitly authorized end-to-end delivery. |
| Adaptive execution waves | The main agent schedules dependency-ready Tickets with fresh implementation and independent verification workers, then integrates evidence before the next gate. |
| Subagent selection | The main agent and host choose the best available built-in or project-defined subagent from the task contract and agent description; no task class is hard-coded to a named agent. |
| `.codex/config.toml` and `.codex/agents/` | Project-local coordinator/worker configuration and scoped agent definitions; [installation.md](../deployment/installation.md#codex-model-routing) owns model defaults, escalation and dispatch policy. |
| `plan-to-ticket` | Defines an explicitly scoped delivery batch as one Plan, splits its functionalities into behavior Tickets, and decomposes each Ticket into dependency-ordered Slices with explicit scope and acceptance criteria. It persists the Plan and child Ticket Issues before branch work when the work is complex, must survive a session boundary, or the user asks for a persisted plan. |
| GitHub Issues connector | Stores the durable Plan/Ticket records; the Plan owns status, dependency index, branch, base, and PR metadata while child Tickets own behavior and acceptance metadata. |
| `test-workflow` | Maps acceptance criteria to evidence, selects mandatory risk dimensions, and closes the Test Quality Gate only when required verification is satisfied. |
| `repo-current-state` | Maintains the compact, verified recovery point on the same Plan branch and PR as the work it describes. |
| `repo-documentation` | Governs documentation as one canonical document per fact: the documentation impact check, canonical ownership, the documentation index, duplicate and orphan detection, document lifecycle, and the diagram policy. |
| `docs/skills/` | Specialist README, architecture, usage, and supporting documentation. |
| `scripts/install-all.sh` | Installs the root orchestrator and local specialist bundles. |
| `references/skill-map.md` | Maps each managed bundle to its local source and both host destinations. |
| `data-document-redaction` | Scans the files staged for the next commit before publication and repeats the scan after subsequent fixes that change staged content. |
| `github-push-when-ready` | Guards feature-branch publication through Commit, Push, and PR readiness. |

The main agent centrally owns requirements, architecture, planning, dependency
ordering, execution-wave scheduling, integration, stage-gate decisions, and
final judgment. Fresh workers own every Ticket's implementation and
independent verification without changing the workflow topology.
[`AGENTS.md`](../../AGENTS.md#multi-agent-delegation) owns the
scheduling policy. Dependent or overlapping work remains sequential, and the
main agent must not duplicate active delegated work.

## Development process

### Overview diagrams

![Workflow components and responsibilities](../diagrams/components-overview.svg)

Source: [`components-overview.puml`](../diagrams/components-overview.puml)

![Plan Ticket Slice work decomposition](../diagrams/plan-ticket-slice.svg)

Source: [`plan-ticket-slice.puml`](../diagrams/plan-ticket-slice.puml)

![Risk-aware Test Quality Gate](../diagrams/test-quality-gate.svg)

Source: [`test-quality-gate.puml`](../diagrams/test-quality-gate.puml)

![Documentation and publication lifecycle](../diagrams/docs-publication-flow.svg)

Source: [`docs-publication-flow.puml`](../diagrams/docs-publication-flow.puml)

These PlantUML overviews summarize responsibilities and major decisions.
The detailed views below show exact workflow loops and lifecycle detail in the
same source format.

### Component responsibilities and records

![Detailed workflow components and authorities](diagrams/components.svg)

Source: [`diagrams/components.puml`](diagrams/components.puml)

Skills are procedures used by the coordinator and dispatched workers. The
diagram separates lifecycle orchestration, specialist responsibilities, GitHub
Issues as Plan/Ticket authority, GitHub as publication surface, and repository
documentation as persisted project knowledge.

### End-to-end lifecycle

![Detailed end-to-end workflow lifecycle](diagrams/architecture.svg)

Source: [`diagrams/architecture.puml`](diagrams/architecture.puml)

### Stage workflows

```text
Requirement
  -> plan-workflow        understand, design, decompose, persistence decision
  -> develop-workflow     implement to Development Complete
  -> verify-workflow      verification scope, level, and conclusion
  -> publish-workflow     docs/redaction, requested commit/push/PR boundary
  -> integrate-workflow   merge once, cleanup, close Issues, state and docs
  -> Evaluate workflow
```

Stage routing stops at the requested boundary. Local verified functionality is
a normal checkpoint; the user controls publication/merge timing and scope. See
[publication decisions](../workflow/usage.md#publication-decisions).
The full orchestration runs these stages only for an explicitly authorized
end-to-end delivery of the stated batch:

```text
Create Plan branch
  -> Implement all Plan Tickets
  -> Test Quality Gate
  -> Documentation impact check
  -> Update Repo_Current_State.md if represented state changed
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> Merge the PR once
  -> Delete branch
  -> Update main
  -> Validate PR-included State / Docs
  -> Close Plan + Tickets
  -> If separately authorized: external release handoff (outside this workflow)
  -> Evaluate workflow
```

Feature, Bug, Refactor, and Docs are profiles of these stages, not separate
workflows: they change verification breadth and whether a plan is persisted.
Planning depth and verification level may vary. Authorized commits and pushes
on a non-default branch may stop at their requested boundary; integration into
the default branch still requires the guarded PR and merge path. A requirement
that is complex, must survive a session boundary, or is explicitly requested as
a persisted plan is recorded as one Plan Issue with one or more child Ticket
Issues before branch work; split Ticket Slices only after each boundary is clear,
and treat a single-behavior requirement as one Plan with one Ticket and one
implicit Slice.

When `plan-to-ticket` persists a plan, it creates the Plan Issue and all child
Ticket Issues before the Plan branch is created. Each Slice loads only the
context needed for its acceptance criteria. A wrong design assumption returns to
Plan or causes a Slice split.

### Fixed topology and adaptive execution waves

```text
Fixed stages: plan -> develop -> verify -> publish -> integrate
Ticket execution: fresh implementer (all Slices) -> fresh verifier (all scenarios)
Final delivery verification: one fresh verifier checks the whole Plan branch/PR scope
Coordinator: readiness -> dispatch safe wave -> integrate evidence -> gates
```

Worker selection and concurrency adapt to dependencies and ownership. Ticket
roles and independent context remain mandatory under the canonical
[AGENTS.md policy](../../AGENTS.md#multi-agent-delegation); local development
checks do not replace independent verification.

### Ticket-to-Slice hierarchy

The detailed Plan/Ticket lifecycle is split into three linked views so each
return edge has a clear scope and exit condition:

![Plan / Ticket lifecycle](diagrams/ticket-lifecycle.svg)

Source: [`diagrams/ticket-lifecycle.puml`](diagrams/ticket-lifecycle.puml)

![Slice implementation and validation loop](diagrams/ticket-slice-loop.svg)

Source: [`diagrams/ticket-slice-loop.puml`](diagrams/ticket-slice-loop.puml)

Dependency waits resume only after fresh evidence; a failed Slice returns to
diagnosis and affected validation, while a design conflict returns to planning.
A failed validation or publication step returns to the recorded failed stage, never a later gate.
Only the single verified Plan merge permits `done` and Plan/Ticket Issue closure.
There is no outer per-Ticket merge loop. `planned`, `in_progress`, `blocked`,
and `in_review` remain open states; `Status` is workflow metadata, not a claim
that GitHub provides these workflow states automatically.

A Plan is an explicitly scoped delivery batch that may include multiple
independent functionalities and owns one branch and, if delivered, one PR and
merge. Before merge, new user-requested functionality appends as a Ticket;
after merge it starts a new Plan. An expanded Plan with an open PR retains
its URL but returns to `in_progress`, invalidating impacted readiness until
revalidation and an authorized PR update. See the
[Plan scope contract](../../skills/plan-to-ticket/SKILL.md#scope-and-sizing) and
[batch publication rules](../../skills/github-push-when-ready/SKILL.md#readiness-and-boundaries).
A Ticket is an independently reviewable behavior or capability boundary inside
that Plan. A Slice is an execution-ready unit within a Ticket, with its own
scope, dependencies, acceptance criteria, test strategy, test level, test
cases, and validation command. Establish the Plan boundary, then Ticket
boundaries, then dependency-ordered Slices. All Tickets and Slices for one Plan
share its implementation branch; Ticket dependencies control work order within
the Plan, while Slice dependencies control order within a Ticket. Tiny work is
one Plan with one Ticket and one implicit Slice.

### Persistent ticket authority

GitHub Issues are the sole durable authority for persisted Plans and Tickets
created by `plan-to-ticket`. A persisted plan has one Plan Issue holding the
overall plan and linking to one or more child Ticket Issues. The Plan retains `Status`, `Branch`,
`Base`, `PR`, and completion metadata; each child Ticket retains its Plan link,
goal, scope, dependencies, acceptance criteria, validation, and Slice plan but
does not own a branch or PR. The workflow blocks when required Issue reads or
writes fail; it does not create a local Markdown mirror or treat chat output as
completion.

`Repo_Current_State.md` remains a compact recovery pointer to the active Issue,
not a backlog or second ticket database.

### Plan branch

A persisted Plan owns one branch created or resumed before editing, after its
Plan and child Ticket Issues exist. The Plan branch is named
`<type>/<plan-id>-<short-description>`. Ticket dependencies are completed and
validated on that branch; no prerequisite Ticket merge is required. Parallel
workers use isolated worktrees or return patches/findings for integration, and
never create a second delivery branch. The Plan Issue is the one-to-one owner
of its branch: record `Branch` and `Base` before editing, set Plan
`Status: in_progress` when work starts, and require the Plan PR head/base to
match those fields.

### Ticket worker boundaries

The [canonical policy](../../AGENTS.md#multi-agent-delegation) owns clean-context
contracts, fresh per-Ticket roles, safe waves and failure recovery. Root,
develop, verify and test Skills retain minimum executable rules for installed
use without AGENTS.md. A dispatched worker executes its role without recursive
agent creation. Verifiers read the repository without repair edits; failures
return to implementation and a new verifier checks the affected functionality.
Ordinary per-Ticket verification uses one fresh verifier. Final Plan/branch/PR
acceptance verification uses one fresh independent verifier checking the whole
current Plan scope.
The coordinator retains integration, the Test Quality Gate and final judgment.

[Context Management](../../AGENTS.md#context-management) owns the thin
coordinator, scoped worker context, concise handoffs and durable Issue
checkpoints. The state snapshot remains repository recovery truth; it does not
replace those checkpoints.

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

The verification level controls breadth, not PASS. Stop only after every
acceptance criterion has executed evidence and every mandatory risk dimension
has passed or has a concrete N/A reason. Escalate breadth when acceptance
criteria, failure evidence, affected boundaries, release requirements, or the
risk profile justify it.


### Host-specific project configuration

Each host exposes its own agent runtime. Codex reads `.codex/config.toml`, may
use built-in agents, and may also read project-defined agents from
`.codex/agents/` when present. The canonical
[Codex model routing policy](../deployment/installation.md#codex-model-routing)
owns coordinator and worker defaults, scoped escalation and final acceptance
selection. Claude Code may use its built-in agents and
project-defined agents from `.claude/agents/`. Neither host reads the other's
project-agent directory. Agent choice and escalation are dynamic and driven by
the task contract plus the available agent descriptions; the repository does
not hard-code task classes to agent names. The scheduling policy lives in
[`AGENTS.md`](../../AGENTS.md#multi-agent-delegation), and
[installation.md](../deployment/installation.md) owns the per-host
configuration procedure.

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
- A persisted plan has one Plan Issue with at least one Ticket; a single-behavior requirement is one Ticket with one implicit Slice, and a persisted Plan uses one branch and PR.
- Tests provide evidence inside a Slice; local verification is a valid stop.
  If delivery is elected, single-verifier Plan/branch/PR acceptance precedes the
  final publication/merge boundary.
- `Repo_Current_State.md` is the recovery point, not a session transcript or full backlog.
- `repo-documentation` owns documentation governance; `repo-current-state` owns
  only the recovery snapshot.
- Redaction is conditional and scoped to the staged commit set; it is not a mandatory transformation of every artifact.
- State / Docs that belong to delivered work are updated before commit/PR creation and travel with that PR; integration validates the merged result.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Specialist skills are vendored under `skills/` and updated through this repository's normal version-control process.
