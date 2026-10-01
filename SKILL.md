---
name: codex-development-workflow
description: "Thin repository development policy for capability-driven Codex and Claude Code work. Use as a compatibility entry point when repository-wide engineering guardrails are needed. It does not route work through fixed plan/develop/verify/publish/integrate stages. The model reasons about the user's goal directly and invokes specialized capabilities only when their trigger applies."
---

# Capability-Driven Development Policy

Use model reasoning as the default control plane.

Do not run a fixed development workflow and do not require a stage Skill for ordinary planning, implementation, verification, publication, or integration. Select specialized capabilities only when they add repository-specific behavior, durable contracts, deterministic scripts, or hard safety gates.

## Capability selection

Available capabilities:
- plan-to-ticket — Plan / Ticket / Slice decomposition and GitHub Issue persistence.
- test-quality — risk-aware verification and the Test Quality Gate.
- repo-documentation — documentation impact, canonical ownership, and lifecycle.
- repo-current-state — verified repository-state reconciliation.
- data-document-redaction — staged sensitive-data scanning and sanitization.
- github-publish — guarded Conventional Commit, push, and pull-request publication.
- plantuml — maintainable engineering diagrams.

The model decides when to invoke each capability from the current task and repository state. Prefer the most specific capability. Multiple capabilities may be composed when their independent triggers apply. Skip a capability when it is unnecessary, duplicative, or its outcome is already established by stronger evidence.

## Native model work

Use native reasoning for understanding requirements, architecture and design choices, implementation, refactoring, local exploration, delegation choices, integration, and deciding whether verification, documentation, publication, or state reconciliation is needed.

Do not wrap these ordinary decisions in an extra workflow Skill.

## Task authority

GitHub Issues are the sole authoritative source for repository development tasks. Before implementation begins, ensure the task exists as an Issue in the target repository. Chat, PR descriptions, local Markdown, and model memory may reference the Issue but must not replace it.

Small tasks may use one Issue directly. Use plan-to-ticket only when a task needs Plan / Ticket / Slice decomposition.

If the authoritative Issue cannot be created or updated, implementation is blocked.

## Non-skippable record contract

Skill invocation is optional; required records are not.

For every development task, update the authoritative Issue with:
- current status plus branch / PR references when applicable;
- verification evidence, or a concrete reason structured verification was unnecessary;
- `Documentation Impact: updated | no-change` plus documents or reason;
- `Repo Current State: updated | no-change` plus document or reason.

The model may produce these records directly without loading the corresponding Skill, but it may not bypass the records.

## Guardrails

Before publication:
- required verification evidence must be sufficient;
- applicable redaction must pass;
- documentation impact must be considered;
- publication must follow the target repository's branch and PR policy.

Never weaken security, permission, branch, verification, or release gates for convenience.

## Verification contract

When structured verification is needed, use test-quality. PASS requires the Test Quality Gate, not merely a green focused test. Retry cannot convert an unexplained flaky failure to PASS. Coverage is diagnostic evidence only.

## Persistence contract

Use plan-to-ticket when the authoritative Issue needs complex, dependent, resumable, or explicitly requested decomposition. A decomposed Plan owns one branch, one PR, and one merge for all child Tickets and Slices.

## Publication contract

Use github-publish when a change is ready to commit, push, or open/update a pull request. Use data-document-redaction before the commit when the staged set may contain sensitive values. Use repo-documentation when documentation may be affected.

## Completion

Finish when the user's requested outcome is satisfied, the authoritative Issue contains all required records, and all applicable capability contracts and hard guardrails have passed. Do not manufacture extra stages, artifacts, or follow-up work merely to match a process.
