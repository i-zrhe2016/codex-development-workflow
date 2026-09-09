# Plan to Ticket

`plan-to-ticket` is the planning specialist for the main-agent workflow. It
turns a feature idea, requirement, bug-fix plan, refactor plan, or other
project change into a concise implementation plan, behavior Tickets, and
dependency-ordered Slices within each Ticket, then persists the plan and
Tickets to GitHub Issues.

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
5. Creates or updates one parent plan Issue and one Issue per Ticket before
   implementation branches start, reusing stable markers to avoid duplicates.
6. Assigns or resumes one implementation branch and base branch for each
   Ticket, using the updated default branch for new dependency-ready Tickets;
   each Ticket Issue and branch remain a one-to-one pair.
7. Returns the `Plan` and `Tickets` sections defined by the skill contract,
   including canonical Issue links, nested Slices, and current execution
   metadata.

The skill is intentionally implementation-neutral. It uses repository context
and requires the available GitHub Issues connector for persistence, but it does
not implement code, add dependencies, force parallel implementation, or invent
commands for unknown tooling. The parent workflow decides whether any Slice is
delegated. A required GitHub read/write failure blocks completion; the skill
does not fall back to local Markdown or chat-only storage.

## Ticket-to-Slice hierarchy

Ticket decomposition comes before Slice decomposition. A Ticket is the
behavior/capability boundary represented by one GitHub Issue and one branch. A
Slice is a smaller execution-ready unit inside that Ticket and inherits the
Ticket's Issue and branch. Keep Ticket dependencies at the branch-readiness
level and Slice dependencies inside the Ticket. Tiny work may remain one
implicit Slice without creating a Ticket.

## Usage

Make the skill available in a Codex skills environment, then provide a change
request or implementation idea in a repository with a resolvable GitHub
remote. The frontmatter description in `SKILL.md` is used for skill selection.
The skill creates/updates the parent plan Issue and Ticket Issues before
returning a successful plan with execution-ready Tickets and nested Slices. If
the connector or required permission is unavailable, the result is blocked
rather than an unpersisted plan.

For repository-aware planning, include the relevant repository in the working
context. The skill will reuse existing architecture and conventions where they
are documented and available.

Every ticket output includes the branch handoff:

**Branch**

- feature/t0001-short-description

**Base branch**

- main

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
