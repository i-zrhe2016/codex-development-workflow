# Repository Current State

Last verified: 2026-10-02 @ policy/zero-skills

## Current Focus

- GitHub Issue #189: disable all runtime Skills and consolidate non-native repository requirements into `AGENTS.md`.

## Implemented

- Codex is the sole reasoning/execution control plane for ordinary software-engineering work.
- The repository has zero runtime Skill entrypoints: no root `SKILL.md` and no `skills/**/SKILL.md`.
- `AGENTS.md` is the single repository runtime policy surface.
- GitHub Issues remain the sole authoritative development-task store.
- Durable Plan/Ticket Issue schema, stable IDs, lifecycle, one-Plan/one-branch/one-PR rules, and required task records are defined in `AGENTS.md`.
- Documentation ownership, document standards, and Repo Current State reconciliation are defined in `AGENTS.md` with detailed standards under `docs/reference/`.
- Deterministic sensitive-data scanning lives at `scripts/redaction/scan_staged.py`.
- Deterministic publication checks live under `scripts/publication/`.
- Diagram authoring is native Codex work; deterministic repository rendering remains `scripts/render-diagrams.sh`.
- `scripts/retire-skills.sh` removes previously managed Skill installations while preserving unverified/unrelated directories.

## In Progress

- CI verification for the zero-Skill migration.

## Known Issues / Failing Checks

- None known before CI for this branch.

## Constraints

- Repository-specific hard gates must not be weakened merely because their former Skill wrappers were removed.
- GitHub Issue persistence requires an available authorized GitHub target.
- Public diagram rendering must not receive sensitive or unreleased architecture.

## Architecture Snapshot

- Codex native capabilities + `AGENTS.md` contracts + deterministic scripts.
- No Skill discovery, Skill routing, or Skill installation.
- GitHub Issues hold task authority; repository docs hold canonical technical documentation.

## Next

- Merge the zero-Skill migration after repository verification passes.
