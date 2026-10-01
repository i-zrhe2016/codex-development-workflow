---
name: data-document-redaction
description: "Run the repository's deterministic staged sensitive-data scanner before publication when staged content has a sensitive surface. Use for the scanner and blocking policy only; Codex handles ordinary editing and remediation natively."
---

# Staged Sensitive-Data Gate

This Skill exists because the repository ships deterministic scanning tooling.

Run from the target Git repository after the intended files are staged:

```bash
python3 <skill-dir>/scripts/scan_staged.py
```

## Outcomes

- `pass` / `noop`: gate is clear.
- `findings`: block publication until the staged content is sanitized and re-scanned.
- `needs_review`: block publication until the uninspectable surface is resolved.
- `error`: block publication until the scanner can run successfully.

After any remediation that changes staged content, re-stage and re-run the scanner.

Report finding type, file path, and line number only. Never echo secret values.

## Scope

The gate protects the next staged Git commit. It is not proof that repository history is clean.

If a real secret was already committed or pushed, treat it as credential exposure: revoke or rotate it first, then handle repository history separately.

Do not weaken scanner, security, permission, verification, or publication controls to make the gate pass.
