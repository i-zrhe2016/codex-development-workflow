# GitHub Plan Persistence

Load this file only when a Plan must persist across sessions or the user explicitly requests GitHub Issue persistence.

## Durable model

Use one Plan Issue plus one child Issue per Ticket. GitHub Issues are the authoritative Plan/Ticket store; chat is only a convenience copy.

A persisted Plan still owns exactly one branch, one PR, and one merge. All Tickets and Slices run on that branch.

Allowed status values: `planned`, `in_progress`, `blocked`, `in_review`, `done`. Only `done` is closed, and only after the Plan PR is verified merged.

## Stable identity

Plan marker:

```text
<!-- codex-plan-id: <lowercase-kebab-plan-id> -->
```

Plan title:

```text
[PLAN] <short title>
```

Ticket marker:

```text
<!-- codex-ticket-id: T0016 -->
```

Ticket title:

```text
[T0016] <short behavior title>
```

Allocate Ticket IDs repository-wide by scanning open and closed Issue bodies for valid markers and choosing a value greater than every existing ID. Never reuse an ID. Slice IDs are `S<ticket-digits>.<ordinal>`, for example `S0016.1`.

Before creating an Issue, search its exact stable marker. Reuse/update one match. If multiple matches remain ambiguous, stop rather than guessing.

## Delivery metadata

Plan body starts with:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: <default-or-explicit-base>
PR: null
Tickets: [T0001]
```

Ticket body starts with:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

The Plan owns overall goal, milestones, branch/base/PR, Ticket index, dependency order, and the one-merge rule. Each Ticket owns its behavior boundary, dependencies, acceptance criteria, and nested Slice definitions. Do not duplicate mutable Ticket details in the Plan.

## Create/update order

1. Resolve repository and base branch.
2. Build the Plan/Tickets/Slices in memory.
3. Resolve stable markers and Ticket ID collisions.
4. Create/update the Plan Issue.
5. Create/update Ticket Issues sequentially and link them to the Plan/dependencies.
6. Verify the Plan Ticket index links every child Issue.
7. Only then allow Plan branch work.

If a write fails, report successful Issue URLs and the failed operation; mark affected work `blocked` when possible. Do not claim persistence succeeded and do not create a local fallback backlog.

## Lifecycle

- Branch work starts -> Plan `in_progress`.
- Blocking dependency/environment problem -> affected Plan/Ticket `blocked`.
- Plan PR opens -> Plan `in_review`, set canonical `PR`; Tickets may also enter `in_review`.
- PR merges -> Plan and all Tickets `done`, then close them.

Keep Plan `Branch`, `Base`, `PR`, and Ticket index current. PR head/base must match Plan metadata.

Ticket dependencies control execution order on the shared Plan branch; a dependency does not require an intermediate merge. Do not start a dependency-blocked Ticket until its prerequisite behavior is complete and validated.
