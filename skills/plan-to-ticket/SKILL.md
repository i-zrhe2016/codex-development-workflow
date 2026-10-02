---
name: plan-to-ticket
description: "Decompose feature, bug-fix, refactor, docs/config, dependency, test, CI/CD or other requirements into one Plan, behavior Tickets and dependency-ordered Slices. Persist GitHub Plan/Ticket Issues for complex, resumable, or explicitly persisted work; include boundaries, acceptance, context, test strategy/level/cases, and validation."
---

# Plan to Ticket

Own decomposition and Issue persistence, not product/repository implementation.
A **Plan** is one requirement/delivery boundary; a **Ticket** is a reviewable
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
  planning overhead. Never split the same requirement into multiple Plans.
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
- Delegation is optional. Expose independently executable Slices with disjoint
  ownership; sequence dependent/overlapping work and shared files, interfaces,
  schemas, migrations, configuration or generated artifacts. Never name an
  executing agent; the host/parent workflow chooses.
- If implementation reveals a materially different design, new subsystem or
  unrelated behavior, stop expanding the Ticket, preserve valid work and
  re-plan/update dependencies. Add a Ticket if still the same requirement;
  otherwise create a separate Plan/delivery. Do not silently widen scope.

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
branch, tests, applicable redaction, commits/push, one PR and one merge** for
all Tickets/Slices/documents. GitHub Issues are authoritative; chat is only a
linked convenience copy. No chat-only completion or local Markdown,
`docs/plans/`, `docs/tickets/` mirror/fallback is allowed.

Use the available GitHub Issues connector and current repository remote's
`owner/name`. Missing target, connector, authentication or write permission
blocks persistence; do not use an unapproved ad-hoc API client. All required
Issues must exist before creating the Plan branch.

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

It also contains its marker, overall goal/milestones, linked Ticket index,
Ticket dependency order and one-merge completion rule. Do not duplicate mutable
Ticket acceptance or Slice progress there.

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
| One Plan PR opens | Head/base match Branch/Base; Plan `Status: in_review`, `PR` canonical URL or number; Tickets may enter `in_review`. |
| PR verified merged | Plan and **all** children `done` and closed; retain merged PR on Plan. |

Keep `PR: null` until the PR exists and keep branch/base/PR references current.
Branch/PR existence alone never means done. Once all Ticket acceptance passes,
the Plan is ready for its one PR. The parent workflow starts publication
immediately after PR creation/update, fixes blockers through
Test/Redaction/Commit/Push, and delivers only after the merge. When repository
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
