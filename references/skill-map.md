# Skill Map

This repository installs one thin policy package plus five repository-specific capabilities. Native Codex behavior is intentionally not packaged as Skills.

| Skill | Managed source | Repository-specific value |
|---|---|---|
| codex-development-workflow | repository root | Thin policy and hard guardrails |
| github-issue-persistence | skills/github-issue-persistence/ | Durable GitHub Issue schema, IDs, and lifecycle |
| repo-current-state | skills/repo-current-state/ | Verified current-state snapshot contract |
| repo-documentation | skills/repo-documentation/ | Canonical documentation ownership and file/lifecycle rules |
| data-document-redaction | skills/data-document-redaction/ | Deterministic staged sensitive-data gate |
| github-publish | skills/github-publish/ | Deterministic publication identity and branch/commit/PR guards |

## Native Codex capabilities

Do not add Skills for ordinary planning/decomposition, implementation/refactoring, verification/testing, delegation/coordination, Git/GitHub operations, or diagram authoring. Codex performs those natively.

## Retired bundles

Owned legacy destinations are pruned on `--update`, including:

- plan-workflow
- develop-workflow
- verify-workflow
- publish-workflow
- integrate-workflow
- test-workflow
- test-quality
- plan-to-ticket
- plantuml
- github-push-when-ready
