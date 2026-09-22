# Plan to Ticket

`plan-to-ticket` is the planning specialist for the main-agent workflow. It
turns a requirement, including a feature, bug fix, refactor, documentation,
configuration, dependency, test, or CI/CD change, into one Plan, behavior
Tickets, and dependency-ordered Slices within each Ticket, and persists the Plan
and its Tickets to GitHub Issues when the work is complex, must survive a
session boundary, or the user asks for a persisted plan.

The executable skill source is maintained at
[`skills/plan-to-ticket/`](../../../skills/plan-to-ticket/). This document and
its diagrams are the migrated documentation for that local bundle; they do not
describe an application runtime or a custom API/database service. GitHub Issues
are the external durable store used by the planning workflow.

## Architecture

![Plan Ticket Slice work decomposition](../../diagrams/drawio/plan-ticket-slice.svg)

Editable overview: [`plan-ticket-slice.drawio`](../../diagrams/drawio/plan-ticket-slice.drawio)

Detailed Plan-to-Ticket logical architecture:

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The diagrams-as-code source is available at
[diagrams/plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
The full explanation is in [architecture.md](architecture.md).

## What it does

When the skill is selected for a planning request, it:

1. Normalizes the original request into a Requirement Contract with stable
   Requirement IDs, explicit Must Not / Non-goal boundaries, constraints,
   assumptions, and open questions, then runs the Requirement Fidelity Gate.
2. Identifies the desired outcome and the minimum implementation foundations.
3. Splits complex or multi-behavior requirements into focused, independently
   verifiable behavior Tickets.
4. Splits each Ticket into dependency-ordered Slices that the main agent can
   execute sequentially or delegate when they are independent, bounded, and
   have disjoint ownership.
5. Defines scope boundaries, Requirement coverage, acceptance criteria,
   relevant context, test strategy, bounded test level, test cases, and
   validation for each Slice.
6. Persists one Plan Issue and one Issue per Ticket before the Plan branch
   starts when the persistence trigger applies, reusing stable markers to avoid
   duplicates.
7. Assigns or resumes one implementation branch and base branch for the Plan;
   every Ticket and Slice on that Plan shares the branch.
8. Returns the `Plan` and `Tickets` sections defined by the skill contract,
   including canonical Issue links, nested Slices, and current execution
   metadata.

The skill is intentionally implementation-neutral. It uses repository context
and requires the available GitHub Issues connector for persisted planning, but it
does not implement code, add dependencies, force parallel implementation, or
invent commands for unknown tooling. The parent workflow decides whether any
Slice is delegated. For a persisted plan, a required GitHub read/write failure
blocks completion; the skill does not fall back to local Markdown or chat-only
storage.

## Naming contract

The skill uses stable, distinct names for every planning record:

| Record | Identifier | GitHub Issue or output title |
| --- | --- | --- |
| Plan | lowercase kebab-case `codex-plan-id` slug | `[PLAN] <short plan title>` |
| Ticket | repository-scoped `T` plus four digits, such as `T0016` | `[T0016] <short behavior/capability title>` |
| Slice | parent Ticket digits plus a one-based ordinal, such as `S0016.1` | Nested Slice heading `S0016.1 - <slice title>` |
| Branch | lowercase Plan ID plus a short description | `<type>/<plan-id>-<short-description>` |

New Ticket IDs are selected by scanning both open and closed Issue bodies and
must be greater than every existing valid ID; IDs are never reused. Duplicate
IDs in closed historical Issues are legacy records and are not renumbered.
When a matching Issue is reused, its title is normalized without changing its
stable marker or identifier. A persisted one-Ticket requirement still has a Plan
Issue and a child Ticket Issue, both using their canonical titles.

## Ticket-to-Slice hierarchy

Plan decomposition comes before Ticket decomposition, and Ticket decomposition
comes before Slice decomposition. A Plan is the requirement delivery boundary
represented by one GitHub Issue, one branch, one PR, and one merge. A Ticket is
the behavior/capability boundary represented by one child Issue and no
independent delivery branch. A Slice is a smaller execution-ready unit inside
that Ticket and inherits the Plan branch. Keep Ticket dependencies at the
execution-order level within the Plan and Slice dependencies inside the Ticket.
A persisted requirement is recorded as one Plan plus at least one Ticket; tiny
work is one Plan containing one Ticket with one implicit Slice. Requirement IDs
are the stable semantic link from the original request to Ticket/Slice
acceptance criteria and later verification evidence. An uncovered Requirement
or behavior-changing Plan item with no Requirement or verified repository
constraint blocks the Plan.

## Usage

Make the skill available in a Codex skills environment, then provide a change
request or implementation idea in a repository with a resolvable GitHub
remote. The frontmatter description in `SKILL.md` is used for skill selection.
When the persistence trigger applies, the skill creates or updates one Plan
Issue and its Ticket Issues before returning a successful Plan with
execution-ready Tickets and nested Slices. If the connector or required
permission is unavailable, the persisted result is blocked rather than replaced
by an unpersisted plan.

For repository-aware planning, include the relevant repository in the working
context. The skill will reuse existing architecture and conventions where they
are documented and available.

Every Plan output includes the branch handoff:

**Branch**

- <type>/plan-slug-short-description

**Base branch**

- main

Plan planning is complete before implementation begins. The parent workflow
then runs the Test -> applicable Redaction -> Commit -> Push -> Create / Update
Plan PR -> Merge lifecycle once for the Plan, while its Tickets
and Slices share that delivery boundary.

## Repository layout

```text
.
├── skills/plan-to-ticket/
│   ├── SKILL.md                          # Managed skill behavior and contract
│   └── agents/openai.yaml                 # Skill interface metadata
└── docs/skills/plan-to-ticket/
    ├── README.md                         # This documentation index
    ├── architecture.md                   # Logical architecture and boundaries
    └── diagrams/
        ├── plan-to-ticket-architecture.puml
        └── plan-to-ticket-architecture.svg
```

## Documentation

- [Architecture overview](architecture.md)
- [Architecture diagram source](diagrams/plan-to-ticket-architecture.puml)
- [Rendered architecture diagram](diagrams/plan-to-ticket-architecture.svg)

## Maintenance

Keep changes scoped to the skill's planning behavior or its supporting
documentation. When the persistence or output contract changes, update
`skills/plan-to-ticket/SKILL.md` and this documentation together. Keep
`agents/openai.yaml` limited to interface metadata rather than behavior.
