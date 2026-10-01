# Capability Architecture

> Type: Architecture
> Status: Active
> Scope: Native-first repository capability architecture

## Core model

Codex is the orchestrator and owns ordinary software-engineering reasoning and execution.

Repository Skills exist only for durable repository-specific state, deterministic tooling, external persistence, or hard gates.

User goal -> Codex native work -> repository-specific capability only when needed -> requested outcome.

## Components

| Component | Responsibility |
|---|---|
| Codex | Planning, decomposition, architecture, implementation, verification, delegation, integration, Git/GitHub operation, diagram authoring |
| codex-development-workflow | Thin repository policy and hard guardrails |
| github-issue-persistence | Durable GitHub Issue schema, stable IDs, delivery metadata, lifecycle |
| repo-documentation | Documentation ownership and repository document conventions |
| repo-current-state | Verified current-state snapshot contract |
| data-document-redaction | Deterministic staged sensitive-data scan |
| github-publish | Repository-specific publication guards |

## Trigger model

- durable GitHub task records needed -> github-issue-persistence
- documented repository facts changed -> repo-documentation
- verified repository truth materially changed -> repo-current-state
- staged sensitive surface -> data-document-redaction
- commit/push/PR publication -> github-publish

Planning, testing, Git operations, and diagrams remain native even when a repository contract records their result.

Mandatory Issue records remain independent of Skill invocation: status/delivery references, verification evidence or skip reason, Documentation Impact, and Repo Current State reconciliation.
