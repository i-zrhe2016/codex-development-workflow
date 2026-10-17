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

Persist every new requirement as one versioned `docs/plans/<plan-id>.md` before
other implementation edits, with one Ticket
section in that file for an ordinary requirement. A complex requirement may have
multiple Tickets only for distinct behavioral, dependency, or acceptance
boundaries. A Plan owns one branch and, when delivery is elected, one PR and one
merge for that requirement. Independent requirements always get separate Plans,
even while another Plan is unmerged. Supplementary work for the same requirement
updates its Ticket or adds a behavior Ticket when a distinct boundary justifies
it. Preserve IDs, branch/base, existing PR and evidence; after merge, new
requirements use new Plans. `plan-to-ticket` owns scope updates, combined historical-Issue/visible-branch
ID allocation, conflict rechecks and legacy continuation. A branch may precede
the Plan file; read back the complete contract before other edits. Existing
Issue requirements, including extensions, retain original authority without
migration or dual writes. Verified merged PR facts determine effective Markdown
Plan/Ticket completion without a post-merge status-only commit.

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
Ticket dependencies, verification, publication, integration and
completion gates remain fixed. This section owns the scheduling policy;
explanatory documents link here rather than copying it.

### Roles and Ticket ownership

The main agent owns requirements, architecture, planning and decomposition,
cross-Ticket dependencies and scheduling, integration, stage gates and final
judgment. It directly dispatches one fresh implementation owner per Ticket.
Each owner retains context across that Ticket and local repair work, and never
spawns agents. The main agent may dispatch optional
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

### Adaptive execution

The portable `develop-workflow` Skill owns the dynamic Ticket Ready Queue,
critical-path priority, integration/unlock conditions, completion-triggered
requeue, snapshot identity, conflict serialization, recovery and host-capacity
accounting. Follow its [Ticket owner and Ready Queue rules](skills/develop-workflow/SKILL.md#ticket-owners-and-workers).
The root workflow Skill preserves only cross-stage unlock invariants. The main
agent must not duplicate worker implementation or verification.

### Who chooses the subagent

The main agent selects each Ticket owner, optional module assistant, verifier or
repair implementer. This project's explicit model-routing policy overrides the
bundle defaults: every Codex worker uses `gpt-6.1-sol`; development workers use
`low` reasoning effort and verification workers use `high`. It uses the canonical model-routing procedure in
[`SKILL.md`](SKILL.md#codex-worker-model-routing), including its active-copy
resolution, explicit dispatch arguments and observed-versus-requested evidence
rules. Codex may read `.codex/agents/`; Claude Code may read `.claude/agents/`.
Named agent descriptions state their trigger and operating boundary.

For every Codex dispatch explicitly request `gpt-6.1-sol` and the role's reasoning
effort with `fork_turns="none"`. Development, docs, synchronization, API/schema,
security, complex logic and repair implementation all use Sol/low. The initial implementation
failure does not count as a repair round. Preserve failure evidence and the
count across replacements. After two consecutive failed repair rounds on the
same problem, the main agent diagnoses and replans using the preserved evidence.
Ticket and final acceptance also use Sol/high, with the exact one-Ticket coalescing
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

Manually provide this minimum Agent Handoff Contract in the following order,
putting business intent and user-visible outcomes before technical task details.
Keep each entry concise and relevant to the task:

* **Intent**: why the user needs the work and what they want to improve.
* **Outcome**: the change the user can observe when the work succeeds.
* **Scope**: role (Ticket owner, module assistant, repair implementation or
  verification), current Ticket goal, allowed modules/files, read/write
  ownership and non-goals.
* **Constraints**: interfaces, data structures and behaviors that must remain
  unchanged; state "No additional constraints" when none apply.
* **Acceptance**: concrete, verifiable conditions that demonstrate the Outcome
  has been achieved.
* **Context**: the minimum relevant file paths and entrypoints for further
  reading, with brief summaries of Ticket dependencies, Plan branch/base and
  verified prerequisite results/checkpoints.
* **Validation**: required commands and their expected results.

Workers read only rules and material needed for the current task, expanding
scope when evidence requires it. Do not preload the repository or attach the
parent conversation, unrelated history or other Tickets' context.

### Handoff and durable checkpoints

Return only the result, files changed, decisions, executed validation evidence
including failures, unresolved risks and affected dependencies. Exclude raw logs,
search output and conversation history. The main agent checks that evidence
before scheduling dependent work or crossing a stage gate.

For persisted work, the main agent records the accepted summary, current status,
acceptance and dependency changes in the Ticket section of the Plan Markdown record body,
with append-only Ticket-ID-tagged evidence entries that preserve failures. The Plan indexes
stable Ticket section anchors within the same file; each section retains its
contract and evidence summary. Detailed persistence and legacy compatibility
rules, including unchanged legacy child-Issue continuation and checkpoint
destinations, belong to `plan-to-ticket`. Every requirement is persisted
before implementation edits.

Before retiring context for persisted or resumable work, persist its checkpoint.
If a Plan write fails, report **BLOCKED** and preserve completed changes and
evidence until persistence succeeds; do not discard them or replace Plan state
with memory files. `docs/Repo_Current_State.md` holds repository recovery truth,
not Ticket history. Do not create `handoff.md`, `memory.md` or `context.md`.

### Retirement and recovery

Prefer fresh execution context at natural task, role, stage and Ticket
boundaries; retire the finished worker context without deleting host logs.
Keep the Ticket owner's continuity across implementation and local repairs;
do not create per-step acknowledgements or acceptance gates. A same-
problem repair uses a fresh implementation worker and preserves the failure
count. All repair implementation workers use Sol/low from the first round; after two failed
repair rounds, the main agent diagnoses and replans. Ticket
acceptance repairs use a fresh replacement, followed by a new independent
verifier. Never reuse workers across roles, stages or Tickets; independent
verification remains mandatory. Worker task completion does not
mark the Ticket done or verify effective Plan completion before verified merge.

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
| Requirement needs Plan/Ticket decomposition and persistence | `plan-to-ticket` |
| Feature, bug fix, regression, integration, or browser validation       | `test-workflow`              |
| Skill effectiveness evaluation by blind A/B real task outcomes         | `skill-eval`                 |
| Architecture or flow visualization materially improves understanding   | `plantuml`                   |
| Verified repository state materially changed                           | `repo-current-state`         |
| Every change (documentation impact check), or docs need normalizing    | `repo-documentation`         |
| Files staged for a commit or PR may contain credentials or personal data | `data-document-redaction`    |
| Branch publication, Commit, Push, or PR readiness is required          | `github-push-when-ready`     |

## Skill Rules

* Workflow Skills are explicit-only: invoke one only when the user writes its
  `$skill-name` form.
* Prefer the most specific explicitly requested Skill.
* Follow the invoked Skill's `SKILL.md`.
* Do not duplicate Skill procedures here or infer invocation from a generic
  task trigger.
* Multiple Skills may be invoked only when the user explicitly names each one.
* If a required Skill is unavailable, report it instead of inventing a replacement.

## Repository Rules

* Keep architecture and dependencies as simple as practical.
* One commit should represent a clear declared scope: one requirement's Plan.
  Follow `github-push-when-ready` for Plan messages and publication gates.
* Never commit passwords, tokens, credentials, private keys, `.env`, or other secrets.
* Do not commit local `AGENTS.md` or `CLAUDE.md` unless the repository intentionally versions them.

## Completion

The requested work is complete when its authorized stage gates have passed.
Local verification, commit, push and PR readiness are distinct stopping points;
final Plan delivery is complete only after verified merge and reconciliation.
