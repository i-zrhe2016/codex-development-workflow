# Capability Architecture

> Type: Architecture
> Status: Active
> Scope: Capability-driven repository development architecture

## Core model

The model is the orchestrator. There is no fixed stage topology.

GitHub Issues are the sole development-task authority. Capability Skills are optional execution aids; mandatory records are policy-level invariants and cannot be bypassed.

User goal -> Model reasoning -> native work or discovered capability -> Model reasoning -> requested outcome.

Planning, implementation, verification, publication, and integration are outcomes the model reasons about, not repository Skills that must be traversed.

## Components

| Component | Responsibility |
|---|---|
| Model | Resolve the authoritative Issue, understand intent, choose architecture, implement, coordinate, select/skip capabilities, integrate results, own final judgment and mandatory records |
| codex-development-workflow | Thin compatibility policy and guardrails |
| plan-to-ticket | Durable decomposition and GitHub Issue persistence |
| repo-documentation | Documentation impact and canonical ownership |
| repo-current-state | Verified current-state snapshot |
| data-document-redaction | Staged sensitive-data scan |
| github-publish | Commit/push/PR publication guard |
| plantuml | Diagram source, render, and readability validation |

## Event-driven capability use

- complex/resumable requirement -> plan-to-ticket
- behavior needs proof -> model-native verification
- documented surface changed -> repo-documentation
- staged sensitive surface -> data-document-redaction
- commit/push/PR requested -> github-publish
- verified repo truth changed -> repo-current-state
- diagram improves understanding -> plantuml

Capabilities may compose naturally, but composition is decided from the current goal and evidence rather than a predefined chain. A capability may be skipped when unnecessary or redundant.

Mandatory Issue records remain independent of capability invocation: status/delivery references, verification evidence or skip reason, Documentation Impact, and Repo Current State reconciliation.


## Detailed execution diagrams

Persisted Plan execution details remain capability references rather than mandatory workflow stages:

- [ticket-lifecycle.puml](diagrams/ticket-lifecycle.puml) — persisted Plan / Ticket delivery boundary.
- [ticket-slice-loop.puml](diagrams/ticket-slice-loop.puml) — dependency-ready Slice execution and verification loop.
