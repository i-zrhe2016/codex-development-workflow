# Redaction Workflow

> Type: Guide
> Status: Active
> Scope: The orchestration-level redaction gate: timing, procedure, outcomes, exit codes and boundaries

`data-document-redaction` owns detection/sanitization; this guide owns its
publication boundary. Inspect exact staged content for the next commit, not
worktree or repository. Repeat after any staged correction; never defer secret/personal-data
cleanup until after commit.

1. Stage intended files; run `python3 <skill-dir>/scripts/scan_staged.py`.
2. Interpret the result below. Blocking findings require minimal sanitization:
   load removed secrets from environment/secret storage/runtime config; use
   obvious examples or synthetic personal data preserving tested formats. Never
   partially mask a credential or invent a replacement secret.
3. Stage corrections and re-scan to `pass`.
4. Report types/paths/lines only, never values/mappings/credentials.

| Result | Exit | Action |
|---|---|---|
| `pass` | 0 | Continue to commit/publication gates |
| `noop` | 0 | Nothing staged; no redaction action |
| `findings` | 1 | Block; sanitize reported files/re-scan |
| `needs_review` | 2 | Block; resolve uninspectable staged file |
| `error` | 3 | Block; fix scanner cause (e.g. non-repo/unreadable diff), rerun |
| No sensitive surface | — | Record inspected scope and skip reason; continue |

Already committed/pushed secrets are credential exposure: stop, revoke/rotate
first, handle history separately if required. Git history is durable.

The packaged scan covers staged files only, not document/PDF/Office/OCR,
repository-wide anonymization or non-Git exports/sharing; those require
project-specific tooling/review. See the installed specialist's runtime contract.
