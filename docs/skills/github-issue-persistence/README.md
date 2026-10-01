# GitHub Issue Persistence

> Type: Reference
> Status: Active
> Scope: Repository-specific durable task records in GitHub Issues

Codex performs planning, decomposition, acceptance reasoning, sequencing, and delegation natively.

The runtime Skill at `skills/github-issue-persistence/` exists only to persist repository-specific data that must survive sessions:

- GitHub Issues as the sole task authority;
- stable Plan/Ticket markers and repository-scoped Ticket IDs;
- Plan/Ticket metadata shape;
- one Plan -> one branch -> one PR -> one merge;
- durable lifecycle reconciliation.

Do not use this Skill as a planning methodology.

Repository overview diagram:

- Render: [plan-ticket-slice.svg](../../diagrams/drawio/plan-ticket-slice.svg)
- Editable source: [plan-ticket-slice.drawio](../../diagrams/drawio/plan-ticket-slice.drawio)

The diagram documents the persisted Issue hierarchy only; it is not a Codex planning workflow.
