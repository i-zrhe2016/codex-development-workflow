---
name: plan-workflow
description: "Plan, design, investigate or decompose a requirement into one persisted Plan and its executable Tickets before changes. Owns architecture, scope and persistence decisions; never edits repository files, verifies delivery or publishes."
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
3. Invoke `plan-to-ticket` to define the requirement-level Plan, its Ticket
   boundaries/dependencies, acceptance criteria and planned verification; do not
   execute checks. One ordinary requirement has one Ticket. A complex
   requirement may have multiple Tickets only for distinct behavioral,
   dependency, or acceptance boundaries.
4. Persist every requirement as a Plan Issue and all required child Ticket
   Issues before branch edits, regardless of size or session length. Follow the
   capability's titles, markers, ID allocation and branch contract. Supplementary
   work for an unmerged requirement updates the existing Ticket, or adds a
   behavior Ticket when a distinct boundary justifies it; update affected Plan
   and Ticket contracts before edits. An independent new requirement always
   starts a new Plan, even while another is unmerged. New scope grants no
   publication authority.

Complete only when the Plan and Tickets are persisted, and every Ticket has
scope/exclusions, dependencies, acceptance, test strategy/level and validation
command. Return the plan and stop; later implementation uses `develop-workflow`.

No product/test/config/docs edits, acceptance verification (`verify-workflow`),
publication/integration, Issue closure, PR-bound state refresh or evaluation.
