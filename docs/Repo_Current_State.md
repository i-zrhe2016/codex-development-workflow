# Repository Current State

Last verified: 2026-09-07 @ working tree

## Current Focus
- None

## Implemented
- The repository packages a gated Codex development workflow with mapped specialist skills.
- The review gate uses the Codex CLI's built-in `codex review` command.
- The architecture source and rendered SVG document the current workflow gates.

## Constraints
- Code review requires an installed and authenticated Codex CLI; review targets are selected with one of `--uncommitted`, `--base`, or `--commit`.

## Architecture Snapshot
- `SKILL.md` routes the lifecycle to specialist skills; `scripts/install-all.sh` installs the mapped skill folders.
- Source mappings are maintained in `references/skill-map.md`; detailed flow documentation is under `docs/`.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.

## Next
- None
