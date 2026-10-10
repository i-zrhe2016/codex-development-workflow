---
name: plan-to-ticket
description: "Define one requirement-level Plan and its Ticket execution contracts, then persist GitHub Issues before branch edits. Use multiple Tickets only for genuine behavior, dependency, or acceptance boundaries."
---

# Plan to Ticket

Own requirement decomposition and Issue persistence, not product/repository
implementation. Every independent user requirement receives one Plan Issue before
branch edits. An ordinary requirement has one Ticket; a complex requirement may
have multiple Tickets only when distinct behavioral, dependency, or acceptance
boundaries make the work independently understandable and verifiable. A Ticket
is the execution and acceptance unit. Do not create per-step IDs, statuses,
Issues, or acceptance gates.

When the user controls the overall flow, present scope, dependency order, risks
and validation options, but do not choose unapproved scope or delivery actions.
Persist the user's stated requirement and the minimum contracts needed to execute
it; every requirement is persisted regardless of size or expected session length.

## Scope and sizing

Determine the requirement's desired outcome, necessary foundations, behavior
boundaries, Ticket dependencies, scope exclusions, observable acceptance,
concrete cases, and Ticket/final validation.

- Use one Ticket for an ordinary requirement. Use multiple Tickets for a complex
  requirement only when they represent distinct behaviors, real dependencies,
  or acceptance boundaries. Do not create Tickets for file/class/method/import
  steps, implementation phases, or test activities that belong with behavior.
- Keep tests with their behavior; a separate test Ticket is justified only when
  test infrastructure is itself the requirement. Avoid unrelated refactors,
  upgrades, formatting, speculative abstractions and future work.
- Record dependencies between Tickets only when real. A dependent Ticket may
  prepare read-only, but delivery edits wait for its prerequisite's independent
  PASS. All Tickets share the Plan branch; no Ticket branches or merges.
- New independent requirements always start new Plans, even if another Plan is
  unmerged or shares a branch, files, or session. Supplementary work for the
  same requirement updates its existing Ticket. Add a Ticket only if the new
  work creates a distinct behavioral, dependency, or acceptance boundary.
- If implementation reveals a materially different design or an independent
  requirement, stop expansion and persist the necessary scope/Plan changes before
  further edits. Preserve valid work and prior evidence.

The main agent directly dispatches one fresh implementation owner per Ticket,
including docs/config/test work. The owner retains context across the Ticket and
local repairs and never spawns agents. The main agent separately dispatches
fresh independent verifiers and repair replacements. Verifiers are read-only
except caches and temporary evidence. Optional module assistants require fixed
interfaces, non-overlapping ownership, isolated workspaces and returned patches.
Do not split Ticket implementation or acceptance verification across workers.
A separate final Plan verifier is required except one NEW verifier may satisfy
both Ticket and final gates for a one-Ticket Plan when full scope,
artifact/version, configuration and deployment surface match exactly. Main-agent
capacity and dispatch routing follow `AGENTS.md` and the root workflow skill.
Planning does not dispatch workers. Serialize dependent or overlapping files,
interfaces, schemas, migrations, configuration and shared test state.

## Updating scope

For supplementary work within an unmerged requirement:

1. Confirm the Plan remains unmerged; preserve its stable ID, Issue, branch/base,
   existing PR and accepted evidence.
2. Update the existing Ticket scope. Add a behavior Ticket only if the new work
   has a distinct behavioral, dependency, or acceptance boundary.
3. Update the Plan goal/scope, Ticket index, dependencies and validation; update
   every affected Ticket Issue and preserve prior passing and failing evidence.
4. Verify all Issue changes before editing. Set the Plan `in_progress`; if a PR
   exists, retain its URL and require impacted acceptance and final Plan
   verification before an authorized update.
5. Keep publication authority separate. Scope authorization permits the
   requested implementation, not commit, push, PR update or merge.

An independent requirement always receives a new Plan, including before the
previous Plan merges. After merge, the next requirement also starts a new Plan.

Local verified functionality may stop with Plan/Tickets open and checkpointed.
Keep `in_progress` before review or `in_review` for unchanged review scope.
Awaiting a publication decision is not `blocked`. Mark `done` and close only
after verified merge.

## Repository context and validation

Use `AGENTS.md`, `docs/Repo_Current_State.md`, affected code and directly
relevant architecture/design documents when available. Verify important claims
against code. Reuse project patterns, tests, fixtures and commands. Find
commands in package scripts, task runners, CI or test docs; do not invent them.
Without repository context, remain implementation-neutral and state expected
validation layers.

Each Ticket includes a behavioral Function Checklist mapping required
capabilities to acceptance and test evidence. Acceptance states observable
outcomes; cases state how to exercise them. Prefer a concise set of high-value
success, boundary/failure, state-transition, regression, integration, and
browser-visible cases when applicable. Specify the smallest reliable
Ticket/final-Plan validation. Downstream testing chooses level and breadth;
planning does not force RED/GREEN for trivial or mechanically verifiable work.

## Persistence and delivery contract

Persist one Plan Issue and its child Ticket Issue or Issues for every user
requirement before creating a branch or editing repository files. GitHub Issues
are authoritative. Chat may link to them but is not a substitute. Do not create
local Markdown or `docs/plans/` / `docs/tickets/` mirrors.

A Plan owns one requirement, one Issue, one branch, and when delivery is
authorized, one PR and one merge. Each Ticket owns one child Issue and its
complete execution/acceptance contract, tests and docs. Every Ticket shares the
Plan branch/base; Plan and branch are one-to-one. Plan Issue records the overall
goal, scope, Ticket index, Ticket dependency order, relevant integration /
regression validation, and one-merge completion rule. Do not copy mutable Ticket
acceptance or execution evidence into the Plan. Ticket Issue owns its goal,
scope, exclusions, dependencies, current status, acceptance, relevant context,
Function Checklist, test strategy/level/cases and validation command.

Use the available GitHub Issues connector and current repository remote's
`owner/name`. Missing target, connector, authentication or write permission
blocks persistence; do not use an unapproved ad-hoc API client. All required
Issues must exist before branch creation. Any same-requirement scope update and
required Issue edits must persist before further implementation edits.

### Naming and idempotency

- Plan ID: repository-unique stable lowercase kebab-case slug in its
  `codex-plan-id` marker. Title: `[PLAN] <short plan title>`.
- Ticket ID: `T` plus exactly four zero-padded decimal digits. Scan open and
  closed Issue bodies for exact `codex-ticket-id` markers and allocate above
  every valid ID; never reuse IDs. Historical duplicates remain legacy records
  and are resolved by exact marker and Plan association. Title:
  `[T0016] <short behavior/capability title>`.
- Before creation, search exact Plan and Ticket markers. Reuse/update the unique
  matching Issues and normalize titles while retaining stable IDs. Resolve
  duplicate matches; never guess or create a duplicate.

```text
<!-- codex-plan-id: <stable-plan-slug> -->
<!-- codex-ticket-id: T0016 -->
```

### Authoritative Issue bodies

The Plan begins with actual delivery metadata:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: main
PR: null
Tickets: [T0001]
```

Each Ticket begins with:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

Allowed statuses are `planned`, `in_progress`, `blocked`, `in_review`, and
`done`. Keep Plan and Tickets open until verified merge. Issue comments may hold
append-only progress evidence but do not replace structured body fields. Child
Tickets do not carry independent branch/base/PR metadata.

### Persistence sequence and failures

1. Resolve repository, default base, requirement scope and Ticket boundaries.
2. Search exact markers, check IDs, and resolve existing matching Issues.
3. Create/update the Plan with metadata, requirement scope, and Ticket index.
4. Create/update each Ticket Issue with complete execution and acceptance
   contract, Plan URL, dependencies and validation.
5. Verify the Plan index links every required child. Start the Plan branch only
   after every required Issue write succeeds.

If a required read/write fails, report the failed operation and created Issue
URLs; mark affected Issues `blocked` when possible. Do not claim persistence or
implementation readiness and never compensate with a local mirror.

### Branch, status and handoff

Record exact `Branch` and `Base` before branch work, using
`<type>/<plan-id>-<short-description>`, and verify them on resume. Do not share
a branch across Plans or create Ticket branches. Keep every Ticket, test and
document on the Plan branch. Prerequisites are validated on that branch; no
Ticket-level merge is required.

| Boundary | Update |
|---|---|
| Branch work starts | Plan `in_progress`; exact Branch/Base recorded. |
| Blocking dependency/environment | Affected Plan/Ticket `blocked`. |
| Local verification passes; publication awaits user | Keep Issues open with accepted evidence, not `blocked`. |
| Same-requirement scope added before merge | Update Plan/Ticket scope, index, dependencies and validation; Plan `in_progress`; retain PR; revalidate affected work. |
| One Plan PR opens or is updated with authorization | Head/base match Branch/Base and current requirement checks pass; Plan `in_review`, record PR URL; Tickets may enter `in_review`. |
| PR verified merged | Plan and all child Tickets `done` and closed; retain merged PR on Plan. |

Keep `PR: null` until a PR exists. Branch/PR existence alone never means done.
The Plan is ready for its one PR only after every Ticket acceptance and relevant
Plan-level integration/regression checks pass. Any failure blocks publication.
Commit-only and push-only stop at their authorized boundaries. Human-authorized
delivery follows verification, redaction, commit/push/PR, then separately
authorized merge unless full delivery explicitly includes merge. When repository
state changes, `docs/Repo_Current_State.md` holds a compact active-Issue pointer,
not a copied Plan/backlog.

## Output structure

Use `# Plan` and `# Tickets`. For persisted work, include canonical Plan and
Ticket Issue URLs, metadata, actual branch/base, milestones and Ticket index.
Before persistence, return only scope/options discussion, not an
implementation-ready contract; persistence remains required before branch edits.

Each Ticket uses these fields:

```text
### T0001 - <behavior/capability title>
Issue title: [T0001] <behavior/capability title>
Issue: <canonical child Issue URL>
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: <explicit Ticket IDs or None>
Ticket Goal: <one concrete outcome>
Ticket Scope: <allowed components/behavior>
Ticket Out of scope: <unrelated/future work>
Function Checklist: <required behaviors as checkboxes>
Requirements: <concrete requirements and important edge cases>
Non-goals: <explicit exclusions>
Ticket Acceptance Criteria: <observable results>
Relevant Context / Files: <needed files/interfaces/state>
Test Strategy: <justified focused-after, RED/GREEN, static, integration, browser>
Test Level: <minimal / focused / regression / full>
Test Cases: <concrete success/failure/boundary cases>
Validation Command: <smallest known commands, otherwise expected evidence>
```

On successful persistence, return `# Plan` and `# Tickets` with URLs and current
metadata. On required Issue read/write failure, return a concise blocked report
naming the operation and any created URLs; do not return a chat-only plan or
readiness claim.
