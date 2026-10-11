# Staged Document Redaction

`data-document-redaction` scans the exact files staged for the next Git commit. It checks for credentials, private keys, personal identifiers, and other sensitive values before commit or publication. The runtime instructions and scanner are in [`skills/data-document-redaction/`](../../../skills/data-document-redaction/).

Run the scanner from a Git checkout:

```bash
python3 skills/data-document-redaction/scripts/scan_staged.py
```

| Result | Action |
|---|---|
| `pass` or `noop` | Continue; `noop` means no files are staged. |
| `findings` | Inspect only reported paths and lines, sanitize, stage fixes, and scan again. |
| `needs_review` | Stop because a staged file cannot be safely inspected. |
| `error` | Fix the scanner or Git access problem, then retry. |

Exit codes are `0` for `pass`/`noop`, `1` for findings, `2` for needs review, and `3` for errors. Never print matched values; report finding types, paths, and line numbers only.

The scanner does not inspect the whole repository or Git history and does not handle PDF, Office, OCR, image metadata, or general anonymization. A pass is limited to the staged content it inspected.
