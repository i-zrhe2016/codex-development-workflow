---
name: integrate-workflow
description: "Merge a ready PR, clean up its branch, synchronize default branch, close Plan/Tickets and reconcile state/docs. Never writes product code."
---

# Integrate Workflow

Owns **PR ready -> delivered and reconciled**.

1. Confirm required verification passed and PR head/base match delivery metadata.
2. Merge once under repository policy; delete source branch, update default.
3. After verified merge, set Plan/child Tickets `done` and close them.
4. Invoke `repo-current-state` if verified state changed, and `repo-documentation`
   to reconcile the index with merged changes.

No product/test/config edits: discovered defects return to `develop-workflow` as
new changes. If more work is needed before merge, resume the branch; do not
produce a second merge. Tracked post-merge state/docs edits require their own
branch/PR/merge gates, never direct default-branch commits. Post-delivery
evaluation belongs to the entry-point skill.
