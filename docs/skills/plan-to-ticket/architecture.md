# Plan-to-Ticket Architecture

> Type: Architecture
> Status: Active
> Scope: GitHub Issue persistence boundary for model-decided Plan/Ticket records

## Scope

The model is the planning engine. `plan-to-ticket` receives an already-decided
Plan/Ticket structure and persists it into authoritative GitHub Issues.

There is no custom planning engine, local task database, decomposition algorithm,
test-planning layer, or delegation layer in this Skill.

## Logical architecture

![Plan-to-Ticket persistence architecture](diagrams/plan-to-ticket-architecture.svg)

Source: [plan-to-ticket-architecture.puml](diagrams/plan-to-ticket-architecture.puml).

## Responsibilities

| Asset | Responsibility | Boundary |
| --- | --- | --- |
| Model | Decide requirement structure, decomposition, dependencies, acceptance, sequencing, verification, and delegation | Native capability; not duplicated in the Skill |
| [`skills/plan-to-ticket/SKILL.md`](../../../skills/plan-to-ticket/SKILL.md) | Persist identifiers, Issue metadata, lifecycle, delivery ownership, deduplication, and failure semantics | Does not plan or decompose |
| GitHub Issues | Authoritative durable task store | No local Markdown mirror |
| `agents/openai.yaml` | UI metadata | No behavior |

## Persistence flow

1. The model decides whether durable multi-Issue persistence is useful.
2. The model provides the Plan/Ticket structure it already chose.
3. The Skill resolves stable markers and repository-scoped Ticket IDs.
4. The Skill creates or updates the Plan Issue and child Ticket Issues.
5. The Skill records branch/base/PR ownership and lifecycle status.
6. The Skill returns canonical Issue links and current delivery metadata.

## Invariants

- GitHub Issues are the sole task authority.
- A persisted Plan owns one branch, one PR, and one merge.
- Ticket IDs are stable and never reused.
- Duplicate stable markers are resolved before creating new records.
- A failed required write blocks persistence; there is no chat/local fallback.
- Planning and decomposition stay outside this Skill.
