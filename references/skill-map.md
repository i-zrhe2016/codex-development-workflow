# Skill Map

This repository installs one thin policy package plus seven focused capabilities. The model decides when each capability applies; there is no stage-workflow routing layer.

| Skill | Managed source | Purpose |
|---|---|---|
| codex-development-workflow | repository root | Thin compatibility policy and hard guardrails only |
| plan-to-ticket | skills/plan-to-ticket/ | Persisted Plan / Ticket / Slice contracts |
| test-quality | skills/test-quality/ | Risk-aware verification and Test Quality Gate |
| plantuml | skills/plantuml/ | Engineering diagrams |
| repo-current-state | skills/repo-current-state/ | Verified repository-state snapshot |
| repo-documentation | skills/repo-documentation/ | Documentation governance |
| data-document-redaction | skills/data-document-redaction/ | Staged sensitive-data gate |
| github-publish | skills/github-publish/ | Guarded commit, push, and PR publication |

## Selection model

Skill metadata is the discovery surface. Descriptions state the capability and its trigger. The model uses native reasoning for ordinary planning, implementation, investigation, integration, and coordination.

## Retired bundles

Owned legacy destinations are pruned on --update:
- plan-workflow
- develop-workflow
- verify-workflow
- publish-workflow
- integrate-workflow
- test-workflow (renamed to test-quality)
- github-push-when-ready (renamed to github-publish)
