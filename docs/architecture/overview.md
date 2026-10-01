# Capability Architecture

> Type: Architecture
> Status: Active
> Scope: Capability-driven repository development architecture

## Core model

The model is the orchestrator. There is no fixed stage topology.

User goal -> Model reasoning -> native work or discovered capability -> Model reasoning -> requested outcome.

Planning, implementation, verification, publication, and integration are outcomes the model reasons about, not repository Skills that must be traversed.

## Components

| Component | Responsibility |
|---|---|
| Model | Understand intent, choose architecture, implement, coordinate, select capabilities, integrate results, own final judgment |
| codex-development-workflow | Thin compatibility policy and guardrails |
| plan-to-ticket | Durable decomposition and GitHub Issue persistence |
| test-quality | Verification strategy, evidence matrix, mandatory risk dimensions, Test Quality Gate |
| repo-documentation | Documentation impact and canonical ownership |
| repo-current-state | Verified current-state snapshot |
| data-document-redaction | Staged sensitive-data scan |
| github-publish | Commit/push/PR publication guard |
| plantuml | Diagram source, render, and readability validation |

![Capability architecture](diagrams/components.svg)

Source: [components.puml](diagrams/components.puml)

## Event-driven capability use

- complex/resumable requirement -> plan-to-ticket
- behavior needs proof -> test-quality
- documented surface changed -> repo-documentation
- staged sensitive surface -> data-document-redaction
- commit/push/PR requested -> github-publish
- verified repo truth changed -> repo-current-state
- diagram improves understanding -> plantuml

Capabilities may compose naturally, but composition is decided from the current goal and evidence rather than a predefined chain.
