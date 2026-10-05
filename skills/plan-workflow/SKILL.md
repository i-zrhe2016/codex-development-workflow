---
name: plan-workflow
description: "Plan, design, investigate or decompose a requirement into executable Tickets/Slices before changes. Owns architecture, scope and persistence decisions; never edits repository files, verifies delivery or publishes."
---

# Plan Workflow

Owns **requirement -> executable work definition**; `plan-to-ticket` owns the
decomposition and persistence procedure.

When the user controls the overall flow, planning may present the main workflow,
trade-offs, risks and recommended next decisions, but must not choose scope,
persistence, stage transitions, publication timing or delivery boundaries for
the user. Record explicit user decisions; otherwise return options and stop.

1. Read `docs/Repo_Current_State.md`, affected code and applicable `AGENTS.md`;
   verify relevant claims, boundaries, interfaces and existing constraints.
2. Choose the simplest sufficient design; record rejected alternatives only
   when they explain a real decision.
3. Invoke `plan-to-ticket` for behavior Tickets, dependency-ordered Slices,
   acceptance criteria and planned verification breadth; do not execute checks.
4. Persist Plan and child Issues when complex, cross-module, dependent,
   multi-session/resumable by another agent, or explicitly requested. Keep small
   single-session plans inline. Follow the capability's exact titles, markers,
   ID allocation and branch contract. For newly requested functionality in an
   unmerged Plan, use its scope-update contract before edits: append a Ticket,
   update goal/scope/index/dependencies/validation, preserve branch/base/PR and
   evidence, and invalidate impacted readiness. After merge, use a new Plan.
   Planning new scope grants no publication authority.

Complete only when the persistence decision is recorded and every Slice has
scope/exclusions, dependencies, acceptance, test strategy/level and validation
command. Return the plan and stop; later implementation uses `develop-workflow`.

No product/test/config/docs edits, acceptance verification (`verify-workflow`),
publication/integration, Issue closure, PR-bound state refresh or evaluation.
