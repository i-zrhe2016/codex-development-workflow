---
name: plan-to-ticket
description: "Define one requirement-level Plan and its Ticket execution contracts, then persist one GitHub Issue with Ticket sections before branch edits. Use multiple Tickets only for genuine behavior, dependency, or acceptance boundaries."
---

# Plan to Ticket

Own requirement decomposition and Issue persistence, not product/repository
implementation. Every independent user requirement receives one [PLAN] Issue containing its
Plan and Ticket sections before branch edits. An ordinary requirement has one Ticket; a complex requirement may
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
  prepare read-only; delivery edits become ready only after each prerequisite's
  work is integrated on the shared Plan branch, a fresh independent verifier
  passes that fixed integrated snapshot, and PASS evidence is saved to its
  section and Ticket-ID-tagged comments on the Plan Issue. Failed Issue writes never unlock dependents. The coordinator requeues
  eligible work on each completion or material progress event; there is no
  batch barrier. All Tickets share the Plan branch; no Ticket branches or merges.
- Before persisting a multi-Ticket Plan, validate that every dependency points
  to an indexed Ticket in this Plan and that the graph is acyclic. Record each
  Ticket's owned paths/modules, shared resources or conflicts, and a rough
  relative effort estimate when useful for scheduling. Dependency edges express
  acceptance prerequisites; overlapping ownership/resources are serialized
  separately and do not by themselves justify an extra Ticket dependency.
- New independent requirements always start new Plans, even if another Plan is
  unmerged or the work shares files or a session; each Plan owns its own branch. Supplementary work for the
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
Planning does not dispatch workers. Declare actual file, interface, schema,
migration, configuration, fixture and shared-runtime conflicts so the
coordinator can serialize them. The `develop-workflow` skill owns Ready Queue
priority, integration and recovery details.

## Updating scope

Classify follow-up scope by the desired outcome, the existing Plan scope and
its acceptance boundaries. Shared files, a session or an available branch do
not establish that work belongs to the same requirement.

For supplementary work within an unmerged requirement:

1. Confirm the Plan remains unmerged; preserve its stable ID, Issue, branch/base,
   existing PR and accepted evidence.
2. Update the existing Ticket scope. Add a behavior Ticket only if the new work
   has a distinct behavioral, dependency, or acceptance boundary.
3. Update the Plan goal/scope, Ticket index, dependencies and validation; update
   every affected Ticket section in the same Issue and preserve prior passing and failing evidence.
4. Verify all Issue changes before editing. Set the Plan `in_progress`; if a PR
   exists, retain its URL and require impacted acceptance and final Plan
   verification before an authorized update.
5. Keep publication authority separate. Scope authorization permits the
   requested implementation, not commit, push, PR update or merge.

An independent requirement always receives a new Plan and its own branch, including before the
previous Plan merges, regardless of shared files or session. A completed merged
Plan is never reopened. After merge, the next requirement also starts a new Plan.

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

Persist one [PLAN] Issue containing the Plan and one or more Ticket sections for every user
requirement before creating a branch or editing repository files. GitHub Issues
are authoritative. Chat may link to them but is not a substitute. Do not create
local Markdown or `docs/plans/` / `docs/tickets/` mirrors.

A Plan owns one requirement, one Issue, one branch, and when delivery is
authorized, one PR and one merge. Each Ticket owns a section within that same
Issue with its complete execution/acceptance contract, tests and docs. Every
Ticket shares the Plan branch/base; Plan and branch are one-to-one. The Plan
records its overall goal, scope, dependency order, integration/regression
validation and one-merge completion rule. Its Ticket index links to stable
headings `### T0001` (anchor `#t0001`) in the same Issue; put behavior titles in
the section body so renaming a title never changes the anchor. Each section
owns its goal, scope, exclusions, dependencies, status, acceptance, context,
write ownership, shared resources/conflicts, optional relative effort,
Function Checklist, test strategy/level/cases, validation command and evidence
summary. Do not duplicate mutable contracts elsewhere in the Issue.

Use the available GitHub Issues connector and current repository remote's
`owner/name`. Missing target, connector, authentication or write permission
blocks persistence; do not use an unapproved ad-hoc API client. The complete Plan Issue and all required Ticket
sections must exist before branch creation. Any same-requirement scope update and
required Issue edits must persist before further implementation edits.

### Naming and idempotency

- Plan ID: repository-unique stable lowercase kebab-case slug in its
  `codex-plan-id` marker. Scan all open/closed historical Plan markers before
  allocating; preserve and never reuse existing IDs. Title: `[PLAN] <short plan title>`.
- Ticket ID: `T` plus exactly four zero-padded decimal digits. Enumerate every
  page of open and closed historical Issue bodies, extracting **all** exact
  `codex-ticket-id` markers from each body, including multiple markers in one
  Issue. Allocate above every valid ID; never reuse IDs. At `T9999`, stop and
  report ID exhaustion rather than inventing another format. An incomplete
  scan blocks allocation. Historical duplicates stay unchanged; resolve their
  exact marker and Plan association before updating.
- Before creation, search exact Plan and Ticket markers across both new-format
  sections and historical records. Reuse the unique matching Plan and Ticket
  section; never create a duplicate on retry. Preserve stable IDs and existing
  branch/base/PR history. Resolve ambiguous matches rather than guessing.
- New Issues use only `[PLAN] <short plan title>`; Tickets have no separate
  Issue titles. Keep the Plan marker once and each Ticket marker once beside
  its stable heading. Historical child markers may remain in linked superseded
  records; use their verified migration link to resolve the authoritative section.

```text
<!-- codex-plan-id: <stable-plan-slug> -->
<!-- codex-ticket-id: T0016 -->
```

### Authoritative Issue bodies

The Plan begins with actual delivery metadata at the top, before its marker and Plan sections:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: main
PR: null
Tickets: [T0001]
```

Each Ticket section begins with its stable heading and marker, followed by:

```yaml
Status: planned
Dependencies: []
```

Allowed statuses are `planned`, `in_progress`, `blocked`, `in_review`, and
`done`. Keep the Plan Issue open until verified merge; Ticket sections retain separate
statuses. Append-only evidence comments must be tagged with the exact Ticket ID
(e.g. `[T0001] PASS ...`) and record snapshot, commands/results and failures.
Plan-wide comments are explicitly tagged `[PLAN]`; they do not replace each
Ticket's acceptance evidence or structured body fields. Sections link to the
relevant comments and preserve passing and failing evidence summaries. Tickets
do not carry independent branch/base/PR metadata.

### Persistence sequence and failures

1. Resolve repository, default base, requirement scope and Ticket boundaries.
2. Complete the historical marker scan, check IDs and resolve matching records.
3. The main agent serializes all writes to the shared Plan Issue. Read its
   latest body before each scoped section update; preserve other Tickets,
   metadata and evidence, then read back the saved content. Workers return
   checkpoint evidence to the main agent rather than racing whole-body writes.
   Create/update the single Plan Issue with top-level metadata, Plan, anchored
   Ticket index and every complete Ticket section. Preserve unrelated sections
   and evidence when changing its body.
4. Read back the saved body and verify markers, metadata, stable anchors,
   complete contracts, dependencies, evidence references and index consistency.
   Start the Plan branch only after the complete write and read-back succeed.
5. Retry by reading the authoritative Issue first and updating missing content;
   never append duplicate sections, markers or indexes.

If a required read/write fails, report the failed operation and created Issue
URLs; mark affected Issues `blocked` when possible. Do not claim persistence or
implementation readiness and never compensate with a local mirror.

### Legacy continuation without scope extension

A preexisting unmerged Plan resumed **without scope extension** may continue
using its original child-Issue authority. Development/verification checkpoints,
status updates and append-only evidence remain on the original child Issues,
not missing new-format sections. Do not require migration merely to
resume, verify, publish or integrate unchanged legacy scope. Validate the
original Plan and every required child's complete metadata/contracts and
acceptance evidence against the current publication scope; retain IDs,
branch/base, PR history and child evidence. After verified merge, mark the
legacy Plan and child Tickets `done` and close their Issues. All verification,
publication authorization and merge gates remain unchanged.

This exception applies only to existing legacy records without added scope;
new Plans always use single-Issue sections. User-requested extension of an
unmerged legacy requirement triggers the migration below before further
implementation. A completed merged Plan is never reopened.

### Historical child-Issue migration on extension

New Plans always use the single-Issue format. Leave historical Plan/child
Issues unchanged until their unmerged requirement needs extension. Do not
reopen completed merged Plans; later requirements get a new Plan and branch.

1. Read the original Plan and every indexed child body and evidence comments;
   resolve IDs and association without renumbering or replacing the Plan Issue.
2. Copy each complete execution/acceptance contract, status, dependencies and
   a summary of all passing/failing evidence into its Ticket section on the
   original Plan. Retain links to the child and original evidence comments;
   preserve Plan ID, Ticket IDs, branch/base and PR history. Include the new
   scope, updated acceptance and affected-evidence revalidation requirements.
3. Read back and verify the complete Plan, anchored index, copied contracts,
   evidence summaries/links and unchanged delivery metadata before touching
   any child status or closure. The canonical sections must be complete first.
4. Only after successful verification, mark each child superseded with a link
   to its canonical `#tdddd` section and close it with GitHub `state_reason: not_planned` and the superseded note/link,
   not as completed (`superseded` is not a GitHub state reason).
   Do not delete its body or evidence. Plan/Ticket completion still requires
   verified merge. Record migrated child links on the Plan.
5. On partial read/write/verification/closure failure, preserve every record
   and all evidence, report the failed operation, and block readiness. Resume
   from read-back state; verified migrated sections and superseded children
   are reused, not copied again. Finish required reconciliation before readiness.

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
| PR verified merged | All Ticket sections and Plan `done`; close the one Plan Issue; retain merged PR on Plan. |

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
Ticket section URLs, metadata, actual branch/base, milestones and Ticket index.
Before persistence, return only scope/options discussion, not an
implementation-ready contract; persistence remains required before branch edits.

Each Ticket uses these fields:

```text
### T0001
<!-- codex-ticket-id: T0001 -->
Title: <behavior/capability title>
Section: <canonical Plan Issue URL>#t0001
Status: planned
Dependencies: <explicit Ticket IDs or None>
Write Ownership: <paths/modules the owner may change>
Shared Resources / Conflicts: <interfaces, schemas, fixtures, databases, ports, services or None>
Relative Effort: <rough estimate or Unknown>
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
Evidence Summary: <accepted snapshot/results, preserved failures and comment links>
```

On successful persistence, return `# Plan` and `# Tickets` with URLs and current
metadata. On required Issue read/write failure, return a concise blocked report
naming the operation and any created URLs; do not return a chat-only plan or
readiness claim.
