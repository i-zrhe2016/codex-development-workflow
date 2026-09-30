---
name: integrate-workflow
description: "Integrate a ready pull request after publication. Use to merge, clean up the source branch, synchronize the default branch, close Plan/Ticket Issues, and reconcile repository state/docs. It does not write product code."
---

# Integrate Workflow

Take **PR ready** to delivered and reconciled.

1. Confirm required verification passed and PR head/base match delivery metadata.
2. Merge once using repository policy.
3. Delete the source branch and synchronize the default branch.
4. If a persisted Plan exists, set Plan/Tickets to `done` and close them.
5. Invoke `repo-current-state` when verified project state changed.
6. Invoke `repo-documentation` to reconcile the documentation index/owners.

Do not fix product defects in this stage; return them to development as a new change. Any post-merge state/doc edit that changes tracked content must itself use a branch and PR, never a direct default-branch commit.
