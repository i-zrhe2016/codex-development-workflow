# Workflow Usage Guide

`AGENTS.md` is the source of truth for the development lifecycle, engineering rules, and skill invocation policy.

This page intentionally does not duplicate those rules.

## How to use the workflow

For non-trivial repository work, start with `codex-development-workflow`. It reads the repository policy from `AGENTS.md` and dispatches specialist skills only when their documented trigger applies.

The high-level lifecycle is:

`Requirement -> Understand -> Minimal design -> Plan -> Implement -> Validate -> Review -> Update state/docs -> Commit/Push -> Notify`

For exact skill triggers, gates, validation scope, Git rules, architecture rules, and completion behavior, see [`../../AGENTS.md`](../../AGENTS.md).

For skill repositories and installation locations, see [`../../references/skill-map.md`](../../references/skill-map.md).
