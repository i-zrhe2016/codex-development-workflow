---
name: publish-workflow
description: "Commit, push, open/update a PR or prepare review of a verified change through documentation impact, staged redaction and Conventional Commit readiness. Stops at PR ready; never merges."
---

# Publish Workflow

Owns **verified change -> PR ready**. A change may be one functionality or an
explicitly planned multi-function batch. Before publication, every Ticket's
acceptance and the batch's relevant integration/regression checks must pass;
any failure blocks the batch. Invoke these capabilities in order:

1. `repo-documentation`: impact check; update canonical docs/index or record no
   documentation change.
2. `data-document-redaction`: stage only the batch's verified functionality,
   tests and documentation, preserving out-of-Plan user changes; prefer explicit
   pathspecs/hunks under `github-push-when-ready`. Scan staged files. Proceed only on
   `pass`, `noop` or recorded no-sensitive-surface skip. `findings`/`needs_review`
   block: sanitize reported files, re-stage/re-scan; fix scanner `error` first.
3. `github-push-when-ready`: Conventional Commit for one functionality or the
   planned batch, push branch, create/update PR until ready. Follow its batch
   commit/PR description rules. Validate any Plan metadata; a persisted Plan is
   a planning decision, not a publication precondition.

Report branch, commit and PR, then stop. No merge, branch deletion or Issue
closure (`integrate-workflow`); no product edits. Failed checks return to
`develop-workflow`/`verify-workflow`. Never weaken branch, redaction, security,
permission or release gates.
