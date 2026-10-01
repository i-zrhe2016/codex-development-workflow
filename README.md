# Codex Development Capabilities

A native-first repository policy for Codex and Claude Code.

Codex handles general software-engineering work directly. This repository adds Skills only where the repository needs durable external state, deterministic tooling, or hard guards.

## Native-first rule

Keep these native to Codex:

- requirement understanding and planning;
- task decomposition and sequencing;
- architecture and implementation;
- refactoring and investigation;
- verification strategy and test execution;
- delegation, coordination, and integration;
- ordinary Git/GitHub operations;
- diagram design and authoring.

Do not wrap those capabilities in repository Skills.

## Installed skills

- `codex-development-workflow`
- `github-issue-persistence`
- `repo-current-state`
- `repo-documentation`
- `data-document-redaction`
- `github-publish`

## Capability summary

| Capability | Purpose |
|---|---|
| github-issue-persistence | Persist durable GitHub Issue hierarchy, stable IDs, delivery metadata, and lifecycle. |
| repo-documentation | Enforce canonical documentation ownership and repository document conventions. |
| repo-current-state | Maintain the compact verified repository-state snapshot contract. |
| data-document-redaction | Run the deterministic staged sensitive-data gate. |
| github-publish | Enforce repository-specific identity, Conventional Commit, branch, push, and PR guards. |

## Task authority

GitHub Issues are the sole development-task authority. Every development task must have an authoritative Issue before implementation.

A simple task may stay as one Issue. Codex plans natively. Use `github-issue-persistence` only when durable Plan/Ticket records, stable IDs, dependency links, or lifecycle metadata are useful.

Every task Issue records verification evidence or a skip reason, Documentation Impact, and Repo Current State reconciliation.

## Publication

Before publication, required verification must be sufficient, applicable redaction must pass, documentation impact must be recorded, and repository publication guards must pass.

## Installation

Install:

    bash scripts/install-all.sh

Claude Code:

    bash scripts/install-all.sh --target claude

Update and prune retired managed Skills:

    bash scripts/install-all.sh --update

## Skill documentation

| Skill | Runtime source |
|---|---|
| codex-development-workflow | SKILL.md |
| github-issue-persistence | skills/github-issue-persistence/ |
| repo-current-state | skills/repo-current-state/ |
| repo-documentation | skills/repo-documentation/ |
| data-document-redaction | skills/data-document-redaction/ |
| github-publish | skills/github-publish/ |

See `references/skill-map.md` for the managed installation mapping and `docs/architecture/overview.md` for the native-first architecture.
