---
name: plan-to-ticket
description: Persist a model-decided development plan into authoritative GitHub Issues using this repository's Plan/Ticket identifiers, metadata, lifecycle, branch/PR ownership, deduplication, and failure rules. Use only after native model reasoning has already decided that durable multi-Issue persistence is useful or the user explicitly requests Plan/Ticket persistence. Do not use this Skill to plan, decompose, size, sequence, test-design, or delegate work.
---

# Plan to Ticket

Treat this Skill as a GitHub Issues persistence adapter, not a planning engine.

The model owns requirement understanding, planning, decomposition, sequencing, acceptance criteria, verification strategy, and delegation decisions through its native capabilities. This Skill must not replace or restate those capabilities.

## Input contract

Invoke only when the model already has the structure it wants to persist.

The input may contain:
- one overall requirement / Plan boundary;
- zero or more model-decided child Ticket boundaries;
- dependencies already decided by the model;
- acceptance criteria and other task details already decided by the model.

If durable multi-Issue persistence adds no value, keep the existing authoritative Issue and do not invoke this Skill.

## Repository persistence contract

GitHub Issues are the sole authoritative task store.

- Do not create parallel task authority in chat, PR bodies, local Markdown, TODO files, or model memory.
- If GitHub Issues are unavailable or unwritable, return a blocked result. Do not fall back to another store.
- Reuse existing matching records whenever their stable markers identify the same Plan or Ticket.
- Search both open and closed Issues for exact markers before creating a new record.
- If more than one Issue matches the same stable marker and the ambiguity cannot be resolved from the Plan association, stop rather than guessing.

## Stable identifiers

Use repository-specific stable identifiers:

- Plan marker: `<!-- codex-plan-id: <stable-kebab-slug> -->`
- Plan title: `[PLAN] <short plan title>`
- Ticket marker: `<!-- codex-ticket-id: T#### -->`
- Ticket title: `[T####] <short behavior/capability title>`
- Ticket IDs are repository-scoped, four-digit, monotonically increasing, and never reused.
- GitHub Issue numbers are link targets, not Plan or Ticket identifiers.

For a new Ticket ID, scan open and closed Issue bodies for valid `codex-ticket-id` markers and choose a value greater than every existing valid ID.

## Delivery ownership

A persisted Plan owns exactly:
- one implementation branch;
- one base branch;
- one pull request;
- one merge.

All child Tickets belong to that delivery boundary. Do not create Ticket-specific branches or merges.

Use a Plan branch in the form:

`<type>/<plan-id>-<short-description>`

The Plan Issue stores the canonical delivery metadata:

```yaml
Status: planned
Branch: <branch>
Base: <base>
PR: null
Tickets: [T0001, T0002]
```

Each Ticket Issue stores:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

The model decides the Ticket content. Persist that content without inventing additional planning structure.

## Status lifecycle

Allowed values:

- `planned`
- `in_progress`
- `blocked`
- `in_review`
- `done`

Keep `planned`, `in_progress`, `blocked`, and `in_review` Issues open.

Update records at these repository lifecycle boundaries:
- Plan branch starts -> Plan `in_progress`
- blocking problem -> affected Plan/Ticket `blocked`
- Plan PR opens -> Plan `in_review`, set `PR`
- Plan PR merges -> Plan and child Tickets `done`, then close them

Never mark the Plan or a Ticket `done` merely because a branch or PR exists.

## Write order

Persist deterministically:

1. Resolve repository and base branch.
2. Receive the model-decided Plan/Ticket structure.
3. Resolve stable markers and Ticket ID collisions.
4. Create or update the Plan Issue.
5. Create or update child Ticket Issues sequentially.
6. Update the Plan Ticket index with canonical child Issue links/IDs.
7. Verify Branch/Base/PR metadata is internally consistent.
8. Return canonical Issue links and current metadata.

Do not start implementation on the Plan branch until required Issue writes succeed.

## Failure semantics

If a required write fails:
- report the failed operation;
- include any canonical Issue URLs already created;
- mark the affected record `blocked` when that write is still possible;
- do not claim persistence succeeded;
- do not create a local mirror.

## Output

Return only the durable handoff:

```text
Plan: <Plan Issue URL>
Branch: <branch>
Base: <base>
PR: <URL | null>
Tickets:
- T0001 <Ticket Issue URL>
- T0002 <Ticket Issue URL>
```

Do not append a new plan, decomposition rationale, implementation instructions, test strategy, or delegation guidance. Those remain native model work.
