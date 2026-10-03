---
name: plan-to-ticket
description: "Decompose feature, bug-fix, refactor, docs/config, dependency, test, CI/CD or other requirements into one Plan, behavior Tickets and dependency-ordered Slices. Persist GitHub Plan/Ticket Issues for complex, resumable, or explicitly persisted work; include boundaries, acceptance, context, test strategy/level/cases, and validation."
---

# Plan to Ticket

Own decomposition and Issue persistence, not product/repository implementation.
A **Plan** is a delivery batch with explicitly listed scope, which may include
one or multiple independent functionalities; a **Ticket** is a reviewable
behavior/capability within it; a **Slice** is an independently verifiable
execution unit inside a Ticket. Every Plan has at least one Ticket and every
Ticket at least one Slice. These terms are not interchangeable.

## Scope and sizing

Internally determine the desired outcome, necessary foundations, behavior
boundaries, Ticket dependencies, then Slice dependencies/ownership, scope
exclusions, observable acceptance, concrete cases, and Slice/final validation.
Do not expose internal reasoning.

- Use the smallest useful decomposition. One behavior may be one Ticket/one
  Slice; add Tickets only when reduced implementation complexity outweighs
  planning overhead. Multiple planned functionalities may share one Plan while
  retaining separate behavior Tickets and acceptance boundaries. Do not merge
  different existing Plans merely because they share a session.
- Split Tickets for independent behaviors, unrelated subsystems/architecture
  decisions or verification targets, independently completable parts, or parts
  whose failure makes the rest ambiguous. Each must be understandable,
  implementable and verifiable without mid-feature re-planning. Merge mechanical
  file/class/method/import steps back into behavior Tickets.
- Keep tests with their behavior; a separate test Ticket is justified only when
  test infrastructure is the deliverable. Avoid unrelated refactors, upgrades,
  formatting, speculative abstractions and future features/edge-case Tickets.
- Establish Ticket boundaries/dependencies before Slices. Slices stay nested in
  their Ticket: no separate Issue, branch, PR, merge or delivery metadata.
- Use explicit Ticket/Slice dependency IDs and real dependencies only. Validate
  prerequisites on the shared Plan branch before dependents; no Ticket-level
  merge is required. Do not start blocked Tickets just to fill metadata.
- Every Ticket, including docs/config/test, is the worker ownership boundary:
  one fresh implementer executes all its Slices in dependency order, and a separate fresh verifier
  checks all functionality scenarios. Do not divide Slices/scenarios across
  workers or reuse agents across Tickets. The coordinator chooses agents and
  safe concurrency under `AGENTS.md` and the develop/verify runtime rules;
  planning does not dispatch workers. Sequence dependent/overlapping files,
  interfaces, schemas, migrations, configuration and shared test state.
- If implementation reveals a materially different design, new subsystem or
  unrelated behavior, stop expanding the Ticket, preserve valid work and
  re-plan/update dependencies. Add a Ticket only after explicitly updating the
  batch's planned scope. New user-requested functionality follows the scope-update
  contract below; after merge it belongs to a new Plan. Do not silently widen scope.

## Updating an unmerged Plan

New user-requested functionality joins the same unmerged Plan as a new behavior
Ticket, whether or not its PR already exists. Before implementation edits:

1. Resolve the current Plan and confirm it has not merged; reuse its stable ID,
   Issue, branch/base and existing PR. After verified merge, create a new Plan
   with a new branch and eventual PR; never reopen the delivered Plan.
2. Search exact markers and allocate new Ticket/Slice IDs under the naming rules.
   Preserve existing Tickets and evidence; never duplicate a Plan or Ticket.
3. Update the Plan goal, explicit functionality scope, linked Ticket index,
   dependency order and batch validation; create the new Ticket Issue with its
   scope/dependencies/acceptance/Slices/validation and update impacted contracts.
   Verify every required write and index link before any new edits.
4. Set the expanded Plan to `in_progress`. If a PR exists, retain its URL and
   record that it is not ready for expanded scope. Preserve prior accepted and
   failed evidence, identify impacted acceptance and invalidate affected
   readiness; revalidate impacted Tickets and batch integration/regression before
   user-authorized publication or PR update. No per-feature PR or automatic merge.
5. Keep publication authority separate: prior authorization persists only for
   its stated batch/actions. Adding feature scope authorizes its requested work,
   not commit, push, PR update or merge of that scope. The user elects those
   actions and timing; preserve the same one-Plan branch/PR/merge if delivered.

Local verified functionality may stop with Plan/Tickets open and checkpointed.
Keep `in_progress` before review, or existing `in_review` for unchanged review
scope; awaiting a human publication decision is not `blocked`. Mark final
`done` and close only after verified merge.

## Repository context and validation

Call tools only when repository context is explicitly available and needed.
When available, respect `AGENTS.md`, `docs/Repo_Current_State.md`, directly
relevant architecture/design documents, conventions and constraints; none of
these files is required. Verify important documentation claims against code.
Reuse existing patterns, abstractions, frameworks, tests, fixtures and commands.
Find commands in package scripts, task runners, CI or test docs; never invent
commands, framework/fixture details or implementation assumptions. Without
context, remain implementation-neutral and describe expected validation layers.

For each Ticket, supply a behavioral, preferably implementation-neutral
Function Checklist mapping important capabilities to acceptance/test evidence.
Acceptance states **what must be true**, using observable outcomes rather than
vague quality claims; cases state **how to exercise it**. Prefer 3–7 high-value
cases, covering applicable success, boundary/failure, state transition, bug
regression, integration boundary and browser-visible interaction.

Specify the smallest reliable Slice/Ticket/final-Plan validation. Use known
commands, otherwise expected evidence/layer; do not default to full suites or
browser E2E. Let downstream testing choose its mode; do not force RED/GREEN for
trivial or mechanically verifiable changes.

## Persistence and delivery contract

Persist when work is complex, crosses modules, has internal dependencies, must
survive a session/resume by another agent, or the user requests persistence.
Small single-session work stays inline without Issues.

A persisted Plan owns **one Plan Issue, one child Issue per Ticket, one
branch, tests and, when delivery is elected, applicable redaction, commits/push,
one PR and one merge** for
all Tickets/Slices/documents. GitHub Issues are authoritative; chat is only a
linked convenience copy. No chat-only completion or local Markdown,
`docs/plans/`, `docs/tickets/` mirror/fallback is allowed.

Use the available GitHub Issues connector and current repository remote's
`owner/name`. Missing target, connector, authentication or write permission
blocks persistence; do not use an unapproved ad-hoc API client. All required
initial Issues must exist before creating the Plan branch; appended Tickets
and Plan updates must persist before their implementation edits.

### Naming and idempotency

- Plan ID: repository-unique stable lowercase kebab-case slug, recorded only in
  its `codex-plan-id` marker. Title: exactly `[PLAN] <short plan title>`.
- Ticket ID: `T` plus exactly four zero-padded decimal digits. Allocate in
  repository scope by scanning **open and closed Issue bodies** for exact
  `codex-ticket-id` markers; choose above every valid existing ID, never reuse.
  Historical duplicate IDs remain legacy records; do not renumber them.
  Title: exactly `[T0016] <short behavior/capability title>` using the real ID.
- Slice ID: `S` plus parent Ticket's four digits and one-based ordinal,
  e.g. `S0016.1`. GitHub Issue numbers are link targets, not Plan/Ticket IDs.
- Before any creation, search the exact Plan marker and each exact Ticket
  marker. Reuse/update the one match and normalize its title while retaining
  its stable marker/ID. Resolve legacy duplicates by exact marker and Plan
  association; multiple remaining candidates require resolution, never guessing
  or duplicate creation.

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

It also contains its marker, overall goal/milestones, explicit functionality
scope, linked Ticket index, Ticket dependency order, batch integration/regression
validation and one-merge completion rule. Do not duplicate mutable Ticket
acceptance or Slice progress there.

Every Ticket contains its stable marker and begins with actual execution metadata:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

Its body owns its goal, boundaries, dependencies, current status/acceptance and
nested Slice plan, using the structure below. Comments may hold append-only
progress evidence; they never replace structured body fields. Keep Plan
branch/base/index/PR and Ticket dependency/acceptance/Slice bodies current.
Child Tickets hold Plan link, status, dependencies, acceptance and Slice
metadata, never independent branch/base/PR metadata.

### Persistence sequence and failures

1. Resolve target repository and base (default branch unless explicitly
   established otherwise); generate the Plan and dependency-ordered Tickets in
   memory.
2. Search exact markers, check ID collisions and resolve/reuse existing Issues.
3. Create/update the Plan with delivery metadata and Ticket index.
4. Create/update every initial Ticket **sequentially**, preserving metadata and
   linking Plan/dependencies to canonical Issue URLs.
5. Verify the Plan index links every child. Return Plan/Ticket links and allow
   the single branch to start only after **all required writes succeed**.

If any required read/write fails, report the failed operation and created Issue
URLs; mark affected Issues `blocked` if still possible. Do not claim persistence
or implementation readiness, and never compensate with a local mirror.

### Branch, status and handoff

Assign the exact `Branch` and `Base` before branch work/first edit, using
`<type>/<plan-id>-<short-description>`; verify them on resume. Plan Issue and
branch are one-to-one: never share a branch across Plans or create Ticket/Slice
branches. Keep every Ticket/Slice/test/document on that branch.

Allowed statuses: `planned`, `in_progress`, `blocked`, `in_review`, `done`.
All except `done` remain open. Update Plan and child Tickets as work progresses:

| Boundary | Update |
|---|---|
| Branch work starts | Plan `Status: in_progress`; exact Branch/Base recorded. |
| Blocking dependency/environment | Affected Plan/Ticket `Status: blocked`. |
| Local verification passes; publication awaits user | Valid stopping point; keep Issues open with accepted evidence, not `blocked`. |
| New functionality appended before merge | Update goal/scope/index/dependencies/validation; Plan `in_progress`, retain existing `PR`; affected readiness requires revalidation. |
| One Plan PR opens or expanded PR is updated with authorization | Head/base match Branch/Base and current batch checks pass; Plan `Status: in_review`, `PR` canonical URL or number; Tickets may enter `in_review`. |
| PR verified merged | Plan and **all** children `done` and closed; retain merged PR on Plan. |

Keep `PR: null` until the PR exists and keep branch/base/PR references current.
Branch/PR existence alone never means done. Only after every Ticket's acceptance
and the batch's relevant integration/regression checks pass is the Plan ready
for its one PR; any failure blocks batch publication. The batch may use one
commit for multiple functionalities under `github-push-when-ready`'s staging and
message rules. The parent workflow stops at the requested local or publication
boundary; commit-only/push-only never forces a PR. Human-authorized delivery
follows Test/Redaction/Commit/Push/PR and a separately authorized merge (or
explicit full delivery scope). When repository
state is updated, `docs/Repo_Current_State.md` holds a compact active-Issue
pointer, never a copied Plan/backlog.

## Output structure

Use `# Plan` and `# Tickets`; nest Slices under their parent Ticket. For
persisted work include canonical Plan and every child Issue URL, current
metadata above, actual branch/base, milestones and linked Ticket index. Slices
inherit the Ticket Issue and Plan branch/base. For inline work omit nonexistent
Issue links/delivery metadata; keep the execution contracts.

Each Ticket uses these fields (repeat for every Ticket):

```text
### T0001 - <behavior/capability title>
Issue title: [T0001] <behavior/capability title>
Issue: <canonical child Issue URL, when persisted>
<execution metadata above, when persisted>
Ticket Goal: <one concrete outcome>
Ticket Dependencies: <explicit IDs or None>
Ticket Scope: <allowed components/behavior>
Ticket Out of scope: <unrelated/future work>
Function Checklist: <required behaviors as checkboxes>
Requirements: <concrete requirements and important edge cases>
Non-goals: <explicit exclusions>
Ticket Acceptance Criteria: <observable Ticket results>
Slices:
#### S0001.1 - <execution-ready title>
Goal: <one outcome inside T0001>
Scope: <owned files/interfaces/behavior>
Out of scope: <future/unrelated behavior>
Dependencies: <earlier Slice IDs in T0001 or None>
Acceptance Criteria: <observable Slice results>
Test Cases: <concrete success/failure/boundary cases>
Relevant Context / Files: <needed files/interfaces/state>
Test Strategy: <justified test-first/focused-after/static/browser/etc.>
Test Level: <minimal / focused / regression / full>
Validation Command: <smallest known commands, otherwise expected evidence>
```

On successful persistence, return **only** Plan and Tickets sections with URLs
and current metadata: no commentary, explanations, code or implementation
after Tickets. On required Issue read/write failure return **only** a concise
blocked report naming the operation and any created URLs, never a chat-only
plan or readiness claim.
