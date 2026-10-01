# Repository Current State

Last verified: 2026-10-01 @ capability-driven refactor branch

## Current Focus

- Migrating repository orchestration from fixed stage workflows to model-selected capabilities.

## Implemented

- The model is the primary orchestrator. Ordinary planning, implementation, investigation, integration, and coordination use native model reasoning instead of mandatory stage Skills.
- The root `codex-development-workflow` bundle is retained only as a thin compatibility and policy layer carrying repository-wide guardrails.
- Five stage bundles are retired: `plan-workflow`, `develop-workflow`, `verify-workflow`, `publish-workflow`, and `integrate-workflow`.
- Seven focused capabilities remain: `plan-to-ticket`, `test-quality`, `repo-documentation`, `repo-current-state`, `data-document-redaction`, `github-publish`, and `plantuml`.
- The installer manages 8 bundles total for both Codex and Claude Code: one thin policy bundle plus seven capabilities. Claude omits Codex-only `agents/openai.yaml` metadata.
- `test-workflow` is renamed to `test-quality`; `github-push-when-ready` is renamed to `github-publish`. Owned legacy destinations are retired during `--update`.
- A persisted Plan still owns one branch, one PR, and one merge for all child Tickets and Slices. Persistence is used only when complexity, dependencies, session continuity, or explicit user intent justify it.
- `test-quality` owns risk-aware verification, Acceptance-to-Test evidence, mandatory risk dimensions, flaky/isolation policy, and the Test Quality Gate. The model decides when this capability is warranted.
- `repo-documentation` owns documentation impact and canonical ownership. The model invokes it when documented behavior, architecture, interfaces, configuration, operations, or diagrams may be affected.
- `data-document-redaction` remains a hard publication boundary for staged sensitive surfaces.
- `github-publish` owns guarded Conventional Commit, push, publication identity, and PR readiness.
- `repo-current-state` owns the compact verified recovery snapshot.
- `plantuml` owns diagram source quality, rendering, and readability validation.
- The installer records per-bundle ownership markers, protects unmarked paths, and offers recoverable `--adopt-legacy` migration for pre-marker installs.

## In Progress

- CI verification and diagram regeneration for the capability-driven refactor.

## Known Issues / Failing Checks

- None known before CI for this branch.

## Constraints

- `agents/openai.yaml` remains required for the Codex target only.
- Persisted Plans and child Tickets require an available, authorized GitHub Issues target.
- Publication, security, permission, verification, redaction, and release controls must not be weakened for convenience.

## Architecture Snapshot

- Model + Capabilities + Guardrails.
- No fixed `plan -> develop -> verify -> publish -> integrate` stage topology.
- Skill frontmatter descriptions are the primary discovery/trigger surface.
- Capability composition is event-driven: the model invokes only capabilities whose trigger applies to the current goal and repository state.
- Runtime skills remain under `skills/`; explanatory documentation remains under `docs/skills/`.
- See `docs/architecture/overview.md` for topology and `docs/deployment/installation.md` for installation behavior.

## Next

- Merge the capability-driven refactor after repository verification passes.
