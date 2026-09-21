# Redaction Workflow

> Type: Guide
> Status: Active
> Scope: The orchestration-level redaction gate: when it runs, its procedure, gate outcomes, exit codes, and scope boundaries

This document defines the orchestration-level redaction gate for the
development workflow. The `data-document-redaction` specialist owns detection
and sanitization behavior; this page defines when the gate runs and how its
result affects publication.

## When the gate runs

Run the gate after the intended files are staged for the next commit and before
that commit is created. Repeat it after any corrective change that alters the
staged content, before the next commit. Git history is durable, so do not rely
on cleaning up a secret or personal value after it has been committed.

## Procedure

1. **Stage the intended change.** The gate inspects the exact staged content,
   not the working tree and not the whole repository.
2. **Run the scanner.** `python3 <skill-dir>/scripts/scan_staged.py`
3. **Interpret the result.** `pass` continues; `findings` and `needs_review`
   stop publication until the reported gap is resolved.
4. **Sanitize minimally.** Remove the value and load it from environment,
   secret storage, or runtime configuration; replace personal data with an
   obvious example or synthetic value that preserves the tested format. Never
   partially mask a real credential, and never invent a replacement secret.
5. **Re-scan.** Stage the corrections and rerun the scanner; continue only on
   `pass`.
6. **Report safely.** Report finding types, file paths, and line numbers only —
   never original values, mappings, or credentials.

## Gate outcomes

| Result | Required action |
|---|---|
| `pass` | Continue to the commit and the later publication gates. |
| `findings` | Stop publication; sanitize the reported files and re-scan. |
| `needs_review` | Stop publication; resolve the uninspectable staged file. |
| `noop` | Nothing is staged; no redaction action is required. |
| `error` | Stop; the scan could not run, for example outside a Git repository or when the staged diff cannot be read. Fix the cause and re-run. |
| No sensitive surface in the staged change | Record the inspected scope and the skip reason; continue. |

The scanner exits `0` for `pass`/`noop`, `1` for `findings`, `2` for
`needs_review`, and `3` for `error`.

If a secret was already committed or pushed, stop and treat it as credential
exposure: revoke or rotate it first, then handle history separately if
required.

## Scope boundaries

The packaged specialist covers the staged commit set only. It does not perform
document, PDF, Office, OCR, or repository-wide anonymization, and it does not
own non-Git export or sharing boundaries; those need project-specific tooling
and review. Its runtime contract lives in the `data-document-redaction` skill.
