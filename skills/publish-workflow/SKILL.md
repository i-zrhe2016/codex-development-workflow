---
name: publish-workflow
description: "Publish a verified repository change to PR ready. Use when asked to commit, push, sync, or create/update a pull request. Run documentation impact, staged redaction, and guarded GitHub publication in order, then stop before merge."
---

# Publish Workflow

Take a verified change to **PR ready**:

1. `repo-documentation`: run the documentation impact check; update the canonical owner/index only when needed.
2. `data-document-redaction`: stage the intended change and pass the staged-data gate.
3. `github-push-when-ready`: create the coherent Conventional Commit, push the non-default branch, and create/update the PR.

Return branch, commit, and canonical PR, then stop.

Do not write product code here. A failing verification returns to `develop-workflow`/`verify-workflow`. Never weaken branch, redaction, identity, permission, or security gates. Merge/cleanup/Issue closure belong to `integrate-workflow`.
