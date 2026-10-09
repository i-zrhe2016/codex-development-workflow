---
name: integrate-workflow
description: "Merge a ready PR, clean up its branch, synchronize default branch, close Plan/Tickets and validate state/docs included with the PR. Never writes product code."
---

# Integrate Workflow

Owns **authorized ready PR -> delivered and reconciled**. Subsequent functionality
after verified merge uses a new Plan; never append to the delivered Plan.

When the user controls the overall flow, integration may state readiness,
remaining gates, risks and merge/cleanup consequences, but must not choose merge
timing, cleanup timing, follow-up scope or post-merge work for the user.

1. Confirm merge authorization covers the current batch (an explicit full
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
4. After verified merge, set Plan/child Tickets `done` and close them.

No product/test/config edits: discovered defects return to `develop-workflow` as
new changes. If more work is needed before merge, resume the branch; do not
produce a second merge. Do not create post-merge state-only PRs for facts that
belong to the delivered work, and never commit state/docs directly to the
default branch. Post-delivery evaluation belongs to the entry-point skill.
