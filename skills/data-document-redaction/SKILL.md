---
name: data-document-redaction
description: "Scan the staged Git change for secrets, private infrastructure values, and personal identifiers before commit or publication. Use when staged files may contain sensitive data. Block on findings or unreadable staged files, sanitize minimally, and re-scan. Not for repository-wide audits or PDF/Office/OCR anonymization."
---

# Git Commit Redaction

Protect the next commit, not the whole repository.

## Gate

After staging the intended files and before commit:

```bash
python3 <skill-dir>/scripts/scan_staged.py
```

Handle the result:

- `pass` or `noop`: continue.
- `findings`: stop, sanitize only reported locations, re-stage, and re-run.
- `needs_review`: stop; a staged file could not be inspected safely.
- `error`: stop, fix the scanner/repository problem, and re-run.

Never bypass a blocking result because tests pass. Never print matched values; report only type, path, and line.

## Sensitive data

Treat credentials, tokens, private keys, credential-bearing URLs, non-example private/internal IPs, real emails/phones/personal IDs, and payment-card-like values as sensitive. The scanner already ignores recognized documentation placeholders and obvious dummy values.

## Fix rule

Make the smallest change that removes the real value while preserving behavior:

- load credentials from environment/secret storage/runtime configuration;
- remove credentials from URLs and inject them separately;
- replace infrastructure or personal examples with documented/synthetic values;
- preserve only the required format in test fixtures.

Do not partially mask a real secret or add broad ignores for convenience.

After any staged-content change, run the gate again. Continue only on `pass` or `noop`.

If a secret was already committed or pushed, treat it as exposure: revoke/rotate first, then handle history separately if required.
