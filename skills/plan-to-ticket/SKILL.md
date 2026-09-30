---
name: plan-to-ticket
description: "Decompose a requirement into one Plan, behavior Tickets, and dependency-ordered execution Slices. Use for planning or decomposition before implementation. Persist the Plan/Tickets to GitHub Issues only when work is complex, must survive a session boundary, or persistence is explicitly requested. Do not implement code."
---

# Plan to Ticket

Convert one requirement into an executable Plan with the smallest useful behavior Tickets and Slices.

## Core model

- **Plan** = one delivery boundary and final outcome.
- **Ticket** = one reviewable behavior/capability boundary.
- **Slice** = one bounded execution unit inside a Ticket.
- One Plan owns one implementation branch, one PR, and one merge. Tickets/Slices do not get separate delivery branches.
- Small single-session work stays inline. Complex, cross-session, or explicitly persisted work uses GitHub Issues.

When persistence applies, load and follow [references/github-persistence.md](references/github-persistence.md). Do not load it for an inline plan.

## Process

1. Read only the repository context needed to understand the requirement, including applicable `AGENTS.md`, current state, affected code/contracts, and constraints.
2. Define the Plan outcome and out-of-scope boundary.
3. Split into the fewest behavior Tickets that reduce implementation ambiguity. Establish Ticket dependencies first.
4. Split each Ticket into the fewest independently verifiable Slices. Keep dependent/overlapping/shared-interface work sequential; delegation is optional.
5. Give every Slice observable acceptance criteria, relevant context/files, a test strategy, bounded test level, and validation guidance.
6. Persist only when the trigger above applies.
7. Stop after planning; do not implement.

## Sizing rules

Prefer behavior boundaries over file or coding-step boundaries. Keep tests with the behavior they prove; create a test-only Ticket only when test infrastructure itself is the deliverable.

Split a Ticket when it contains independent behaviors, unrelated subsystems/decisions, or a part that can be reviewed and verified independently. Merge mechanical Slices back when splitting adds ceremony without clearer ownership or validation.

Avoid unrelated refactors, dependency upgrades, formatting sweeps, speculative abstractions, and future features.

## Required output

### Plan

- Goal/final outcome
- Scope and important constraints
- Ticket order/dependencies
- Persistence decision

### Ticket

- Goal
- Scope / Out of scope
- Dependencies
- Function checklist stated as behavior, not implementation steps
- Ticket acceptance criteria
- One or more Slices

### Slice

- Goal
- Scope
- Dependencies
- Observable acceptance criteria
- Few high-signal test cases when useful
- Relevant context/files
- Test strategy
- Test level: `minimal`, `focused`, `regression`, or `full`
- Validation command when known; otherwise describe the required evidence instead of inventing a command

Acceptance criteria state what must be true; test cases state how it will be exercised.

For persisted planning, GitHub Issues are the durable source of truth. If the repository target, connector/authentication, or write permission is unavailable, return `BLOCKED`; do not create a parallel local Markdown backlog.
