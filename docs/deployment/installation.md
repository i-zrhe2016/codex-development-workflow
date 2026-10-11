# Install the skills

Run the installer from a checkout:

```bash
bash scripts/install-all.sh
```

By default, it installs `repo-documentation`, `repo-current-state`, `plantuml`, and `data-document-redaction` to `${CODEX_HOME:-$HOME/.codex}/skills`. Select Claude Code with `--target claude`; `--dest PATH` selects a custom skills directory.

A fresh install skips any destination folder that already exists. `--update` replaces bundles carrying this installer's ownership marker. It also removes retired workflow bundles only when their marker identifies the former workflow installer. Unmarked paths are preserved unless `--adopt-legacy` is explicitly supplied with `--update`; adoption moves them into a recoverable backup under the destination.

```bash
bash scripts/install-all.sh --target claude --dest /path/to/skills
bash scripts/install-all.sh --update
bash scripts/install-all.sh --target claude --update --adopt-legacy
```

Codex bundles include `agents/openai.yaml`. Claude bundles omit that Codex-only metadata. The installer copies skill folders only; it does not install or edit `AGENTS.md`, host settings, or project runtime configuration.

To check a destination, confirm it contains the four named folders and that each contains `SKILL.md`. Installation is local file copying and does not run the bundled scanner or access external services.

## Checks

Run the installer regression tests and shell syntax checks with:

```bash
python -m unittest discover -s scripts/tests -p 'test_*.py'
bash -n scripts/install-all.sh
bash -n scripts/render-diagrams.sh
```

The installer tests use temporary directories and cover both targets, bundle contents, ownership-aware updates, legacy backup behavior, and unowned folder preservation.
