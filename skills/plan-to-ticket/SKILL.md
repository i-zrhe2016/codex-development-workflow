---
name: plan-to-ticket
description: Convert a feature idea, requirement, implementation plan, bug-fix plan, refactor plan, or project change into a concise implementation plan and small, dependency-ordered Slices for a main Codex agent and optional bounded workers. Use for complex or multi-step work that benefits from execution-ready Slices. Each behavior Slice includes boundaries, observable acceptance criteria, relevant context, test strategy, a bounded test level, concrete test cases, and validation guidance. Output text only and do not implement code.
---

# Plan to Ticket

Convert complex or dependency-driven work into the smallest useful set of execution-ready tickets.

## Core principle

Create tickets only when they reduce implementation complexity more than they add workflow overhead.

Do not ticket trivial work that can be implemented and verified in one focused pass.

## Rules

- Output text only.
- Do not implement code.
- Do not call tools unless repository context is explicitly available and needed.
- Keep tickets small, focused, independently understandable, and independently verifiable.
- Prefer one behavior or capability per ticket, not one file or one coding step per ticket.
- Keep tests with the behavior they validate; do not create separate "write tests" tickets unless test infrastructure itself is the deliverable.
- Order Slices by real implementation dependency and clear ownership boundaries.
- Do not require delegation. When the parent workflow enables its delegation
  gate, identify independent Slices that are safe to delegate and keep
  dependent or overlapping Slices sequential.
- Avoid unrelated refactors, dependency upgrades, formatting changes, speculative abstractions, or future features.
- If repository context exists, respect its architecture, conventions, constraints, and current state.
- If exact commands or implementation details are unknown, describe validation behavior instead of inventing commands.
- Do not prescribe strict RED/GREEN for trivial or mechanically verifiable changes. Let the downstream testing workflow choose the appropriate test mode.

## Planning Process

Before writing the output, determine internally:

1. The final desired outcome.
2. Whether tickets are actually necessary.
3. The minimum foundations required first.
4. The smallest independently verifiable behavior slices.
5. The real dependency order and any safe delegation boundaries.
6. The scope boundaries that prevent drift.
7. The observable acceptance criteria for each Slice.
8. The test cases and validation evidence needed to prove each Slice.

Do not expose internal reasoning.

## Ticket Sizing

A good ticket is a unit a coding agent can implement, test, and review without needing to re-plan midway.

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

> If the ticket cannot be reviewed and verified independently, split it. If splitting produces only mechanical steps, merge it back into the behavior ticket.

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

Specify the smallest reliable validation path for the ticket.

When repository context provides exact commands, use them. Otherwise describe the expected validation layer, for example:

- focused unit/API tests for retry behavior;
- affected package integration tests;
- typecheck and lint for the changed module;
- real-browser validation for the login flow.

Do not default every ticket to a full test suite or browser E2E run.

## Dependencies and Sequencing

Use explicit ticket IDs.

Dependencies describe the order in which the main agent or a delegated worker
can execute the Slices. They are not an instruction to delegate: independent
Slices may be considered by the parent workflow's delegation gate, while
dependent or overlapping Slices remain sequential.

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

Tickets are plans, not contracts with reality.

If implementation reveals that a ticket requires a materially different design, new subsystem, or unrelated behavior:

- stop expanding the current ticket;
- preserve completed valid work;
- split or re-plan the newly discovered work;
- update dependencies rather than silently widening scope.

Do not pre-split speculative edge cases before evidence shows they need independent treatment.

## Output Format

Always use this structure.

# Plan

1. <Milestone>
2. <Milestone>
3. <Milestone>

# Tickets

### T0001 - <Short behavior/capability title>

**Goal**

<One concrete outcome.>

**Dependencies**

- None

**Scope**

- <What may be changed>
- <Relevant components or behavior>

**Out of scope**

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

**Acceptance Criteria**

- <Observable result>
- <Observable result>

**Test Cases**

- <Concrete success/failure/boundary case>
- <Concrete regression/integration case when relevant>

**Relevant Context / Files**

- <Repository files, interfaces, or state needed for this Slice>

**Test Strategy**

- <Test-first, focused-after-implementation, static-only, browser, or other justified strategy>

**Test Level**

- <minimal / focused / regression / full>

**Validation Command**

- <Smallest relevant validation command, when known>
- <Expected evidence when an exact command is not yet known>

---

Repeat for T0002, T0003, and later tickets.

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

Return only the Plan and Tickets sections. Do not add commentary, explanations, code, or implementation after the tickets.
