---
name: plan-workflow
description: "Plan or design repository work before editing. Use to understand affected architecture/scope, choose the simplest viable design, and produce executable Tickets/Slices. Decide whether the plan needs GitHub Issue persistence, then stop before implementation."
---

# Plan Workflow

Take a requirement to an executable work definition.

1. Read `docs/Repo_Current_State.md` when present plus only the affected code/contracts and applicable `AGENTS.md`.
2. Verify assumptions the request depends on.
3. Establish affected boundaries, interfaces, constraints, and the simplest design that satisfies the requirement.
4. Invoke `plan-to-ticket` for Ticket/Slice decomposition.
5. Persist through `plan-to-ticket` only when work is complex, must survive a session boundary, or the user explicitly requests persistence.
6. Return the plan and stop.

Planning is complete when each Slice has scope/out-of-scope, dependencies, observable acceptance criteria, test strategy/level, and validation guidance. Do not edit code, run delivery verification, publish, merge, close Issues, or refresh post-merge repository state.
