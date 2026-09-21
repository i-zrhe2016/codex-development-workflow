---
name: plan-to-ticket
description: Convert any requirement, including feature, bug-fix, refactor, documentation, configuration, dependency, test, or CI/CD work, into exactly one Plan, one or more behavior Tickets, and small, dependency-ordered Slices for a main agent and optional bounded delegation. Persist the Plan and every Ticket to GitHub Issues before the single Plan branch starts; each Slice includes boundaries, observable acceptance criteria, relevant context, test strategy, a bounded test level, concrete test cases, and validation guidance.
---

# Plan to Ticket

Convert any requirement into exactly one Plan, the smallest useful set of
behavior Tickets within that Plan, and execution-ready Slices within each
Ticket. Every Plan gets at least one Ticket; complex or dependency-driven work
adds more Tickets and Slices without adding another delivery branch or merge.

## Core principle

Every requirement is recorded as exactly one Plan Issue and at least one child
Ticket Issue before the Plan branch starts. Ticket count scales with the
requirement: a single-behavior requirement is one Ticket with one Slice, while
larger or dependency-driven work adds more Tickets and Slices under the same
Plan.

Create additional Tickets only when they reduce implementation complexity more
than they add planning overhead. Never create a second Plan for behavior that
belongs to the same requirement; a smaller Ticket changes planning detail only,
and the parent workflow still requires one Plan branch, tests, applicable
redaction, commit, push, one PR and one merge.

When this skill creates a plan or ticket, GitHub Issues are the mandatory
durable store. Persistence is not an optional output mode. Chat output is only
a convenience copy containing links to the Issues; it is never the source of
truth. Issue persistence is always required once this skill produces a Ticket.

## Rules

- Do not treat text-only output as completion.
- Do not implement the planned product or repository code.
- Do not call tools unless repository context is explicitly available and needed.
- For persisted planning, use the available GitHub Issues connector and the
  current repository's `owner/name` from its remote. If the repository target,
  connector, authentication, or write permission is unavailable, stop with a
  blocked result. Do not fall back to chat-only output, local Markdown plans,
  `docs/plans/`, `docs/tickets/`, or an unapproved ad-hoc API client.
- Before creating anything, search for the exact plan marker and each exact
  ticket marker in the target repository. Reuse and update one existing
  matching Issue; do not create duplicates. If more than one candidate matches,
  stop and request resolution.
- Create or update one Plan Issue and every required child Ticket Issue before
  creating the Plan branch. Use the repository's default branch as the base
  unless the request explicitly establishes another base.
- A Plan Issue is always required, including when the Plan contains one Ticket.
- Assign the Plan one implementation branch and base branch before branch work
  starts. Use `<type>/<plan-id>-<short-description>` and keep the same branch
  for every Ticket, Slice, test, and related document in the requirement.
- Treat the Plan Issue and implementation branch as a one-to-one pair. Write
  the exact `Branch` and `Base` metadata to the Plan Issue before the first
  edit, set Plan `Status: in_progress` when branch work starts, and verify
  those values when resuming the branch.
- Keep all Tickets and their internal Slices on the Plan branch. Do not share a
  branch across Plans or create separate branches for Tickets or Slices.
- Ticket dependencies describe execution order within the Plan branch. Do not
  wait for or create a Ticket-level merge before starting a dependent Ticket;
  validate the prerequisite Ticket/Slices on the same Plan branch first.
- Create one GitHub Issue per behavior ticket. Every ticket Issue must retain
  its goal, scope, dependencies, acceptance criteria, validation, and the
  execution metadata block defined below.
- Update the Plan Issue and each child Ticket Issue as work progresses. The
  allowed status values are `planned`, `in_progress`, `blocked`, `in_review`,
  and `done`.
- `planned`, `in_progress`, `blocked`, and `in_review` Issues remain open. Set
  the Plan and all child Tickets to `done` and close them only after the single
  Plan PR is verified merged; never mark a Plan done merely because its branch
  or PR exists.
- Keep the Plan's branch, base, and PR references current in the Plan Issue.
  Use `PR: null` until the one Plan PR exists, then record its canonical URL or
  number. The PR head/base must match the Plan's `Branch`/`Base`; set the Plan
  to `in_review` when it opens. Child Tickets keep only their Plan link,
  status, dependencies, acceptance, and Slice metadata.
- Keep `docs/Repo_Current_State.md` as a compact pointer to the active Issue
  when repository state is updated; do not copy the plan or backlog into it.
- Keep tickets small, focused, independently understandable, and independently verifiable.
- Prefer one behavior or capability per ticket, not one file or one coding step per ticket.
- Do not use Plan, Ticket, and Slice as synonyms: a Plan is the requirement
  delivery boundary; a Ticket is the child behavior boundary; a Slice is an
  execution unit inside that Ticket.
- Keep tests with the behavior they validate; do not create separate "write tests" tickets unless test infrastructure itself is the deliverable.
- First establish the Ticket boundaries and ticket-level dependencies, then
  order each Ticket's Slices by real implementation dependency and clear
  ownership boundaries.
- Do not require delegation. When the parent workflow delegates, identify
  bounded Slices with disjoint ownership that are independently executable;
  keep dependent, overlapping, or shared-interface/configuration Slices
  sequential. Never name the agent that should run a Slice; the host selects it.
- Avoid unrelated refactors, dependency upgrades, formatting changes, speculative abstractions, or future features.
- If repository context exists, respect its architecture, conventions, constraints, and current state.
- If exact commands or implementation details are unknown, describe validation behavior instead of inventing commands.
- Do not prescribe strict RED/GREEN for trivial or mechanically verifiable changes. Let the downstream testing workflow choose the appropriate test mode.

## GitHub Issues persistence contract

Every requirement uses exactly one Plan Issue for the overall plan, delivery
metadata, and Ticket index, plus one child Issue for each Ticket. The Plan Issue contains the
overall goal, milestones, Plan `Status`/`Branch`/`Base`/`PR`, and links to child
Issues; it must not duplicate mutable Ticket acceptance or Slice progress. The
child Issue is the authoritative record for that Ticket's current status,
Plan link, boundaries, dependencies, nested Slice plan, and acceptance state.
Comments may hold append-only progress evidence, but they do not replace the
structured fields in the Issue body. A one-Ticket requirement still has both the
Plan Issue and its child Ticket Issue.

## Naming contract

Use separate stable identifiers for plans, Tickets, and Slices, and keep the
human-readable Issue titles aligned with those identifiers:

- A plan ID is a stable lowercase kebab-case slug, such as
  `persist-plan-to-ticket-github-issues`. It is written only in the
  `codex-plan-id` marker and must be unique within the target repository.
- A Plan Issue title is exactly `[PLAN] <short plan title>`. A Plan Issue exists
  for every requirement, including a Plan with one Ticket.
- A Ticket ID is an uppercase `T` followed by exactly four zero-padded decimal
  digits, such as `T0016`. Allocate IDs in repository scope: scan open and
  closed Issue bodies for exact `codex-ticket-id` markers, then choose a value
  greater than every existing valid ID. Never reuse an ID. Historical duplicate
  IDs remain legacy records and are not renumbered by this contract.
- A Ticket Issue title is exactly `[T0016] <short behavior/capability title>`,
  replacing the example ID and title with the Ticket's values. The title must
  describe a reviewable behavior or capability, not an implementation step.
- A Slice ID is `S` plus the parent Ticket's four digits, a dot, and a
  one-based ordinal, such as `S0016.1`. A Plan branch uses the lowercase Plan
  slug in `<type>/<plan-id>-<short-description>`.
- The GitHub Issue number is a link target, not a plan or Ticket identifier.

When reusing a matching Issue, normalize its title to the canonical format
while retaining its stable marker and identifier. Resolve legacy duplicate IDs
by their exact marker and plan association; if that still identifies more than
one Issue, stop rather than guessing.

Use stable markers so retries and later sessions can find the same records:

```text
<!-- codex-plan-id: <stable-plan-slug> -->
<!-- codex-ticket-id: T0016 -->
```

The Plan Issue should contain:

- the stable plan marker;
- the overall goal and milestones;
- `Status`, `Branch`, `Base`, and `PR` metadata;
- a Ticket index linking each Ticket ID to its GitHub Issue; and
- the Ticket dependency order and one-merge completion rule.

The Plan Issue should begin with this metadata block, replacing values with the
actual Plan data:

```yaml
Status: planned
Branch: <type>/plan-slug-short-description
Base: main
PR: null
Tickets: [T0001]
```

Each Ticket Issue should begin with this metadata block, replacing values with
the actual Ticket data:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

The Ticket Issue body uses the Ticket structure in this skill, including Goal,
Dependencies, Scope, Out of scope, Function Checklist, Requirements,
Non-goals, and Ticket Acceptance Criteria, followed by one or more nested Slice
sections. Each Slice section includes its own Goal, Scope, Dependencies,
Acceptance Criteria, Test Cases, Relevant Context / Files, Test Strategy, Test
Level, and Validation Command. Keep the Plan body current when its branch, base,
Ticket index, or PR changes; keep each Ticket body current when its dependency,
acceptance boundary, or Slice plan changes.

Persist in this order:

1. Resolve the target repository and base branch.
2. Generate the plan and dependency-ordered tickets in memory.
3. Search for the exact stable plan/ticket markers, check ID collisions, and
   resolve any existing Issues.
4. Create or update the Plan Issue with its delivery metadata and Ticket index.
5. Create or update every initial Ticket Issue sequentially, preserving the
   required metadata and linking the Plan and dependencies to Issue URLs.
6. Verify the Plan Ticket index points to every child Issue.
7. Only after all required writes succeed, return the Plan/Ticket links and
   allow the single Plan branch to start.

If a write fails after some Issues were created, report the created Issue URLs
and the failed operation, mark the affected Issue `blocked` when that update is
still possible, and do not claim the plan is persisted or ready for
implementation. Never create a local mirror to compensate for a failed write.

During implementation, update the Plan Issue and child Ticket Issues on the
shared Plan branch at these boundaries:

- Plan branch work starts: Plan `Status: in_progress`;
- a blocking dependency or environment problem appears: affected Plan/Ticket
  `Status: blocked`;
- the single Plan pull request is opened: Plan `Status: in_review` and set
  `PR`; child Tickets may also be set to `in_review`;
- the Plan pull request is merged: set Plan and all child Tickets to `done`,
  close them, and retain the merged PR reference on the Plan Issue.

Do not start a dependency-blocked Ticket merely to fill metadata. A dependent
Ticket becomes ready when its prerequisite Ticket/Slices are complete and
validated on the same Plan branch; no prerequisite merge is needed. When every
Ticket acceptance boundary passes, the Plan is ready to open or update its one
pull request. The parent workflow starts publication immediately after
that PR is created or updated, fixes blocking findings through the
Test/Redaction/Commit/Push loop, and delivers the requirement only after the Plan
pull request is merged.

## Planning Process

Before writing the output, determine internally:

1. The one requirement and final desired outcome represented by the Plan.
2. How many Tickets the requirement needs.
3. The minimum foundations required first.
4. The smallest independently reviewable behavior Tickets within the Plan.
5. The dependency order between Tickets on the shared Plan branch.
6. The smallest independently verifiable Slices within each Ticket.
7. The dependency order between Slices and any safe delegation boundaries.
8. The scope boundaries that prevent drift into another Plan/requirement.
9. The observable acceptance criteria for each Slice.
10. The test cases and validation evidence needed to prove each Slice and the
    final Plan.

Do not expose internal reasoning.

## Ticket Sizing

A good ticket is a behavior unit a coding agent can implement and test on the
shared Plan branch before the Plan PR opens, without needing to re-plan the
feature midway.

Split a ticket when:

- it contains multiple independent behaviors;
- it crosses unrelated subsystems with separate verification targets;
- it requires unrelated architecture decisions;
- part of it can be completed and verified independently;
- failure in one part would make the remaining work ambiguous.

Do not over-split by implementation mechanics.

Prefer this:

```text
T0001 - Authentication core
        token validation + tests

T0002 - Protected API routes
        middleware integration + tests

T0003 - Login UI
        form/session behavior + tests
```

Avoid this:

```text
T0001 - Create file
T0002 - Add class
T0003 - Add method
T0004 - Add import
T0005 - Write tests
```

A useful heuristic:

> If the ticket cannot be reviewed and verified as a behavior boundary inside
> the Plan, split it. If splitting produces only mechanical steps, merge it
> back into the behavior ticket.

After the Ticket boundaries are fixed, split each Ticket into one or more
execution-ready Slices. A Slice may be delegated or run sequentially, but it
must remain inside its parent Ticket and must not become a separate branch or
Issue. Do not split a Ticket into Slices before its behavior boundary and
dependencies are clear.

## Function Checklist

For each behavior ticket, list the concrete capabilities that must exist when the ticket is complete.

Keep the checklist behavioral and implementation-neutral when possible.

Prefer:

- Retry server errors.
- Do not retry client errors.
- Stop after three attempts.
- Preserve the final error.

Avoid:

- Create `retry.ts`.
- Add a `for` loop.
- Import helper X.

The checklist is the bridge between planning and testing: downstream testing should be able to map every important checklist item to acceptance criteria or test evidence.

## Acceptance Criteria

Write observable outcomes, not vague quality statements.

Prefer:

- `POST /api/login` returns HTTP 200 for valid credentials.
- Invalid credentials return HTTP 401.
- Existing authenticated routes continue to work.

Avoid:

- Works correctly.
- Code is clean.
- Feature is complete.

Acceptance criteria define **what must be true**. Test cases define **how that behavior will be exercised**.

## Test Cases

For each behavior ticket, provide a concise set of concrete cases derived from the requirements and acceptance criteria.

Prefer 3-7 high-value cases over exhaustive low-signal matrices.

Include when relevant:

- primary success path;
- important boundary or failure path;
- state transition;
- regression case for a bug fix;
- integration boundary touched by the ticket;
- browser-visible flow only when user interaction is part of the behavior.

Example:

```text
Test Cases
- HTTP 500 triggers a retry.
- HTTP 502 triggers a retry.
- HTTP 400 is returned without retry.
- A second-attempt success returns normally.
- Three failed attempts return the final error.
```

Do not invent framework-specific test commands or fixture details when the repository context does not establish them.

## Validation

Specify the smallest reliable validation path for the Ticket and the final Plan.

When repository context provides exact commands, use them. Otherwise describe the expected validation layer, for example:

- focused unit/API tests for retry behavior;
- affected package integration tests;
- typecheck and lint for the changed module;
- real-browser validation for the login flow.

Do not default every ticket to a full test suite or browser E2E run.

## Dependencies and Sequencing

Use explicit ticket IDs.

Ticket dependencies describe the order in which the main agent can execute
Tickets on the shared Plan branch. They never create a Ticket branch or merge.
Slice dependencies describe the order in which Slices inside a ready Ticket can
be executed. They are not an instruction to delegate: independent Slices are
candidates for the parent workflow's delegation decision, while dependent or
overlapping Slices remain sequential.

Example:

```text
T0001 - API contract
Dependencies: None

T0002 - Backend implementation
Dependencies: T0001

T0003 - Frontend implementation
Dependencies: T0001

T0004 - End-to-end integration
Dependencies: T0002, T0003
```

Do not create artificial dependencies, but keep the execution order explicit.
Shared files, schemas, interfaces, migrations, or generated artifacts are
reasons to sequence work carefully and define an ownership boundary before any
delegation.

## Re-planning Boundary

Tickets are behavior boundaries inside a Plan, not contracts with reality.

If implementation reveals that a ticket requires a materially different design, new subsystem, or unrelated behavior:

- stop expanding the current Ticket;
- preserve completed valid work;
- split or re-plan the newly discovered work;
- add a Ticket under the same Plan when the behavior is still part of the same
  requirement, or create a new Plan when it is a separate requirement and merge;
- update dependencies rather than silently widening scope.

Do not pre-split speculative edge cases before evidence shows they need independent treatment.

## Output Format

After the persistence contract succeeds, use this structure. Include the
canonical Plan Issue URL and the canonical Issue URL for every child Ticket;
these links are the durable handoff for later sessions and agents. List the
Slices nested under their parent Ticket. A Slice inherits its Ticket Issue and
the Plan's branch and base metadata; it does not create delivery metadata.

# Plan

Plan Issue title: `[PLAN] <Short plan title>`

Plan Issue: <Canonical GitHub plan Issue URL>

**Plan branch**

- <type>/plan-slug-short-description

**Base branch**

- main

```yaml
Status: planned
Branch: <type>/plan-slug-short-description
Base: main
PR: null
Tickets: [T0001]
```

1. <Milestone>
2. <Milestone>
3. <Milestone>

# Tickets

### T0001 - <Short behavior/capability title>

**Issue title**

`[T0001] <Short behavior/capability title>`

**Issue**

<Canonical GitHub Issue URL>

```yaml
Plan: <Canonical GitHub Plan Issue URL>
Status: planned
Dependencies: []
```

**Ticket Goal**

<One concrete outcome.>

**Ticket Dependencies**

- None

**Ticket Scope**

- <What may be changed>
- <Relevant components or behavior>

**Ticket Out of scope**

- <Unrelated areas>
- <Future-ticket functionality>

**Function Checklist**

- [ ] <Required behavior>
- [ ] <Required behavior>

**Requirements**

- <Concrete requirement>
- <Important behavior or edge case>

**Non-goals**

- <Explicitly excluded work>

**Ticket Acceptance Criteria**

- <Observable result covering the Ticket>
- <Observable result covering the Ticket>

**Slices**

#### S0001.1 - <Execution-ready Slice title>

**Goal**

<One concrete Slice outcome within T0001.>

**Scope**

- <Files, interfaces, or behavior owned by this Slice>

**Out of scope**

- <Future Slice or unrelated behavior>

**Dependencies**

- <Earlier Slice ID in T0001, or None>

**Acceptance Criteria**

- <Observable result for this Slice>

**Test Cases**

- <Concrete success/failure/boundary case>

**Relevant Context / Files**

- <Repository files, interfaces, or state needed for this Slice>

**Test Strategy**

- <Test-first, focused-after-implementation, static-only, browser, or other justified strategy>

**Test Level**

- <minimal / focused / regression / full>

**Validation Command**

- <Smallest relevant validation command, when known>
- <Expected evidence when an exact command is not yet known>

Repeat the `S0001.x` section for each Slice in T0001, then repeat the Ticket
and nested Slice sections for T0002, T0003, and later Tickets.

## Existing Repository Context

When repository context is available:

- Read and respect `AGENTS.md` if present.
- Read `docs/Repo_Current_State.md` if present.
- Read architecture or design documentation when directly relevant.
- Treat repository documentation as guidance, but verify important details against actual code when needed.
- Reuse existing patterns, tests, fixtures, commands, and abstractions before proposing new ones.
- Identify existing validation commands from package scripts, task runners, CI configuration, or test documentation instead of guessing them.

Do not require these files to exist. Keep tickets implementation-neutral when repository context is unavailable.

## Final Output Constraint

On successful persistence, return only the Plan and Tickets sections, with the
Issue URLs and current metadata included. Do not add commentary, explanations,
code, or implementation after the tickets. If any required GitHub Issue read or
write fails, return only a concise blocked report naming the failed operation
and any Issue URLs already created; do not return a chat-only plan or claim that
the tickets are ready for implementation.
