# Installation and Update Guide

## Prerequisites

The installer requires:

- Bash;
- Git;
- `mktemp`;
- `tar`; and
- network access to GitHub.

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

The supported one-command installation is:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

By default, skills are installed under:

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

For an auditable installation, download the script first, inspect it, and then
run it locally:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh -o /tmp/codex-workflow-install.sh
bash /tmp/codex-workflow-install.sh
```

The temporary path above is only an example; use a path appropriate for the
local environment and remove it after review if it is no longer needed.

## Update an existing installation

Use `--update` to replace already-installed workflow skills:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Without `--update`, an existing skill directory is reported as `skip` and is
left unchanged. With `--update`, the existing destination directory is removed
before the newly cloned content is copied into place. Back up any local edits
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

The installer clones the configured GitHub repositories with `--depth 1` and
copies the requested paths; it does not perform commit pinning, signature
verification, or dependency installation. Review changes to
[`references/skill-map.md`](../../references/skill-map.md) and
[`scripts/install-all.sh`](../../scripts/install-all.sh) before publishing or
using a new source mapping.
