# Repository Policy Usage

> Type: Guide
> Status: Active
> Scope: Using the repository without runtime Skills

There is no capability routing layer.

1. Codex handles the user's engineering goal natively.
2. `AGENTS.md` supplies repository-specific contracts.
3. Run deterministic scripts only when their gate applies.
4. Persist task state and required records in the authoritative GitHub Issue.

## Deterministic gates

| Need | Tool |
|---|---|
| staged sensitive-data check | `python3 scripts/redaction/scan_staged.py` |
| publication readiness | `python3 scripts/publication/assess_push_readiness.py --json` |
| guarded commit/push | `python3 scripts/publication/push_if_ready.py ... --execute` |
| diagram render | `bash scripts/render-diagrams.sh render` |
| diagram drift check | `bash scripts/render-diagrams.sh --check` |

Planning, coding, testing, delegation, Git/GitHub operations, and diagram authoring do not require wrappers.
