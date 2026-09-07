# Repository Current State

Last verified: 2026-09-07 @ working tree

## Current Focus
- None

## Implemented
- The repository packages a gated Codex development workflow with mapped specialist skills.
- The review gate uses Alibaba Open Code Review's `open-code-review` skill from the `alibaba/open-code-review` Codex plugin path.
- The architecture source and rendered SVG document the current workflow gates.

## Constraints
- `open-code-review` requires the local `ocr` CLI, Git 2.41 or later, and a configured Anthropic or OpenAI-compatible model for default review mode.
- The workflow installer copies the skill but does not install the OCR CLI or store model credentials.

## Architecture Snapshot
- `SKILL.md` routes the lifecycle to specialist skills; `scripts/install-all.sh` installs the mapped skill folders.
- Source mappings are maintained in `references/skill-map.md`; detailed flow documentation is under `docs/`.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.

## Next
- None
