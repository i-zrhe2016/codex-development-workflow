# Repository Current State

Last verified: 2026-10-02 @ policy/native-capabilities-first

## Current Focus

- GitHub Issue #187: remove native Codex behavior from repository Skills and keep only repository-specific contracts/tooling/gates.

## Implemented

- The model is the primary orchestrator. Ordinary planning, implementation, investigation, integration, and coordination use native model reasoning instead of mandatory stage Skills.
- GitHub Issues are the sole authoritative source for development tasks. Every implementation task must have an Issue before work begins; chat, PRs, and local Markdown are non-authoritative views.
- Capability invocation is optional when unnecessary or redundant, but Issue lifecycle/evidence, Documentation Impact, and Repo Current State reconciliation records are mandatory.
- The root `codex-development-workflow` bundle is retained only as a thin compatibility and policy layer carrying repository-wide guardrails.
- Five stage bundles are retired: `plan-workflow`, `develop-workflow`, `verify-workflow`, `publish-workflow`, and `integrate-workflow`.
- Five focused capabilities remain: `github-issue-persistence`, `repo-documentation`, `repo-current-state`, `data-document-redaction`, and `github-publish`.
- The installer manages 6 bundles total for both Codex and Claude Code: one thin policy bundle plus five repository-specific capabilities. Claude omits Codex-only `agents/openai.yaml` metadata.
- Native-overlap bundles including `test-quality`, `plan-to-ticket`, and `plantuml` are retired; owned legacy destinations are pruned during `--update`.
- Codex plans and decomposes natively. `github-issue-persistence` only persists durable Plan/Ticket Issue records, stable IDs, delivery metadata, and lifecycle when needed.
- Verification is model-native. The authoritative Issue still records verification evidence or a concrete reason verification was unnecessary.
- `repo-documentation` owns documentation impact and canonical ownership. The model invokes it when documented behavior, architecture, interfaces, configuration, operations, or diagrams may be affected.
- `data-document-redaction` remains a hard publication boundary for staged sensitive surfaces.
- `github-publish` owns guarded Conventional Commit, push, publication identity, and PR readiness.
- `repo-current-state` owns the compact verified recovery snapshot.
- Diagram reasoning and authoring are native Codex work; repository-specific source/render synchronization stays under documentation policy.
- The installer records per-bundle ownership markers, protects unmarked paths, and offers recoverable `--adopt-legacy` migration for pre-marker installs.

## In Progress

- CI verification for the native-first capability reduction.

## Known Issues / Failing Checks

- None known before CI for this branch.

## Constraints

- `agents/openai.yaml` remains required for the Codex target only.
- Persisted Plans and child Tickets require an available, authorized GitHub Issues target.
- Publication, security, permission, verification, redaction, and release controls must not be weakened for convenience.

## Architecture Snapshot

- Model + Capabilities + Guardrails.
- No fixed `plan -> develop -> verify -> publish -> integrate` stage topology.
- Skill frontmatter descriptions expose only repository-specific capabilities; native Codex capabilities are intentionally absent.
- Capability composition is event-driven: the model invokes only capabilities whose trigger applies to the current goal and repository state.
- Runtime skills remain under `skills/`; explanatory documentation remains under `docs/skills/`.
- See `docs/architecture/overview.md` for topology and `docs/deployment/installation.md` for installation behavior.

## Next

- Merge the native-first skill reduction after repository verification passes.
