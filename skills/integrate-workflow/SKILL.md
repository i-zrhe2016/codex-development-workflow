---
name: integrate-workflow
description: "Merge a ready PR, clean up its branch, synchronize default branch, verify effective Plan/Ticket completion from merged PR and validate state/docs included with the PR. Never writes product code."
---

# Integrate Workflow

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

Owns **authorized ready PR -> delivered and reconciled**. Subsequent functionality
after verified merge uses a new Plan; never append to the delivered Plan.

When the user controls the overall flow, integration may state readiness,
remaining gates, risks and merge/cleanup consequences, but must not choose merge
timing, cleanup timing, follow-up scope or post-merge work for the user.

1. Confirm merge authorization covers the current Plan requirement (an explicit full
   delivery may already include it); PR readiness alone grants no merge authority.
   Confirm required verification passed for the current scope, including the
   final Plan/branch/PR acceptance gate. It may coalesce with Ticket
   verification only for a one-Ticket Plan with exactly matching scope,
   artifact/version, configuration and deployment surface. PR head/base must
   match
   delivery metadata. Expanded unmerged scope must be revalidated and published
   to the same PR before merge; stale readiness is insufficient.
2. Confirm required `docs/Repo_Current_State.md` and documentation updates are
   already included in the PR when verified state/docs changed; missing required
   updates return to `publish-workflow` on the Plan branch before merge.
3. Merge once under repository policy; delete source branch, update default.
4. Follow the [effective completion rule](../plan-to-ticket/SKILL.md#effective-completion-from-verified-merge).
   Resolve or discover the PR when PR is null; verify repository, recorded
   branch/base, merged state/commit and every Ticket's full accepted scope.
   Missing or ambiguous proof blocks a done claim. Derive effective Markdown
   Plan/Ticket `done` from this verified merge without a status-only write.
   For legacy requirements only, update/close original Issues after verified merge.

No product/test/config edits: discovered defects return to `develop-workflow` as
new changes. If more work is needed before merge, resume the branch; do not
produce a second merge. Do not create post-merge state-only PRs for facts that
belong to the delivered work, and never commit state/docs directly to the
default branch. Post-delivery evaluation belongs to the entry-point skill.

## Legacy format compatibility

Existing Issue requirements, including extensions, retain their original authority.
Follow [legacy continuation](../plan-to-ticket/SKILL.md#legacy-continuation). Do not migrate or dual write.
New requirements use versioned Plan Markdown; all existing gates apply.
