# Architecture Overview

## Scope

This repository packages the `plan-to-ticket` specialist inside a larger
main-agent workflow. Its job is to convert a change request into a compact
plan and small engineering Slices with boundaries that can support optional
delegation. There is no runtime service, persistent
data store, external API, or deployment process in this package.

## Logical architecture

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The source for this diagram is
[plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
It describes the behavior exposed by the skill package rather than an
application infrastructure topology.

## Responsibilities

| Asset | Responsibility | Boundary |
| --- | --- | --- |
| [`skills/plan-to-ticket/SKILL.md`](../../../skills/plan-to-ticket/SKILL.md) | Defines trigger metadata, planning rules, Slice structure, scope constraints, and verification expectations. | It produces planning text; it does not implement the planned change. |
| [`skills/plan-to-ticket/agents/openai.yaml`](../../../skills/plan-to-ticket/agents/openai.yaml) | Supplies the display name and short interface description. | It describes the skill in the interface; it does not define planning behavior. |
| This documentation package | Explains the bundle structure, behavior, output contract, and maintenance expectations. | Documentation does not add executable behavior. |

## Request flow

1. A requestor provides a feature idea, requirement, bug-fix plan, refactor plan, or similar project change.
2. Codex uses the frontmatter description in `SKILL.md` to determine whether this skill applies.
3. The planning instructions use the available repository context and identify milestones, dependencies, scope boundaries, and verification.
4. The output follows the contract in `SKILL.md`: a `Plan` section followed by focused `Tickets`/Slice sections.
5. The main agent uses the Slices as implementation input, either executing
   them sequentially or passing independent, bounded work through the
   workflow's delegation gate.

## Design boundaries

- The skill is a single cohesive module because its trigger, planning rules, and output format are tightly coupled.
- The interface metadata is kept separate from behavior so presentation changes do not alter planning semantics.
- The skill does not prescribe a project framework, dependency, command, API shape, or deployment platform unless repository context establishes it.
- Slice verification describes observable checks. It does not claim that implementation has already been completed.
- The skill does not force multi-agent handoffs or parallel implementation; the
  parent workflow decides whether an independent Slice is safe to delegate.

## Slice output contract

Each behavior Slice should expose:

- Goal and Scope;
- Out of scope and Dependencies;
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
