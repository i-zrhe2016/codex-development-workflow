# Plan to Ticket

`plan-to-ticket` is the planning specialist for the single-agent workflow. It
turns a feature idea, requirement, bug-fix plan, refactor plan, or other
project change into a concise implementation plan and small,
dependency-ordered Slices (tickets).

The executable skill source is maintained at
[`skills/plan-to-ticket/`](../../../skills/plan-to-ticket/). This document and
its diagrams are the migrated documentation for that local bundle; they do not
describe an application runtime, API, database, or deployment service.

## Architecture

![Plan-to-Ticket logical architecture](diagrams/plan-to-ticket-architecture.svg)

The diagram source is available at
[diagrams/plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).
The full explanation is in [architecture.md](architecture.md).

## What it does

When the skill is selected for a planning request, it:

1. Identifies the desired outcome and the minimum implementation foundations.
2. Splits the work into focused, dependency-ordered Slices executed one at a
   time by the single agent.
3. Defines scope boundaries, acceptance criteria, relevant context, test
   strategy, bounded test level, test cases, and validation for each Slice.
4. Returns text using the `Plan` and `Tickets` sections defined by the skill
   contract.

The skill is intentionally implementation-neutral. It uses repository context
when available, but it does not implement code, add dependencies, recommend
parallel implementation, or invent commands for unknown tooling.

## Usage

Make the skill available in a Codex skills environment, then provide a change
request or implementation idea. The frontmatter description in `SKILL.md` is
used for skill selection. The response should contain only a plan and
execution-ready Slices/tickets.

For repository-aware planning, include the relevant repository in the working
context. The skill will reuse existing architecture and conventions where they
are documented and available.

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
documentation. When the output contract changes, update
`skills/plan-to-ticket/SKILL.md` and this documentation together. Keep
`agents/openai.yaml` limited to interface metadata rather than behavior.
