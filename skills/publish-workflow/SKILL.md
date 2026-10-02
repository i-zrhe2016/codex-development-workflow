---
name: publish-workflow
description: "Decide WHEN to publish. Take a verified change through the documentation impact check, the staged redaction scan, and Conventional Commit, push, and pull-request readiness. Use when the request is to commit, push, open or update a pull request, or prepare a branch for review. It runs to PR ready and stops, and never merges."
---

# Publish Workflow

Stage workflow for the **verified change -> PR ready** transition.

## Responsibility

Compose the capability skills in this order, then stop:

1. `repo-documentation` — run its documentation impact check. Update the
   canonical owner document and the documentation index, or record that no
   documentation change is needed.
2. `data-document-redaction` — stage the intended change, run its staged scan,
   and follow the redaction workflow that skill owns. Continue on `pass`,
   `noop`, or a recorded no-sensitive-surface skip;
   sanitize only the reported files and re-scan on `findings`, `needs_review`,
   or `error`.
3. `github-push-when-ready` — make one focused Conventional Commit, push the
   branch, and create or update the pull request until it is ready to merge.

Report the branch, the commit, and the pull request, then stop.

## Boundaries

- The stage ends at **PR ready**. It never merges, never deletes a branch, and
  never closes an Issue; those belong to `integrate-workflow`.
- It does not write product code. A failing check returns to
  `develop-workflow` or `verify-workflow` instead of being patched here.
- One commit carries one purpose, and the message follows Conventional
  Commits.
- When the branch carries Plan metadata, `github-push-when-ready` validates it.
  When it does not, publication still proceeds: a persisted Plan is a planning
  decision, not a publication precondition.
- Branch, redaction, security, permission, and release gates are never weakened
  to reduce friction.
