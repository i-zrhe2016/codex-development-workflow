# Plan to Ticket

`plan-to-ticket` is the planning specialist for the main-agent workflow. It
turns a feature idea, requirement, bug-fix plan, refactor plan, or other
project change into one feature Plan, behavior Tickets, and dependency-ordered
Slices within each Ticket, then persists the Plan and Tickets to GitHub Issues.

The executable skill source is maintained at
[`skills/plan-to-ticket/`](../../../skills/plan-to-ticket/). This document and
its diagrams are the migrated documentation for that local bundle; they do not
describe an application runtime or a custom API/database service. GitHub Issues
are the external durable store used by the planning workflow.

## Architecture

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The diagram source is available at
[diagrams/plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
The full explanation is in [architecture.md](architecture.md).

## What it does

When the skill is selected for a planning request, it:

1. Identifies the desired outcome and the minimum implementation foundations.
2. Splits complex or multi-behavior requirements into focused, independently
   reviewable behavior Tickets.
3. Splits each Ticket into dependency-ordered Slices that the main agent can
   execute sequentially or pass through the optional delegation gate.
4. Defines scope boundaries, acceptance criteria, relevant context, test
   strategy, bounded test level, test cases, and validation for each Slice.
5. Creates or updates one Plan Issue and one Issue per Ticket before the Plan
   branch starts, reusing stable markers to avoid duplicates.
6. Assigns or resumes one implementation branch and base branch for the Plan;
   every Ticket and Slice on that Plan shares the branch.
7. Returns the `Plan` and `Tickets` sections defined by the skill contract,
   including canonical Issue links, nested Slices, and current execution
   metadata.

The skill is intentionally implementation-neutral. It uses repository context
and requires the available GitHub Issues connector for persistence, but it does
not implement code, add dependencies, force parallel implementation, or invent
commands for unknown tooling. The parent workflow decides whether any Slice is
delegated. A required GitHub read/write failure blocks completion; the skill
does not fall back to local Markdown or chat-only storage.

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
stable marker or identifier. A one-Ticket feature still has a Plan Issue and a
child Ticket Issue, both using their canonical titles.

## Ticket-to-Slice hierarchy

Plan decomposition comes before Ticket decomposition, and Ticket decomposition
comes before Slice decomposition. A Plan is the feature and delivery boundary
represented by one GitHub Issue, one branch, one PR, and one merge. A Ticket is
the behavior/capability boundary represented by one child Issue and no
independent delivery branch. A Slice is a smaller execution-ready unit inside
that Ticket and inherits the Plan branch. Keep Ticket dependencies at the
execution-order level within the Plan and Slice dependencies inside the Ticket.
Every feature is recorded as a Plan plus at least one Ticket; tiny work is one
Plan containing one Ticket with one implicit Slice.

## Usage

Make the skill available in a Codex skills environment, then provide a change
request or implementation idea in a repository with a resolvable GitHub
remote. The frontmatter description in `SKILL.md` is used for skill selection.
The skill creates/updates one Plan Issue and its Ticket Issues before returning
a successful Plan with execution-ready Tickets and nested Slices. If the connector or required permission is
unavailable, the result is blocked rather than an unpersisted plan.

For repository-aware planning, include the relevant repository in the working
context. The skill will reuse existing architecture and conventions where they
are documented and available.

Every Plan output includes the branch handoff:

**Branch**

- feature/plan-slug-short-description

**Base branch**

- main

Plan planning is complete before implementation begins. The parent workflow
then runs the Test -> applicable Redaction -> Commit -> Push -> Create / Update
Plan PR -> `pr-review` -> Merge lifecycle once for the Plan, while its Tickets
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
