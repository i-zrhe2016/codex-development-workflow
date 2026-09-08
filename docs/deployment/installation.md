# Installation and Update Guide

## Prerequisites

The installer requires:

- Bash;
- `tar`; and
- a complete checkout of this repository.

Codex should be restarted after installation so the new skill directories are
discovered.

## Run code review

The review gate uses the Codex CLI's built-in `codex review` command. Install
and authenticate Codex before using it; no separate review skill is required.
Choose one review target per invocation:

```bash
codex review --uncommitted  # staged, unstaged, and untracked changes
codex review --base main    # changes relative to a base branch
codex review --commit SHA   # changes introduced by a commit
```

See the [Codex CLI documentation](https://developers.openai.com/codex/cli/)
for installation and authentication details.

## Install the workflow

The supported installation is run from a checkout so the installer and all
bundled specialist skills are available together:

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
```

By default, skills are installed under:

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

For an auditable installation, inspect the checkout and the managed source map
before running the local installer:

```bash
sed -n '1,220p' scripts/install-all.sh
sed -n '1,160p' references/skill-map.md
bash scripts/install-all.sh
```

## Update an existing installation

Use `--update` to replace already-installed workflow skills:

```bash
bash scripts/install-all.sh --update
```

Without `--update`, an existing skill directory is reported as `skip` and is
left unchanged. With `--update`, the existing destination directory is removed
before the local bundled content is copied into place. Back up any local edits
before using this option.

## Choose another destination

Use `--dest PATH` when Codex uses a non-default skills directory:

```bash
bash scripts/install-all.sh --dest /path/to/codex/skills
```

`--dest` can be combined with `--update`.

## Verify the result

After the command completes, verify the reported destination contains the
expected skill folders and each folder contains `SKILL.md`:

```bash
SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort
```

The installer prints the number of installed and skipped skills. Restart Codex
after checking the output.

## Installation behavior and trust boundary

The installer copies only the configured paths from this checkout; it does not
access GitHub, install dependencies, or execute specialist scripts during
installation. Review changes to
[`references/skill-map.md`](../../references/skill-map.md) and
[`scripts/install-all.sh`](../../scripts/install-all.sh) before publishing or
using a new bundle mapping. Review changes under `skills/` as the source code
for the specialist skills themselves. Review migrated explanatory material
under [`docs/skills/`](../skills/) when changing a skill's documented behavior.
