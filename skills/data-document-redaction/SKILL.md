---
name: data-document-redaction
description: "Scan and sanitize files staged for a Git/GitHub commit or pull request. Use before commit, push, or PR publication when changed files may contain credentials, tokens, private/internal IP addresses, personal identifiers, or other sensitive values. Inspect only the staged commit set by default, block publication on findings, apply the smallest safe replacement, and re-scan until clean. Not for general document anonymization, PDF/Office/OCR processing, or repository-wide privacy audits."
---

# Git Commit Redaction

Prevent sensitive values in the current Git change from reaching GitHub.

## Scope

- Scan the exact files staged for the next commit.
- Do not scan the whole repository unless explicitly requested.
- Do not inspect Git history unless explicitly requested.
- Do not handle PDF, Office, OCR, image metadata, or general-purpose document anonymization.
- Never print matched secret or personal values in logs, reports, or chat.

## Gate

Run this gate after the intended files are staged and before the commit is created:

```bash
python3 <skill-dir>/scripts/scan_staged.py
```

Interpret the result:

- `pass`: continue to commit.
- `findings`: stop publication, inspect only the reported files/lines, sanitize the values, stage the fixes, and run the scan again.
- `needs_review`: stop publication because a staged file could not be safely inspected, such as a binary, oversized, or non-UTF-8 file.
- `noop`: no staged files; no redaction action is required.

Do not bypass `findings` or `needs_review` merely because tests pass.

## What to detect

Treat these as sensitive when they appear in staged files:

- passwords, API keys, access tokens, bearer tokens, JWTs, private keys;
- cloud/provider credentials and GitHub/OpenAI-style tokens;
- credentials embedded in URLs or config assignments;
- non-example IPv4 addresses when repository policy treats infrastructure addresses as sensitive;
- real email addresses, phone numbers, national IDs, SSN-like identifiers, and payment-card-like numbers.

The bundled scanner intentionally ignores common documentation placeholders such as `example.com`, RFC documentation IP ranges, `127.0.0.1`, `0.0.0.0`, and obvious redacted/dummy secret values.

## Sanitize minimally

Choose the smallest change that removes the sensitive value without changing unrelated behavior:

| Finding | Preferred fix |
| --- | --- |
| Password / token / API key / private key | Remove the value and load it from environment, secret storage, or runtime configuration. |
| Credential in URL | Remove the credential from the URL and inject it separately at runtime. |
| Internal/private IP in docs/examples | Replace with an RFC documentation IP or a neutral placeholder. |
| Email / phone / personal ID in docs/tests | Replace with an obvious example or synthetic value. |
| Sensitive value required for a test fixture | Replace with deterministic synthetic data that preserves the tested format only. |

Do not partially mask a real credential and leave it committed. Do not invent replacement secrets.

If a finding is intentional and truly safe, prefer replacing it with a recognized example value rather than adding a broad ignore rule.

## Re-scan after changes

After sanitizing:

1. stage the corrected files;
2. rerun `scan_staged.py`;
3. continue only on `pass`;
4. report only finding types, file paths, and line numbers, never original values.

A later review fix that changes staged content must pass this gate again before the next commit.

## Boundaries

- This gate protects the next Git commit; it is not proof that the repository or history contains no secrets.
- If a secret was already committed or pushed, stop and treat it as credential exposure: revoke/rotate it first, then handle history separately if required.
- Do not weaken repository tests, permissions, or publication controls to make the scan pass.
