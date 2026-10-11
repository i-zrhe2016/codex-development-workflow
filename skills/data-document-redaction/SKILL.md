---
name: data-document-redaction
description: "Before commit, push, or PR publication, scan/sanitize staged files that may contain secrets, private/internal IPs, personal identifiers, or other sensitive values. Block findings and re-scan minimal fixes; excludes general anonymization, PDF/Office/OCR and repository-wide audits."
---

# Git Commit Redaction

Protect the next Git commit, not prove repository/history secret-free. Scan the
**exact staged files**, never the whole repository/history unless explicitly
requested; no PDF, Office, OCR, image metadata or general anonymization.
Never print matched secrets/personal values in logs, reports or chat.

## Gate

After staging intended files and **before creating the commit**, run:

```bash
python3 <skill-dir>/scripts/scan_staged.py
```

| Result / exit | Action |
| --- | --- |
| `pass` / `0` | Continue to commit. |
| `noop` / `0` | No staged files; no redaction needed. |
| `findings` / `1` | Stop publication; inspect only reported files/lines, sanitize, stage fixes and re-scan. |
| `needs_review` / `2` | Stop publication: staged binary, oversized, non-UTF-8 or otherwise unsafe-to-inspect file. |
| `error` / `3` | Stop; fix scanner failure (e.g. outside Git or unreadable staged diff), then re-scan. |

Passing tests never bypass blocking outcomes. Sanitized changes must re-stage/
re-scan to **`pass`**; any later staged-content fix repeats the gate before commit.
Report only finding types, paths and line numbers, never original values.

## Detection and minimal fixes

Sensitive: passwords, API keys, access/bearer tokens, JWTs, private keys,
cloud/provider credentials, GitHub/OpenAI-style tokens, URL/config credentials;
non-example IPv4 when repository policy treats infrastructure addresses as
sensitive; real emails, phones, national IDs, SSN-like IDs and payment-card-like
numbers. Scanner ignores common placeholders: `example.com`, RFC documentation
IPs, `127.0.0.1`, `0.0.0.0`, obvious redacted/dummy secrets.

Remove sensitivity with the smallest change, preserving unrelated behavior:

| Finding | Fix |
| --- | --- |
| Password/token/API key/private key | Remove value; load from environment, secret storage or runtime configuration. |
| URL credential | Remove; inject separately at runtime. |
| Internal/private IP in docs/examples | RFC documentation IP or neutral placeholder. |
| Email/phone/personal ID in docs/tests | Obvious example or synthetic value. |
| Required sensitive test fixture | Deterministic synthetic data preserving only tested format. |

Never commit partially masked real credentials, invent replacement secrets, or
weaken tests, permissions or publication controls. For intentional safe findings,
prefer recognized example values over broad ignore rules.
Already committed/pushed secret: stop, treat as credential exposure, revoke/
rotate **first**, then handle history separately if required.
