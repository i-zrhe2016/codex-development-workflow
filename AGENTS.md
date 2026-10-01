# AGENTS.md

Repository-specific policy only. Codex owns ordinary reasoning and execution.

## Native-first rule

Use Codex natively for planning, decomposition, architecture, implementation, refactoring, investigation, verification, delegation, coordination, integration, ordinary Git/GitHub operations, and diagram authoring.

Do not invoke or add a Skill merely to teach those capabilities.

A repository Skill is justified only when it adds at least one of:

- a durable repository-specific data contract;
- deterministic repository tooling;
- an external-system persistence contract;
- a hard safety or publication gate.

## GitHub Issues authority

GitHub Issues are the sole authoritative development-task store.

- Every development task must have an authoritative Issue before implementation.
- Chat, PR bodies, local Markdown, TODO files, and model memory are non-authoritative views.
- Use `github-issue-persistence` only for repository-specific Issue hierarchy, identifiers, or lifecycle metadata.
- If the authoritative Issue cannot be created or updated, implementation is blocked.

## Active Skills

- `github-issue-persistence`: GitHub Issue persistence schema and lifecycle.
- `repo-documentation`: canonical documentation ownership and repository document conventions.
- `repo-current-state`: verified repository-state snapshot contract.
- `data-document-redaction`: deterministic staged sensitive-data gate.
- `github-publish`: repository-specific publication guards.

## Required records

Every development Issue must keep current:

- task status and branch / PR references when applicable;
- verification evidence or a concrete skip reason;
- `Documentation Impact: updated | no-change` with documents or reason;
- `Repo Current State: updated | no-change` with document or reason.

## Hard guardrails

Before publication, required verification, applicable redaction, documentation impact, and repository publication policy must pass.

Never commit credentials, tokens, private keys, `.env`, or other secrets. Never weaken security, permissions, verification, branch, redaction, or release controls to complete a task.

## Documentation

Keep `README.md` as the project introduction and documentation index. Detailed documentation belongs under `docs/`. Maintain one canonical owner per fact and link instead of duplicating.
