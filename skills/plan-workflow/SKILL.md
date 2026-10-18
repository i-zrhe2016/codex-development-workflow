---
name: plan-workflow
description: "Plan, design, investigate or decompose a requirement into one persisted Plan and its executable Tickets before changes. Owns architecture, scope and persistence decisions; edits only the Plan record and never verifies delivery or publishes."
---

# Plan Workflow

## Execution mode

Default reasoning effort is `low`, including self-verification; planning
uses `high` in either mode. Delegated development/repair uses `low` and
independent verification `high`. Report unsupported effort settings; do not
claim that editing instructions changed the running turn's effort.

Default single-agent execution: the main agent performs this stage directly,
including required checks and acceptance; do not spawn subagents. Record
self-verification accurately, without claiming independent verification.
Worker-only dispatch, independent-verifier and no-main-agent-fallback rules
below apply only in explicitly authorized delegated mode. Stage transitions
and an initial failure do not activate delegation. After two consecutive failed
same-problem repair rounds, checkpoint and pause; ask the user to choose an
escalation model and whether to authorize delegation. Model selection alone
does not authorize subagents. Missing subagent support does not block default
single-agent execution. Keep the existing Test Quality Gate, durable evidence
and publication boundaries in both modes.

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
4. Persist every new requirement as one Plan Markdown record containing all required Ticket
   sections before implementation edits, regardless of size or session length. Follow the
   capability's titles, markers, ID allocation and branch contract. Supplementary
   work for an unmerged requirement updates the existing Ticket, or adds a
   behavior Ticket when a distinct boundary justifies it; update affected Plan
   and Ticket contracts before edits. An independent new requirement always
   starts a new Plan, even while another is unmerged. New scope grants no
   publication authority. Existing Issue requirements, including extensions,
   retain original authority under `plan-to-ticket`; no migration or dual writes.
   A branch may precede the Plan file, but read back the complete contract before
   any other implementation edits.

Complete only when the Plan and Tickets are persisted, and every Ticket has
scope/exclusions, dependencies, acceptance, test strategy/level and validation
command. Return the plan and stop; later implementation uses `develop-workflow`.

Only Plan Markdown persistence and its branch setup are allowed; no other
product/test/config/docs edits, acceptance verification (`verify-workflow`),
publication/integration, legacy Issue closure, PR-bound state refresh or evaluation.
