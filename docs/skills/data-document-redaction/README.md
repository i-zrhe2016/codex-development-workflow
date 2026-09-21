# Git Commit Redaction

`data-document-redaction` is the pre-publication gate for sensitive values in
the files staged for the next Git commit. It catches credentials, tokens,
private keys, personal identifiers, and similar values before they reach
GitHub.

The runtime instructions live in
[`SKILL.md`](../../../skills/data-document-redaction/SKILL.md).

## Gate

Stage the intended files, then run the bundled scanner before creating the
commit:

```bash
python3 skills/data-document-redaction/scripts/scan_staged.py
```

Interpret the result:

| Result | Action |
|---|---|
| `pass` | Continue to the commit. |
| `findings` | Stop publication; sanitize only the reported files and lines, stage the fixes, and re-scan. |
| `needs_review` | Stop publication; a staged file could not be safely inspected, such as a binary, oversized, or non-UTF-8 file. |
| `noop` | No staged files; no redaction action is required. |
| `error` | Stop; the scanner could not run, for example outside a Git repository or when the staged diff cannot be read. Fix the cause and re-run. |

The scanner exits `0` for `pass`/`noop`, `1` for `findings`, `2` for
`needs_review`, and `3` for `error`.

In the unified PR lifecycle, run this scan before the initial commit and repeat
it after any corrective change that alters the staged content, before the next
commit. When the staged change carries no sensitive surface, record the
inspected scope and the skip reason. The gate does not create a direct-push
exception for any change type.

## What it protects

- Credentials: passwords, API keys, access tokens, bearer tokens, JWTs, private
  keys, and credentials embedded in URLs or configuration assignments.
- Personal or sensitive values in staged files: real email addresses, phone
  numbers, national IDs, SSN-like identifiers, and payment-card-like numbers.
- Infrastructure addresses that repository policy treats as sensitive.

The scanner intentionally ignores common documentation placeholders such as
`example.com`, RFC documentation IP ranges, `127.0.0.1`, `0.0.0.0`, and obvious
redacted or dummy secret values.

## Boundaries

- It scans the staged files of the next commit only, not the whole repository
  and not Git history.
- It is not a PDF, Office, OCR, or general document-anonymization tool, and it
  is not a repository-wide privacy audit. Non-Git export or sharing boundaries
  need project-specific sanitization and review.
- A `pass` result protects the next commit; it is not proof that the repository
  or its history contains no secrets. If a secret was already committed or
  pushed, treat it as credential exposure: revoke or rotate it first, then
  handle history separately.
- Never print matched values. Report finding types, file paths, and line
  numbers only.

## Repository layout

```text
skills/data-document-redaction/
├── SKILL.md              # Runtime instructions and gate contract
├── agents/openai.yaml    # Skill interface metadata
└── scripts/
    └── scan_staged.py    # Staged-file scanner
```

## Maintenance

Keep this document aligned with `skills/data-document-redaction/SKILL.md`.
Update it when the gate outcomes, scan scope, or bundled scripts change.
