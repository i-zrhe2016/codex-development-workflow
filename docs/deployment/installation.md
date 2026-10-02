# Zero-Skill Migration Guide

> Type: Guide
> Status: Active
> Scope: Removing Skills installed by earlier repository versions

## Current behavior

This repository no longer installs Skills for Codex or Claude Code.

Codex reads `AGENTS.md` as repository instructions. Repository tools are ordinary scripts under `scripts/`.

## Retire previously managed Skills

Codex destination:

```bash
bash scripts/retire-skills.sh
```

Claude Code destination:

```bash
bash scripts/retire-skills.sh --target claude
```

Explicit directory:

```bash
bash scripts/retire-skills.sh --dest /path/to/skills
```

The script removes only directories with the matching `.codex-development-workflow-managed` marker. Unmarked paths are preserved as `ownership unverified`.

## No replacement Skill

Do not install a root compatibility Skill or specialist Skills after retirement.

Repository-specific requirements have moved to `AGENTS.md`. Deterministic tooling remains under:

- `scripts/redaction/`
- `scripts/publication/`
- `scripts/render-diagrams.sh`

## Host behavior

Codex uses `AGENTS.md` directly as project instructions.

If another host does not consume `AGENTS.md`, mirror or link the repository policy through that host's supported project-instruction mechanism; do not re-create it as a Skill.
