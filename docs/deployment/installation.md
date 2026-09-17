# Installation and Update Guide

## Prerequisites

The installer requires:

- Bash;
- `tar`; and
- a complete checkout of this repository.

Codex should be restarted after installation so the new skill directories are
discovered.

## Configure pull-request review

The `pr-review` Skill is the single pull-request merge gate. It uses Alibaba
Open Code Review's `ocr review` command through its bundled recoverable runner.
Install and configure Open Code Review before using it:

```bash
npm install --global @alibaba-group/open-code-review
ocr config provider
ocr config model
```

From the project root, invoke `pr-review` immediately after each PR creation or
update. Its runtime instructions select the actual base and review scope:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/<base>
```

Only `PASS` permits merge. Blocking findings return to the affected
test/redaction/commit/push loop before `pr-review` runs again. See the
[`pr-review` Skill](../../skills/pr-review/SKILL.md) for the authoritative
review policy and the [runner reference](../../skills/pr-review/references/review-execution.md)
for execution recovery details.

See the [Open Code Review repository](https://github.com/alibaba/open-code-review)
for installation, configuration, and CLI details.

## Optional supplemental review

The project-scoped `.codex/agents/reviewer.toml` is outside the default PR path.
Use it only when an explicitly high-risk change needs a second independent
read-only review; it never replaces `pr-review`.

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
left unchanged. With `--update`, an existing destination is replaced only when
it carries the matching marker written by this installer; an unmarked path is
preserved and reported as `ownership unverified`. Retired skill destinations
are removed under the same ownership check. Back up any local edits before
using this option.

The marker is stored as the hidden file
`.codex-development-workflow-managed` inside each installed bundle. This
prevents an update from recursively deleting an unrelated skill that happens
to use a retired or current workflow name. Installations created before this
marker existed remain untouched by the default update. To migrate one of those
installations, explicitly opt in:

```bash
bash scripts/install-all.sh --update --adopt-legacy
```

This one-time adoption moves every unmarked configured destination to a hidden,
recoverable backup under the skills directory before updating or pruning it;
the command requires `--update`. Review the printed backup path before removing
it manually.

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

## Project-scoped subagent configuration

This checkout also contains the optional project-scoped Codex configuration:

- `.codex/config.toml` enables subagents and caps concurrent spawned-agent
  threads at three, excluding the main thread.
- `.codex/agents/reviewer.toml` defines an optional supplemental reviewer for
  explicitly high-risk changes; it is not part of the default PR path.

The installer copies managed skills only; it does not install or overwrite
project-scoped `.codex/` files in another repository. Copy or adapt these files
there only when that project has the same delegation boundaries and review
needs.

## Installation behavior and trust boundary

The installer copies only the configured paths from this checkout; it does not
access GitHub, install dependencies, or execute specialist scripts during
installation. Review changes to
[`references/skill-map.md`](../../references/skill-map.md) and
[`scripts/install-all.sh`](../../scripts/install-all.sh) before publishing or
using a new bundle mapping. Review changes under `skills/` as the source code
for the specialist skills themselves. Review migrated explanatory material
under [`docs/skills/`](../skills/) when changing a skill's documented behavior.
