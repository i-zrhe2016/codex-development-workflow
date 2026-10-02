---
name: integrate-workflow
description: "Decide WHEN to integrate. Take a ready pull request through merge, source-branch deletion, default-branch update, Plan and Ticket closure, repository-state refresh, and documentation reconciliation. Use when the request is to merge, clean up, or reconcile repository state after delivery. It does not write product code."
---

# Integrate Workflow

Stage workflow for the **PR ready -> delivered and reconciled** transition.

## Responsibility

1. Confirm the pull request's required verification has passed and that its
   head and base match the recorded delivery metadata.
2. Merge the pull request once, following the repository's merge policy.
3. Delete the source branch and update the default branch.
4. Close the Plan and its child Tickets, setting their status to `done`.
5. Invoke `repo-current-state` to refresh `docs/Repo_Current_State.md` when
   verified project state changed.
6. Invoke `repo-documentation` to reconcile the documentation index with the
   merged change.

## Boundaries

- It does not write product, test, or configuration code. A defect found here
  returns to `develop-workflow` as a new change instead of being fixed in
  place.
- It merges the pull request once. Work that needs more change resumes on its
  branch instead of producing a second merge.
- Post-merge state and documentation updates that change tracked content go
  through their own change with the same branch, pull request, and merge gates.
  Never commit them directly to the default branch.
- The post-delivery process evaluation belongs to the entry-point skill, not to
  this stage.
