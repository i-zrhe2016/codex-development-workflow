# Workflow Usage Guide

For non-trivial repository work, start with `codex-development-workflow` and dispatch specialist skills only when their trigger applies.

High-level lifecycle:

`Requirement -> Understand -> Minimal design -> Plan -> Implement -> Validate -> Review -> Update state/docs -> Redact when needed -> Commit/Push -> Notify`

## Redaction gate

Before content is shared or published, invoke `data-document-redaction` when data, documents, logs, configs, images, screenshots, or exports may contain personal information, credentials, or business-sensitive information.

The redaction skill owns the detailed procedure: detection, minimum necessary transformation, hidden-surface checks, validation, and delivery reporting. This workflow does not duplicate those instructions.

If no potentially sensitive content crosses a sharing or publication boundary, skip the redaction gate.

For skill repositories and installation locations, see [`../../references/skill-map.md`](../../references/skill-map.md).
