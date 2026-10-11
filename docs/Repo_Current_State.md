# Repository Current State

Last verified: 2026-10-11 @ working tree

## Implemented

- The installer packages four standalone skills: `repo-documentation`, `repo-current-state`, `plantuml`, and `data-document-redaction` for Codex and Claude Code.
- `--update` replaces bundles marked as installer-managed and prunes retired workflow bundles only when their former ownership marker matches. `--adopt-legacy` backs up unmarked paths before replacing or pruning them.
- Each maintained diagram has a PlantUML source and adjacent SVG render.

## Constraints

- The installer copies skill folders only. Codex bundles include `agents/openai.yaml`; Claude bundles omit it.
- GitHub Issues remain the authority for persisted work plans and tickets; this state note records repository facts only.

## Architecture Snapshot

- Installable sources live in `skills/`; root `README.md` routes to the maintained docs.
- The four bundles are documented under `docs/skills/`; install behavior is documented in `docs/deployment/installation.md`.
