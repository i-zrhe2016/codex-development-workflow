# Architecture Overview

## Scope

This repository packages the `plan-to-ticket` specialist inside a larger
main-agent workflow. Its job is to convert every change request into exactly one
Plan, behavior Tickets, and small engineering Slices within each Ticket with
boundaries that can support optional delegation, then persist the Plan and
Tickets to GitHub Issues. There is no
application runtime, custom API client, or local ticket database in this
package; GitHub Issues are the workflow's external durable store.

## Logical architecture

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The source for this diagram is
[plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
It describes the behavior exposed by the skill package rather than an
application infrastructure topology.

## Responsibilities

| Asset | Responsibility | Boundary |
| --- | --- | --- |
| [`skills/plan-to-ticket/SKILL.md`](../../../skills/plan-to-ticket/SKILL.md) | Defines trigger metadata, Plan/Ticket/Slice planning rules, Issue persistence contract, Slice structure, scope constraints, and verification expectations. | It plans and persists Issue records; it does not implement the planned change. |
| [`skills/plan-to-ticket/agents/openai.yaml`](../../../skills/plan-to-ticket/agents/openai.yaml) | Supplies the display name and short interface description. | It describes the skill in the interface; it does not define planning behavior. |
| GitHub Issues connector | Creates, finds, and updates one Plan Issue plus one child Issue per Ticket. | It is the external durable authority; no local Markdown mirror is maintained. |
| This documentation package | Explains the bundle structure, behavior, output contract, and maintenance expectations. | Documentation does not add executable behavior. |

## Request flow

1. A requestor provides a requirement, including a feature idea, bug-fix plan, refactor plan, documentation, configuration, dependency, test, or CI/CD change.
2. Codex uses the frontmatter description in `SKILL.md` to determine whether this skill applies.
3. The planning instructions use the available repository context to identify
   milestones, Ticket boundaries, Ticket dependencies, scope boundaries, and
   verification.
4. The skill decomposes each Ticket into dependency-ordered execution Slices
   with their own acceptance and validation contract.
5. The skill resolves the repository's GitHub target, searches exact stable
   markers and Ticket ID collisions, normalizes matching Issue titles, and
   creates or updates one Plan Issue and its Ticket Issues before the Plan
   branch starts.
6. The skill assigns or resumes one branch and base branch for the Plan, records
   those values on the Plan Issue, and keeps all Tickets on that branch.
7. The successful output follows the contract in `SKILL.md`: a `Plan` section
   followed by Ticket sections containing nested Slices and canonical Issue
   links, with the Plan branch handoff fields on the Plan section.
8. The main agent uses the Slices as implementation input, either executing
   them sequentially or delegating independent, bounded work.

## Design boundaries

- The skill is a single cohesive module because its trigger, planning rules, and output format are tightly coupled.
- The interface metadata is kept separate from behavior so presentation changes do not alter planning semantics.
- The skill does not prescribe a project framework, dependency, command, or deployment platform unless repository context establishes it. It requires the available GitHub Issues connector for persistence but does not implement a custom API client.
- Slice verification describes observable checks. It does not claim that implementation has already been completed.
- A required GitHub Issue failure blocks completion; chat output and local Markdown are not persistence fallbacks.
- The skill does not force multi-agent handoffs or parallel implementation; the
  parent workflow decides whether an independent Slice is safe to delegate.
- Each Plan Issue maps to one implementation branch and one PR; all child
  Tickets and internal Slices share that branch, and the PR head/base must match
  the Plan Issue metadata.
- Plan Issue titles use `[PLAN] <short plan title>`; Ticket Issue titles
  use `[T####] <short behavior/capability title>`. New `T####` identifiers are
  repository-scoped, four-digit, monotonically allocated, and never reused;
  historical duplicate IDs remain legacy records.
- Every requirement has exactly one Plan Issue and at least one Ticket Issue; a
  single-behavior requirement is one Ticket with one Slice, and the Plan's
  branch, PR, `pr-review`, merge, and cleanup gates remain mandatory exactly
  once.

## Ticket-to-Slice hierarchy

The Plan is the independently deliverable requirement boundary. Each Ticket is an
independently reviewable behavior boundary inside that Plan and contains one or
more execution-ready Slices. Ticket dependencies decide execution order on the
Plan branch; Slice dependencies decide order inside a Ticket. All Tickets and
Slices for one Plan share the Plan Issue's branch.

## Slice output contract

Each behavior Slice should expose:

- Goal and Scope;
- Out of scope and Dependencies;
- Plan branch and Base branch inherited by the Slice;
- Acceptance Criteria;
- Relevant Context / Files;
- Test Strategy and Test Level;
- Test Cases; and
- Validation Command.

## Change guidance

When changing planning behavior:

1. Update the relevant rule or output-contract section in
   `skills/plan-to-ticket/SKILL.md`.
2. Check that the architecture boundaries and request flow in this document remain accurate.
3. Update this documentation index or repository layout if files or responsibilities change.
4. Verify the Markdown structure, frontmatter, and any rendered diagram before committing.
