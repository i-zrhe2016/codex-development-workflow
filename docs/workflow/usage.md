# Capability Usage Guide

> Type: Guide
> Status: Active
> Scope: Selecting repository capabilities without a fixed development workflow

Start from the user's goal. Let the model reason about the work directly.

| Situation | Capability |
|---|---|
| Complex, dependent, resumable, or explicitly persisted planning | plan-to-ticket |
| Structured verification evidence is needed | test-quality |
| Documented surfaces may change | repo-documentation |
| Verified repository truth materially changed | repo-current-state |
| Staged content may contain sensitive values | data-document-redaction |
| Commit, push, or PR publication is requested | github-publish |
| A diagram materially improves understanding | plantuml |

Ordinary planning, coding, refactoring, exploration, integration, and delegation remain native model work.

Capabilities may be composed when independent triggers apply. That composition is contextual, not a mandatory pipeline.

Stop when the requested outcome is satisfied and applicable hard gates have passed. Do not create extra stages, Issues, documents, or follow-up changes solely for process symmetry.
