---
name: github-issue-persistence
description: "Persist repository-specific development task hierarchy and lifecycle metadata in GitHub Issues. Use only when the authoritative Issue needs durable Plan/Ticket records, stable repository IDs, dependency links, branch/PR metadata, or lifecycle reconciliation. Codex performs the planning itself; this Skill does not teach planning, ticket sizing, acceptance criteria, testing, sequencing, or delegation."
---

# GitHub Issue Persistence

This Skill defines only the repository's durable GitHub Issue schema and write rules.

Codex decides the plan natively. Persist only the structure that must survive sessions or be shared through GitHub Issues.

## Authority

GitHub Issues are the sole authoritative development-task store.

A simple task may remain one Issue. When a durable hierarchy is useful, persist one Plan Issue plus the smallest useful set of child Ticket Issues. Do not create a parallel backlog in chat, local Markdown, PR bodies, or model memory.

## Idempotency

Before creating a Plan or Ticket, search open and closed Issues for its exact marker. Reuse one exact match. If multiple records match the same stable marker, stop rather than guessing.

Stable markers:

```text
<!-- codex-plan-id: <stable-kebab-slug> -->
<!-- codex-ticket-id: T0016 -->
```

Ticket IDs are repository-scoped: `T` plus four zero-padded digits. Allocate a value greater than every existing valid `codex-ticket-id`; never reuse an ID.

## Plan record

A persisted Plan Issue title is:

```text
[PLAN] <short title>
```

Its body starts with:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: <base-branch>
PR: null
Tickets: [T0001]
```

The Plan owns one implementation branch, one pull request, and one merge. Child Tickets do not get independent delivery branches.

The Plan body owns only overall goal/milestones, delivery metadata, Ticket index, and dependency order. Mutable Ticket detail belongs to child Issues.

## Ticket record

A Ticket Issue title is:

```text
[T0001] <short behavior title>
```

Its body starts with:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

Store the Codex-produced task details needed for durable handoff, such as scope, acceptance boundary, dependencies, and relevant implementation notes. This Skill does not prescribe how Codex derives those details.

## Lifecycle

Allowed status values:

- `planned`
- `in_progress`
- `blocked`
- `in_review`
- `done`

Keep Plan `Branch`, `Base`, `PR`, Ticket index, dependencies, and statuses synchronized with repository reality.

Typical durable transitions:

- branch work begins -> Plan `in_progress`;
- blocking condition -> affected record `blocked`;
- PR opens -> Plan `in_review` and set `PR`;
- merged PR -> Plan and completed child Tickets `done`, then close them.

Do not mark a Plan or Ticket done merely because a branch or PR exists.

## Write failure

Persistence is complete only when all required GitHub writes succeed. If a write partially fails, report the records already created, mark the affected record blocked when possible, and do not create a local mirror as a fallback.
