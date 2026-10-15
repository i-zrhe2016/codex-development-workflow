# Plan-to-Ticket Architecture

> Type: Architecture
> Status: Active
> Scope: Planning components and persistence authority boundaries

![Plan-to-Ticket architecture](diagrams/plan-to-ticket-architecture.svg)

[Diagram source](diagrams/plan-to-ticket-architecture.puml)

| Component | Responsibility | Boundary |
| --- | --- | --- |
| Skill instructions | Requirement boundaries, complete Ticket contracts and persistence rules | No product implementation or publication authority |
| Interface metadata | Explicit invocation and display text | No duplicate procedural authority |
| Versioned Plan Markdown | One new requirement, indexed Ticket sections and append-only evidence | All Tickets share one branch and optional PR/merge |
| Historical Issues | Original authority for existing requirements, including extensions; input to global ID scans | No migration, supersession or dual writes |
| Main coordinator | Serialized allocation/writes, scoped worker contracts and accepted checkpoints | Workers return evidence; they do not race record writes |
| Independent verification | Ticket and whole-Plan acceptance on fixed integrated snapshots | Read-only; main agent retains gate decisions |
| Repository state summary | Compact links to canonical Plan paths/anchors or legacy Issues | No copied backlog or Ticket history |

There is no application runtime, custom API client, global ledger or scheduler
service. Git provides versioned Plan records; the available GitHub connector
provides historical Issue scans, legacy operations and PR merge facts.

The [persistence contract](../../../skills/plan-to-ticket/SKILL.md#persistence-and-delivery-contract)
owns metadata, stable anchors, save/read-back ordering, retries and failure
blocking. Branch setup may precede the file; complete contracts precede all
other implementation edits. The [identifier contract](../../../skills/plan-to-ticket/SKILL.md#naming-and-idempotency)
combines historical Issue markers and visible branch Markdown; the
[publication recheck](../../../skills/plan-to-ticket/SKILL.md#publication-conflict-recheck)
handles concurrent allocation collisions without changing historical identities.

[Legacy continuation](../../../skills/plan-to-ticket/SKILL.md#legacy-continuation)
retains existing record destinations. For Markdown,
[verified merge facts](../../../skills/plan-to-ticket/SKILL.md#effective-completion-from-verified-merge)
determine effective completion even with stale stored status or PR null. This
avoids a post-merge status-only write. Worker scheduling remains owned by the
[role/context policy](../../../AGENTS.md#multi-agent-delegation).
