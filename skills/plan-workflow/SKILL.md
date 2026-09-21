---
name: plan-workflow
description: "Decide WHEN to plan. Turn a requirement into an executable work definition: understand the affected repository area, settle architecture and scope, and decompose the work into Tickets and Slices. Use when the request is to plan, design, investigate, or decompose before any code changes. It does not edit code, run the delivery verification, or publish anything."
---

# Plan Workflow

Stage workflow for the **requirement -> executable work definition**
transition. It decides *when* planning happens and *how much* planning the
requirement warrants; the decomposition and persistence procedure itself
belongs to the `plan-to-ticket` capability.

## Responsibility

- Read `docs/Repo_Current_State.md` and the affected code before proposing
  anything; verify the claims the request depends on.
- Establish the affected boundary, the interfaces it touches, and the
  constraints that already exist, including `AGENTS.md` rules in scope.
- Choose the simplest design that satisfies the requirement. Record a rejected
  alternative only when it explains a real decision.
- Split the requirement into behavior Tickets and dependency-ordered Slices.
- Name the acceptance criteria and the verification breadth each Slice will
  need, without executing it.
- Decide whether the work needs a persisted Plan Issue.

## Persistence decision

Persist a Plan and its child Tickets as GitHub Issues when any of these hold:

- the work is complex, crosses modules, or has internal dependencies;
- the work must survive a session boundary or be resumed by another agent;
- the user explicitly asks for a persisted plan.

Small, single-session work keeps its plan inline and moves straight to
`develop-workflow`. Use `plan-to-ticket` for the decomposition and, when a
trigger above applies, for its persistence contract. Title format, markers,
Ticket ID allocation, and branch naming stay exactly as `plan-to-ticket`
defines them.

## Not responsible for

- editing product, test, configuration, or documentation files;
- running the acceptance verification — that is `verify-workflow`;
- committing, pushing, opening a pull request, or merging — those are
  `publish-workflow` and `integrate-workflow`;
- closing Issues, or refreshing `docs/Repo_Current_State.md`, which happens
  after integration;
- the post-delivery process evaluation.

## Completion

Planning is complete when every Slice a later stage will execute carries a
scope, an out-of-scope boundary, dependencies, acceptance criteria, a test
strategy and level, and a validation command, and when the persistence decision
above has been recorded. Return the plan and stop; do not start implementing.
