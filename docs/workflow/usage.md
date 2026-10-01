# Capability Usage Guide

> Type: Guide
> Status: Active
> Scope: Selecting repository capabilities without a fixed development workflow

Start from the user's goal, but create or resolve its authoritative GitHub Issue before implementation. GitHub Issues are the sole development-task authority.

| Situation | Capability |
|---|---|
| Complex, dependent, resumable, or explicitly persisted planning | plan-to-ticket |
| Verification evidence is needed | model-native reasoning |
| Documented surfaces may change | repo-documentation |
| Verified repository truth materially changed | repo-current-state |
| Staged content may contain sensitive values | data-document-redaction |
| Commit, push, or PR publication is requested | github-publish |
| A diagram materially improves understanding | plantuml |

Ordinary planning, coding, refactoring, exploration, verification, integration, and delegation remain native model work.

Capabilities may be skipped when unnecessary, redundant, or already satisfied by stronger evidence. Composition is contextual, not a mandatory pipeline.

## Mandatory records

Regardless of which capabilities are invoked, every development Issue must record:
- task status and branch / PR references when applicable;
- verification evidence or why verification was unnecessary;
- Documentation Impact: updated or no-change, with documents/reason;
- Repo Current State: updated or no-change, with document/reason.

A PR may mirror these fields, but the GitHub Issue remains authoritative.

Stop when the requested outcome is satisfied and applicable hard gates have passed. Do not create extra stages, Issues, documents, or follow-up changes solely for process symmetry.
