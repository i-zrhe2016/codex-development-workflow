---
name: plan-to-ticket
description: "Define one requirement-level Plan and its Ticket execution contracts, then persist one versioned Markdown Plan with Ticket sections before implementation edits. Use multiple Tickets only for genuine behavior, dependency, or acceptance boundaries."
---

# Plan to Ticket

## Execution mode

Default reasoning effort is `low`, including self-verification; planning
uses `high` in either mode. Delegated development/repair uses `low` and
independent verification `high`. Report unsupported effort settings; do not
claim that editing instructions changed the running turn's effort.

Default single-agent execution: the main agent performs this stage directly,
including required checks and acceptance; do not spawn subagents. Record
self-verification accurately, without claiming independent verification.
Worker-only dispatch, independent-verifier and no-main-agent-fallback rules
below apply only in explicitly authorized delegated mode. Stage transitions
and an initial failure do not activate delegation. After two consecutive failed
same-problem repair rounds, checkpoint and pause; ask the user to choose an
escalation model and whether to authorize delegation. Model selection alone
does not authorize subagents. Missing subagent support does not block default
single-agent execution. Keep the existing Test Quality Gate, durable evidence
and publication boundaries in both modes.

Own requirement decomposition and Plan persistence, not product/repository
implementation. Every new independent user requirement receives one versioned Plan Markdown
file containing its Plan and Ticket sections before other implementation edits. An ordinary requirement has one Ticket; a complex requirement may
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
  work is integrated on the shared Plan branch, the main agent in default
  single-agent mode or a fresh independent verifier in delegated mode passes
  that fixed integrated snapshot, and PASS evidence is saved to its
  section and Ticket-ID-tagged append-only evidence in the Plan record. Failed Plan writes never unlock dependents. The coordinator requeues
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

In explicitly authorized delegated mode, the main agent directly dispatches
one fresh implementation owner per Ticket,
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

1. Confirm the Plan remains unmerged; preserve its stable ID, authoritative record, branch/base,
   existing PR and accepted evidence.
2. Update the existing Ticket scope. Add a behavior Ticket only if the new work
   has a distinct behavioral, dependency, or acceptance boundary.
3. Update the Plan goal/scope, Ticket index, dependencies and validation; update
   every affected Ticket section in the same authoritative record and preserve prior passing and failing evidence.
4. Read back all saved contract changes before editing. Set the Plan `in_progress`; if a PR
   exists, retain its URL and require impacted acceptance and final Plan
   verification before an authorized update.
5. Keep publication authority separate. Scope authorization permits the
   requested implementation, not commit, push, PR update or merge.

An independent requirement always receives a new Plan and its own branch, including before the
previous Plan merges, regardless of shared files or session. A completed merged
Plan is never reopened. After merge, the next requirement also starts a new Plan.

Local verified functionality may stop with Plan/Tickets open and checkpointed.
Keep `in_progress` before review or `in_review` for unchanged review scope.
Awaiting a publication decision is not `blocked`. Effective `done` requires verified merge; see the completion rule below.

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

For every new requirement, persist one versioned `docs/plans/<plan-id>.md`
containing the Plan and one or more complete Ticket sections before any other
implementation edits. This Markdown file is authoritative, not a mirror. Chat
is not persistence. No new Plan/Ticket Issues, separate Ticket files, parallel
ledger, or dual writes are created. Existing Issue requirements retain their
original authority under legacy continuation below.

A Plan owns one requirement, one file, one branch and, when delivery is
authorized, one PR and one merge. A branch may be created first to write the
Plan file on that branch. Record exact Branch/Base, save the complete Plan and
read back every contract before other implementation edits. Scope updates must
likewise be saved and read back before their implementation.

The Plan owns goal, scope, dependency order, integration/regression validation
and completion rule. Its index links to stable headings `### T0001` (anchor
`#t0001`) in the same file; put behavior titles in the section body so renaming
a title never changes the anchor. Each Ticket owns its complete execution and
acceptance contract, status, dependencies, ownership/conflicts, Function
Checklist, test strategy/level/cases, validation command and evidence summary.
Do not duplicate mutable contracts in other records.

### Naming and idempotency

- Plan ID: repository-unique stable lowercase kebab-case slug in its
  `codex-plan-id` marker and filename. Scan historical Plan markers and visible
  Markdown records before allocation; preserve and never reuse existing IDs.
- Ticket ID: `T` plus exactly four zero-padded decimal digits. Enumerate every
  page of open and closed historical Issue bodies using the available GitHub
  connector for the verified repository remote. Extract **all** exact
  `codex-ticket-id` markers, including multiple markers in one Issue, historical
  child Issues and single-Issue sections. Also scan `docs/plans/*.md` in the
  working tree and all visible local and remote branches, including unmerged
  branches; refresh remote refs and enumerate their trees, not just default.
  Deduplicate copies of the same Plan/Ticket across refs, not distinct owners.
  Allocate exactly the combined maximum + 1 across all valid IDs in the scan;
  treat an empty scan or maximum zero as zero, yielding `T0001`. For multiple
  new Tickets, allocate consecutively, updating the maximum after each ID;
  never reuse IDs.
  Missing connector/authentication, failed fetch/read, inaccessible records,
  pagination failure or an incomplete scan blocks allocation. A transport or
  parse error is never an empty final page; verify successful pagination end. At `T9999`, stop
  and report ID exhaustion; never invent another format.
- The main agent serializes allocation and Plan writes for this repository.
  Read latest records before allocation/write and read back afterwards. Local
  serialization cannot reserve an ID against an unseen concurrent branch;
  recheck conflicts before publication as specified below.
- Search exact Plan and Ticket markers before creation and retry. Reuse the
  unique matching Plan file and section; never append duplicate markers,
  sections or indexes. Preserve IDs and branch/base/PR history. Resolve
  ambiguous matches rather than guessing. Historical duplicates stay unchanged;
  resolve their exact marker and Plan association before updating.

```text
<!-- codex-plan-id: <stable-plan-slug> -->
<!-- codex-ticket-id: T0016 -->
```

### Authoritative Markdown record

The Plan begins with actual delivery metadata before its marker and sections:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: main
PR: null
Tickets: [T0001]
```

Each Ticket begins with its stable heading and marker, followed by:

```yaml
Status: planned
Dependencies: []
```

Allowed statuses are `planned`, `in_progress`, `blocked`, `in_review`, and
`done`. Ticket sections have no independent branch/base/PR. Keep mutable status
and concise summaries in their sections. Append-only evidence in `## Evidence`
is Ticket-ID-tagged (for example `[T0001] PASS ...`) or explicitly `[PLAN]` for
Plan-wide evidence. Record snapshot identity, commands/results, failures and
accepted conclusions. Preserve prior passing and failing entries when summaries
or scope change; a retry never erases failure. Plan evidence cannot replace
Ticket acceptance. No GitHub comment write is required for Markdown work.

### Persistence sequence and failures

1. Resolve repository, default base, requirement identity and Ticket boundaries.
   Detect an existing authoritative record before choosing the storage format.
2. Complete the combined historical Issue and visible-branch Markdown marker
   scan, serialize allocation, check IDs and resolve matching records.
3. Create or resume the Plan branch if needed; the Plan file is the only allowed
   initial edit. The main agent serializes all writes, reads the latest file
   before scoped updates and preserves other Tickets, metadata and evidence.
   Workers return checkpoint evidence rather than racing whole-file writes.
4. Save the complete Plan, anchored index and every required Ticket contract.
   Read back markers, metadata, stable anchors, dependencies, complete contracts,
   evidence and index consistency before any other implementation edits.
5. On retry read the authoritative file first and update only missing content.
   Failed required read/write or read-back blocks readiness and dependent unlock;
   preserve completed work and evidence and report the exact operation/path.
   Do not compensate with chat, another file or a new Issue. Persist checkpoints
   at integration, Development Complete, acceptance failure and context retirement.

### Publication conflict recheck

Before any commit, push or PR creation/update, refresh visible remote refs and
repeat the combined marker scan. Compare distinct Plan owners, not repeated
copies of the same record. A conflicting ID blocks publication. Renumber only
new Tickets in the current unmerged Plan, allocating exactly the new combined
maximum + 1 and then consecutively updating the maximum after each ID; apply
the same empty/zero and `T9999` exhaustion rules above. Never renumber historical
Issues, merged records or another Plan.
Update all references atomically: heading, marker, Tickets index, dependencies,
checklists, evidence tags/summaries, docs, commit/PR descriptions and pending
handoffs. Keep evidence content and failure history. Read back and rerun
impacted contract/link checks and required acceptance before publication.
If ownership is ambiguous, a scan fails, or IDs are exhausted, stop rather than
publish a collision. This repair grants no publication authority.

### Legacy continuation

Existing Issue requirements remain on their original Issue authority, including
scope extensions: single-Issue sections stay there, and legacy Plan/child-Issue
contracts, checkpoints, statuses and append-only comments stay on the original
Issues. Read the original Plan and every required Ticket contract and evidence;
preserve IDs, branch/base, PR and history. Extend the existing contract or add
a behavior Ticket under its original format after the global ID scan. Do not
migrate, copy into Markdown, supersede/close children for migration, or dual
write. Required Issue read/write failures block readiness. After verified merge,
mark the legacy Plan/Tickets done and close their Issues using original rules.
All independent new requirements use Markdown. A completed merged Plan is never
reopened; subsequent requirements receive new Plans.

### Effective completion from verified merge

For Markdown Plans, a verified merged PR is the authoritative completion fact:
effective Plan and Ticket status is `done` even if the merged file still says
`in_review` or `PR: null`. Do not create a post-merge status-only commit or PR,
edit the default branch, or reopen the Plan merely to synchronize fields.
Resolve the recorded PR; if PR is null or stale, discover the repository PR by
exact recorded head branch and base, then verify its merged state and that its
merged scope includes this Plan file and every current Ticket's accepted work.
Check repository, branch/base, merged commit and full scope against the contract;
branch deletion, closed/unmerged PRs, names alone or unrelated merged PRs never
prove completion. Ambiguous/missing PR or incomplete scope proof blocks a done
claim. Report the verified PR URL/merge fact as external evidence without
requiring a Markdown write. Before merge, readiness is not done.

### Branch, status and handoff

Record exact `Branch` and `Base` before implementation edits, using
`<type>/<plan-id>-<short-description>`, and verify them on resume. Do not share
a branch across Plans or create Ticket branches. Keep every Ticket, test and
document on the Plan branch. Prerequisites are validated on that branch; no
Ticket-level merge is required.

| Boundary | Update |
|---|---|
| Branch work starts | Plan `in_progress`; exact Branch/Base recorded. |
| Blocking dependency/environment | Affected Plan/Ticket `blocked`. |
| Local verification passes; publication awaits user | Keep the Plan checkpointed with accepted evidence, not `blocked`. |
| Same-requirement scope added before merge | Update Plan/Ticket scope, index, dependencies and validation; Plan `in_progress`; retain PR; revalidate affected work. |
| One Plan PR opens or is updated with authorization | Head/base match Branch/Base and current requirement checks pass; Plan `in_review`, record PR URL; Tickets may enter `in_review`. |
| PR verified merged | Effective Plan/Tickets `done` from verified merged PR; no post-merge Markdown write. |

Keep `PR: null` until a PR exists. Branch/PR existence alone never means done.
The Plan is ready for its one PR only after every Ticket acceptance and relevant
Plan-level integration/regression checks pass. Any failure blocks publication.
Commit-only and push-only stop at their authorized boundaries. Human-authorized
delivery follows verification, redaction, commit/push/PR, then separately
authorized merge unless full delivery explicitly includes merge. When repository
state changes, `docs/Repo_Current_State.md` holds a compact active-Plan path/anchor (or legacy Issue) pointer,
not a copied Plan/backlog.

## Output structure

Use `# Plan` and `# Tickets`. For persisted work, include canonical Plan and
Ticket section paths/anchors, metadata, actual branch/base, milestones and Ticket index.
Before persistence, return only scope/options discussion, not an
implementation-ready contract; persistence remains required before implementation edits.

Each Ticket uses these fields:

```text
### T0001
<!-- codex-ticket-id: T0001 -->
Title: <behavior/capability title>
Section: docs/plans/<plan-id>.md#t0001
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
Evidence Summary: <accepted snapshot/results, preserved failures and evidence references>
```

On successful persistence, return `# Plan` and `# Tickets` with file paths/anchors and current
metadata. On required Plan read/write failure, return a concise blocked report
naming the operation and the affected paths or legacy URLs; do not return a chat-only plan or
readiness claim.
