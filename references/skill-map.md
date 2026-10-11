# Skill Map

`scripts/install-all.sh` installs the following standalone bundles from `skills/`:

| Skill | Repository source | Documentation |
|---|---|---|
| `repo-documentation` | `skills/repo-documentation/` | `docs/skills/repo-documentation/` |
| `repo-current-state` | `skills/repo-current-state/` | `docs/skills/repo-current-state/` |
| `plantuml` | `skills/plantuml/` | `docs/skills/plantuml/` |
| `data-document-redaction` | `skills/data-document-redaction/` | `docs/skills/data-document-redaction/` |

Each bundle contains its own `SKILL.md` and Codex `agents/openai.yaml`. The installer supports Codex (default), Claude Code, and a custom `--dest` directory. It does not install repository instructions or runtime configuration.
