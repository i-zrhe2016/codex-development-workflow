# Workflow Usage Guide

For non-trivial repository work, start with `codex-development-workflow` and dispatch specialist skills only when their trigger applies.

High-level lifecycle:

`Requirement -> Understand -> Minimal design -> Plan -> Implement -> Validate -> Review -> Update state/docs -> Classify outputs -> Redact when needed -> Commit/Push -> Notify`

The `Review` stage uses the `open-code-review` specialist skill, which invokes
Alibaba Open Code Review's local `ocr` CLI. Configure the CLI before relying on
the review gate; installation details are in the
[installation guide](../deployment/installation.md).

## Output classification

Classify the complete change set before staging or committing it, and again
before any separate sharing, export, upload, or publication boundary. Include
source files, documentation, logs, configs, images, screenshots, exports,
filenames, and metadata in the scope.

Record the recipient/environment, purpose, required utility, and whether
controlled reversibility is allowed. The default is non-reversible handling.

## Redaction gate

If classification finds no potentially sensitive surface, record the inspected
scope and the reason the gate was skipped, then continue to the next workflow
stage. Otherwise, invoke `data-document-redaction` and follow the detailed
[redaction workflow](redaction.md).

The specialist skill owns format-specific detection, minimum necessary
transformation, hidden-surface checks, validation, and delivery reporting. The
orchestrator accepts the boundary transition only when the report is `pass`.
`needs_review` and `blocked` results stop commit, push, sharing, and
publication until the concrete gap is resolved.

Reports must contain only safe evidence: entity types, counts, location
categories, hashes, tool versions, coverage, utility checks, and residual
risks. Do not include original values, mappings, credentials, or complete
matching context.

For skill repositories and installation locations, see [`../../references/skill-map.md`](../../references/skill-map.md).
