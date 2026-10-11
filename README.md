# Documentation Skills

A small collection of Codex skills for documenting repositories, maintaining a verified current-state note, creating PlantUML diagrams, and scanning staged content before publication.

## Install

```bash
bash scripts/install-all.sh
```

The installer adds these four skills to the Codex skills directory:

- `repo-documentation` — maintain canonical, reachable repository documentation.
- `repo-current-state` — keep a concise snapshot of verified repository state.
- `plantuml` — create, render, and review diagrams when they clarify behavior.
- `data-document-redaction` — scan staged files before commit or publication.

Use `--target claude` for Claude Code, `--dest PATH` for a custom directory, and `--update` to update managed copies and remove retired workflow bundles owned by this installer. Unowned destinations are preserved. See [installation details](docs/deployment/installation.md).

## Documentation

- [Skill map](references/skill-map.md)
- [Current repository state](docs/Repo_Current_State.md)
- [Installation](docs/deployment/installation.md)
- [repo-documentation skill](docs/skills/repo-documentation/README.md)
- [repo-current-state skill](docs/skills/repo-current-state/README.md)
- [PlantUML skill](docs/skills/plantuml/README.md)
- [Staged redaction skill](docs/skills/data-document-redaction/README.md)
