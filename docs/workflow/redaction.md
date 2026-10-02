# Redaction Workflow

> Type: Guide
> Status: Active
> Scope: Staged sensitive-data gate before publication

The repository uses a deterministic scanner rather than a runtime Skill.

## Run

After staging the intended commit:

```bash
python3 scripts/redaction/scan_staged.py
```

Repeat after any corrective change that alters staged content.

## Outcomes

| Result | Required action |
|---|---|
| `pass` | Continue. |
| `findings` | Stop publication; sanitize, re-stage, and re-scan. |
| `needs_review` | Stop publication; resolve the uninspectable staged file. |
| `noop` | Nothing is staged. |
| `error` | Stop; fix the scanner/runtime problem and run again. |

The scanner exits `0` for `pass`/`noop`, `1` for `findings`, `2` for `needs_review`, and `3` for `error`.

Never report matched secret values. Report finding type, path, and line number only.

If a real secret was already committed or pushed, revoke or rotate it first, then handle history separately.

## Boundary

The scanner protects the next staged Git commit. It is not a repository-history audit and does not replace broader privacy review for non-Git exports, PDFs, Office documents, OCR, or image metadata.
