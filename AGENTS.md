# AGENTS.md

This file defines repository-wide engineering principles, the development workflow stages, and when specialist Skills must be invoked.

Detailed procedures belong in each Skill's `SKILL.md`. Do not duplicate them here.

## Principles

Priority:

`Correctness -> Simplicity -> Architecture Clarity -> Maintainability -> Extensibility`

* Follow Occam's razor: prefer the simplest necessary and maintainable solution.
* Understand the existing architecture before making non-trivial changes.
* Prefer minimal changes, existing capabilities, mature frameworks, and clear interfaces.
* Do not introduce speculative abstractions, services, features, or dependencies.
* Keep responsibilities and module/service boundaries clear.
* Fix root causes instead of hiding problems with additional complexity.

## Documentation

* Keep `README.md` as the project introduction and documentation index.
* Put detailed documentation under `docs/`.
* Keep documents focused on one module or topic.
* Update documentation only when verified behavior, architecture, interfaces, dependencies, deployment, or important project state changes.

## Development Workflow

Use the lightest workflow that preserves correctness. Work is routed to the
stage that owns it rather than running one fixed chain for every request.

| Situation | Stage |
| --- | --- |
| A requirement needs understanding, design, or decomposition | `plan-workflow` |
| Repository content must change | `develop-workflow` |
| Acceptance, a regression, or a branch needs proof | `verify-workflow` |
| A verified change must be committed, pushed, or turned into a PR | `publish-workflow` |
| A ready PR must be merged, cleaned up, or reconciled | `integrate-workflow` |
| The user explicitly authorizes a complete end-to-end delivery | the full orchestration in `codex-development-workflow` |

Feature, bug fix, refactor, and documentation work are profiles of these stages,
not separate workflows.

Persist a Plan Issue with one or more child Ticket Issues before branch work
when the work is complex, must survive a session boundary, or the user asks for
a persisted plan. A persisted Plan owns one branch and, when the user elects delivery, one PR and
one merge for all of its Tickets; split each Ticket into independently
verifiable Slices. New user-requested functionality joins the same unmerged
Plan as a new Ticket after its goal, scope, index, dependencies and validation
are updated. Preserve IDs, branch/base, existing PR and evidence; after merge,
start a new Plan. `plan-to-ticket` owns the scope-update procedure.

Local verified functionality is a normal stopping point, not BLOCKED while
publication awaits the user. The user controls commit, push, PR creation/update
and merge timing and scope. Prior authorization persists for its stated batch;
adding scope alone grants no publication authority. Commit-only and push-only
requests stop at those boundaries. With an open PR, expanded scope returns the
Plan to `in_progress`, retains its PR URL and requires impacted acceptance,
batch readiness and final Plan/branch/PR acceptance to be revalidated before
authorized publication/update.

`codex-development-workflow` routes to these stages and carries the invariants
that hold in all of them. Its full orchestration is the only path that runs
several stages as one authorized delivery.

## Multi-Agent Delegation

Use a **fixed workflow / adaptive execution** model. Stage ownership, Plan ->
Ticket -> Slice dependencies, verification, publication, integration and
completion gates remain fixed. This section owns the scheduling policy;
explanatory documents link here rather than copying it.

### Roles and Ticket ownership

The main agent owns requirements, architecture, planning and decomposition,
cross-Ticket dependencies and scheduling, integration, stage gates and final
judgment. It directly dispatches one fresh implementation owner per Ticket.
Each owner retains context across that Ticket's dependency-ordered Slices and
local repair work, and never spawns agents. The main agent may dispatch optional
independent-module assistants only for fixed interfaces and non-overlapping
ownership; parallel writers use isolated workspaces and return patches for main
integration. It directly dispatches fresh independent verifiers and fresh
repair replacements. Workers are never reused across Tickets or roles.
Interrupted workers are replaced from verified checkpoints.

Ticket acceptance uses a fresh independent verifier. Final Plan/branch/PR
acceptance uses a separate fresh verifier for the whole current Plan scope,
except that one NEW verifier may satisfy both gates for a one-Ticket Plan only
when Ticket and final scopes have exactly the same full scope, artifact/version,
configuration and deployment surface. It must PASS; any FAIL or BLOCKED blocks
readiness and preserves evidence. Never reuse a verifier after code, test,
configuration or documentation changes.

The verifier reads the repository without changing code, tests, configuration
or documentation; caches and temporary evidence are allowed. Verification
failures return to the implementation role for fixes, then a **new** verifier
rechecks the affected functionality. Preserve prior failure evidence: changing
agents or a passing retry cannot turn unexplained flakiness into PASS. The main
agent retains the Test Quality Gate and stage-transition decision.

Worker context, task contracts, handoffs and retirement follow
[Context Management](#context-management).

### Adaptive execution waves

Schedule dependency-ready Tickets and bounded owner/module/verifier tasks at
runtime. Count all active main agents and workers against actual host capacity;
the repository imposes no fixed concurrency cap or total/lifetime agent quota.
A direct main-to-worker dispatch requires two available slots; queue when host
capacity is exhausted. No additional leaf-slot reservation applies. Integrate
completed waves and recompute readiness after material results, failures,
dependency changes or integration steps. A dependent Ticket may prepare
read-only, but delivery writes wait for its prerequisite's independent PASS.

Before a wave, check dependencies, ownership, risk, host capacity and overlap
in files, interfaces, schemas, migrations, configuration and shared test state.
Keep dependent or conflicting work sequential. Context isolation does not
isolate the filesystem. Parallel writers require separate safe ownership and
isolated worktrees or returned patches for main-agent integration on the shared
Plan branch. Never switch a directory used by active workers or create Ticket
delivery branches. If safe isolation is unavailable, serialize work. The main
agent must not duplicate worker implementation or verification.

### Who chooses the subagent

The main agent selects each Ticket owner, optional module assistant, verifier or
repair implementer. It uses the canonical model table in
[`SKILL.md`](SKILL.md#codex-worker-model-routing), including its active-copy
resolution, explicit dispatch arguments and observed-versus-requested evidence
rules. Codex may read `.codex/agents/`; Claude Code may read `.claude/agents/`.
Named agent descriptions state their trigger and operating boundary.

For every Codex dispatch explicitly request the policy-selected model and
reasoning effort with `fork_turns="none"`. Ordinary development, docs and sync
use Luna/medium; API/schema, security and complex logic use Luna/high. The
initial implementation failure does not count as a repair round. After two
consecutive failed repair rounds on the same problem, stop Luna writes to that
problem and dispatch a fresh Sol/high repair implementer. Preserve failure
evidence and the count across replacements; later unrelated work remains Luna.
Ticket and final acceptance use Sol/high, with the exact one-Ticket coalescing
exception above. If a required setting is actually unsupported or a selected
role has an unavoidable conflicting override, stop
that dispatch as **BLOCKED**. Do not silently fall back, switch providers or
substitute a coordinator for implementation or verification. `skill-eval` keeps
its candidate model fixed across baseline and treatment; it does not inherit
the default routing table.

The installer does not install this file. The root, develop, verify and test
Skills therefore carry the minimum executable worker/context rules so this
policy still operates in target repositories without `AGENTS.md`.

## Context Management

Execution context is disposable; accepted state and evidence are durable.
This section owns context lifecycle policy; delegation and stage gates remain
governed above and by their Skills.

### Thin coordinator and lazy workers

Keep the main agent long-lived and thin: retain requirements, decisions, the
Plan and current Ticket, dependencies, acceptance criteria, completion summaries
and unresolved risks. Perform only scoped inspections needed for coordination;
delegate noisy exploration and log analysis. Do not restart the main agent for
every Ticket.

Every worker starts with independent context. For Codex, every `spawn_agent`
call must set `fork_turns="none"`; never inherit the parent conversation. Other
hosts must use an equivalent fresh-agent, independent-context capability. If
fresh workers and clean context cannot be guaranteed, report **BLOCKED**;
there is no main-agent implementation/verification fallback.

Manually provide only this minimum task contract:

* role (Ticket owner, module assistant, repair implementation or verification), current
  Ticket/Slice goal, scope and non-goals;
* Slice dependencies and acceptance criteria for the assigned Ticket or Slice;
* relevant files and read/write ownership;
* Plan branch/base and verified prerequisite results/checkpoints;
* validation commands and expected result summary.

Workers read only rules and material needed for the current task, expanding
scope when evidence requires it. Do not preload the repository or attach the
parent conversation, unrelated history or other Tickets' context.

### Handoff and durable checkpoints

Return only the result, files changed, decisions, executed validation evidence
including failures, unresolved risks and affected dependencies. Exclude raw logs,
search output and conversation history. The main agent checks that evidence
before scheduling dependent work or crossing a stage gate.

For persisted work, the main agent records the accepted summary, current status,
acceptance and dependency changes in existing Ticket Issue bodies, with
append-only evidence comments that preserve failures. The Plan remains the
batch index and dependency order; do not copy Ticket evidence into it. Keep
existing small inline-work persistence exceptions, but work that must survive
a context or session boundary requires durable persistence.

Before retiring context for persisted or resumable work, persist its checkpoint.
If an Issue write fails, report **BLOCKED** and preserve completed changes and
evidence until persistence succeeds; do not discard them or replace Issue state
with memory files. `docs/Repo_Current_State.md` holds repository recovery truth,
not Ticket history. Do not create `handoff.md`, `memory.md` or `context.md`.

### Retirement and recovery

Prefer fresh execution context at natural task, role, stage and Ticket
boundaries; retire the finished worker context without deleting host logs.
Keep the Ticket owner's continuity across that Ticket's dependent Slices and
local repairs; do not require per-Slice main-agent acknowledgement. A same-
problem repair uses a fresh implementation worker and preserves the failure
count. After two failed repair rounds, use Sol/high for that problem. Ticket
acceptance repairs use a fresh replacement, followed by a new independent
verifier. Never reuse workers across roles, stages or Tickets; independent
verification remains mandatory. Worker task completion does not
make the Ticket done or closed before verified merge.

A compacted or fresh main agent reconstructs from repository rules, the Plan,
current Ticket and relevant predecessor summaries, checked against the actual
branch/worktree. Do not rely on remembered chat. Compaction permits continuation;
it is neither durable persistence nor a substitute for a fresh worker at a
natural boundary.

## Skill Routing

| Situation                                                              | Skill                        |
| ---------------------------------------------------------------------- | ---------------------------- |
| Routing a request to its stage, or an authorized end-to-end delivery   | `codex-development-workflow` |
| Planning, designing, or decomposing before changes                     | `plan-workflow`              |
| Implementing or modifying repository content                           | `develop-workflow`           |
| Verifying acceptance, a regression, or a branch                        | `verify-workflow`            |
| Committing, pushing, or preparing a pull request                       | `publish-workflow`           |
| Merging, cleaning up, or reconciling after delivery                    | `integrate-workflow`         |
| Complex, multi-step, dependent, or incremental work needs a Plan/Ticket/Slice breakdown | `plan-to-ticket` |
| Feature, bug fix, regression, integration, or browser validation       | `test-workflow`              |
| Skill effectiveness evaluation by blind A/B real task outcomes         | `skill-eval`                 |
| Architecture or flow visualization materially improves understanding   | `plantuml`                   |
| Verified repository state materially changed                           | `repo-current-state`         |
| Every change (documentation impact check), or docs need normalizing    | `repo-documentation`         |
| Files staged for a commit or PR may contain credentials or personal data | `data-document-redaction`    |
| Branch publication, Commit, Push, or PR readiness is required          | `github-push-when-ready`     |

## Skill Rules

* Invoke Skills only when their trigger applies.
* Prefer the most specific applicable Skill.
* Follow the invoked Skill's `SKILL.md`.
* Do not duplicate Skill procedures here.
* Multiple Skills may be invoked when independent triggers apply.
* If a required Skill is unavailable, report it instead of inventing a replacement.

## Repository Rules

* Keep architecture and dependencies as simple as practical.
* One commit should represent a clear declared scope: one functionality or a
  planned delivery batch. Follow `github-push-when-ready` for batch messages and
  publication gates.
* Never commit passwords, tokens, credentials, private keys, `.env`, or other secrets.
* Do not commit local `AGENTS.md` or `CLAUDE.md` unless the repository intentionally versions them.

## Completion

The requested work is complete when its authorized stage gates have passed.
Local verification, commit, push and PR readiness are distinct stopping points;
final Plan delivery is complete only after verified merge and reconciliation.
