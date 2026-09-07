---
name: codex-development-workflow
description: "Entry point for the repository-wide Codex development lifecycle. Use for non-trivial feature development, bug fixes, refactors, and repository changes. This skill orchestrates specialist skills and invokes data-document-redaction before sensitive content is shared or published."
---

# Codex Development Workflow

Use this skill as the entry point for non-trivial repository development.

## Workflow

`Requirement -> Understand -> Minimal design -> Plan/Tickets -> Implement -> Validate -> Review -> Update state/docs -> Redact when needed -> Commit/Push -> Notify`

## Specialist Skills

Invoke specialist skills only when their trigger applies. Follow each skill's own `SKILL.md` for detailed procedures; do not duplicate them here.

- `context-efficiency`: large, unfamiliar, or context-heavy repository exploration.
- `plan-to-ticket`: non-trivial multi-step or dependent work.
- relevant test skill: changed behavior that has a matching test workflow.
- `frontend-click-test`: frontend interaction or browser-visible behavior changes.
- `code-review`: meaningful implementation after relevant tests pass.
- `repo-current-state`: verified repository behavior, architecture, dependencies, deployment, or important state changed.
- `data-document-redaction`: before sharing or publishing data, documents, logs, configs, images, exports, or other content that may contain personal information, credentials, or business-sensitive information.
- `github-push-when-ready`: before commit or push.
- `bark-finish-notify`: once after implementation and validation, before the final response.

For `data-document-redaction`, the redaction skill owns the complete detection, transformation, hidden-surface checking, validation, and reporting procedure. This workflow only decides when to invoke it.

Read `references/skill-map.md` only when repository sources or install locations are needed.

If a required specialist skill is unavailable locally, report it rather than silently replacing its workflow.

## Installation

Install the complete workflow skill set with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

Update existing installations with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Codex uses `${CODEX_HOME:-$HOME/.codex}/skills` by default. Restart Codex after installation.
