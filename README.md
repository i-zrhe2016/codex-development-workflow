# Codex Development Capabilities

A capability-driven repository for Codex and Claude Code.

The model reasons about the user's goal directly and invokes specialized Skills only when they add repository-specific contracts, deterministic tooling, or hard safety gates. There is no mandatory plan -> develop -> verify -> publish -> integrate workflow.

## Architecture

User goal -> Model reasoning -> native work or a matching capability -> Model reasoning -> completion.

The root codex-development-workflow package is retained only as a thin compatibility and policy layer. It does not route requests through stage Skills.

## Design principles

- GitHub Issues are the sole development-task authority.
- Model decides when a capability is useful; unnecessary or redundant capabilities may be skipped.
- Capability defines specialized how.
- Documentation/state record obligations cannot be skipped even when the corresponding Skill is skipped.
- Keep hard guardrails explicit.
- Prefer native model reasoning over procedural wrappers.
- Prefer the smallest useful context and execution topology.
- Do not invoke a capability merely because it exists.

## Hard guardrails

Before publication, required verification must have sufficient evidence, applicable sensitive-data checks must pass, documentation impact must be considered, and target repository branch/PR policy must be respected.

Never weaken security, permission, branch, verification, or release controls for convenience.

## Installed skills

- `codex-development-workflow`
- `plan-to-ticket`
- `test-quality`
- `plantuml`
- `repo-current-state`
- `repo-documentation`
- `data-document-redaction`
- `github-publish`

## Capability summary

| Capability | Purpose |
|---|---|
| plan-to-ticket | Persist complex/resumable work as Plan, Tickets, and dependency-ordered Slices. |
| test-quality | Map acceptance criteria to evidence and close a risk-aware Test Quality Gate. |
| repo-documentation | Govern documentation impact, canonical ownership, diagrams, and lifecycle. |
| repo-current-state | Maintain the compact verified repository-state snapshot. |
| data-document-redaction | Scan staged content for credentials, personal data, and other sensitive values. |
| github-publish | Guard Conventional Commit, push, publication identity, and PR readiness. |
| plantuml | Create, render, and review maintainable engineering diagrams. |

## Task authority and planning

Every repository development task starts from an authoritative GitHub Issue. A small task may remain one Issue. Use plan-to-ticket only when decomposition into a Plan, Tickets, and Slices adds value.

Chat, PR bodies, local Markdown, and model memory may link to or summarize the Issue but are not parallel task stores.

For every task, the Issue must record verification evidence or a skip reason, Documentation Impact, and Repo Current State reconciliation. Those records are mandatory even when the model skips the corresponding capability Skill.

## Verification model

The model decides whether verification is warranted from the requirement, changed behavior, and risk. Use test-quality when structured verification evidence is needed. Verification levels remain bounded: minimal, focused, regression, or full. PASS is controlled by the Test Quality Gate.

## Publication model

When a repository change is ready to publish, the model independently checks whether documentation, redaction, and publication capabilities apply. These are event-driven capability triggers, not mandatory workflow stages.

## Installation

Install all managed capabilities:

    bash scripts/install-all.sh

Claude Code:

    bash scripts/install-all.sh --target claude

Update an existing managed installation:

    bash scripts/install-all.sh --update

During update, retired stage Skills and old capability names are removed only when their ownership marker confirms they came from this repository.

## Skill documentation

| Skill | Runtime source | Documentation |
|---|---|---|
| codex-development-workflow | SKILL.md | AGENTS.md |
| plan-to-ticket | skills/plan-to-ticket/ | docs/skills/plan-to-ticket/ |
| test-quality | skills/test-quality/ | docs/skills/test-quality/ |
| plantuml | skills/plantuml/ | docs/skills/plantuml/ |
| repo-current-state | skills/repo-current-state/ | docs/skills/repo-current-state/ |
| repo-documentation | skills/repo-documentation/ | docs/skills/repo-documentation/ |
| data-document-redaction | skills/data-document-redaction/ | docs/skills/data-document-redaction/ |
| github-publish | skills/github-publish/ | docs/skills/github-publish/ |

See references/skill-map.md for managed installation mapping and docs/architecture/overview.md for the capability architecture.
