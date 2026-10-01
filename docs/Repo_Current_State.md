# Repository Current State

Last verified: 2026-10-02 @ policy/native-model-first

## Current Focus

- GitHub Issue #186: preserve native model capabilities and reduce `plan-to-ticket` to GitHub Issue persistence.

## Implemented

- The model is the primary orchestrator. Ordinary planning, implementation, investigation, integration, and coordination use native model reasoning instead of mandatory stage Skills.
- GitHub Issues are the sole authoritative source for development tasks. Every implementation task must have an Issue before work begins; chat, PRs, and local Markdown are non-authoritative views.
- Capability invocation is optional when unnecessary or redundant, but Issue lifecycle/evidence, Documentation Impact, and Repo Current State reconciliation records are mandatory.
- The root `codex-development-workflow` bundle is retained only as a thin compatibility and policy layer carrying repository-wide guardrails.
- Five stage bundles are retired: `plan-workflow`, `develop-workflow`, `verify-workflow`, `publish-workflow`, and `integrate-workflow`.
- Six focused capabilities remain: `plan-to-ticket`, `repo-documentation`, `repo-current-state`, `data-document-redaction`, `github-publish`, and `plantuml`; each is limited to repository-specific behavior.
- The installer manages 7 bundles total for both Codex and Claude Code: one thin policy bundle plus six capabilities. Claude omits Codex-only `agents/openai.yaml` metadata.
- `test-workflow` and `test-quality` are retired; `github-push-when-ready` is renamed to `github-publish`. Owned legacy destinations are retired during `--update`.
- Planning, decomposition, sequencing, acceptance criteria, test design, and delegation are native model work. `plan-to-ticket` only persists a model-decided Plan/Ticket structure; a persisted Plan owns one branch, one PR, and one merge.
- Verification is model-native. The authoritative Issue still records verification evidence or a concrete reason verification was unnecessary.
- `repo-documentation` owns documentation impact and canonical ownership. The model invokes it when documented behavior, architecture, interfaces, configuration, operations, or diagrams may be affected.
- `data-document-redaction` remains a hard publication boundary for staged sensitive surfaces.
- `github-publish` owns guarded Conventional Commit, push, publication identity, and PR readiness.
- `repo-current-state` owns the compact verified recovery snapshot.
- `plantuml` owns diagram source quality, rendering, and readability validation.
- The installer records per-bundle ownership markers, protects unmarked paths, and offers recoverable `--adopt-legacy` migration for pre-marker installs.

## In Progress

- CI verification and diagram regeneration for the native-model-first refactor.

## Known Issues / Failing Checks

- None known before CI for this branch.

## Constraints

- `agents/openai.yaml` remains required for the Codex target only.
- Persisted Plans and child Tickets require an available, authorized GitHub Issues target.
- Publication, security, permission, verification, redaction, and release controls must not be weakened for convenience.

## Architecture Snapshot

- Native Model + Repository-Specific Capabilities + Guardrails.
- No fixed `plan -> develop -> verify -> publish -> integrate` stage topology.
- Skill frontmatter descriptions are the primary discovery/trigger surface.
- Capability composition is event-driven: the model invokes only capabilities whose trigger applies to the current goal and repository state.
- Runtime skills remain under `skills/`; explanatory documentation remains under `docs/skills/`.
- See `docs/architecture/overview.md` for topology and `docs/deployment/installation.md` for installation behavior.

## Next

- Merge the native-model-first refactor after repository verification passes.
