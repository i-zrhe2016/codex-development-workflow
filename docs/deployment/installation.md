# Installation and Update Guide

> Type: Guide
> Status: Active
> Scope: Installing, updating, and verifying this repository's skill bundles for Codex and Claude Code, and the host-specific configuration each host reads

## Prerequisites

The installer requires:

- Bash;
- `tar`; and
- a complete checkout of this repository.

Restart the host after installation so the new skill directories are
discovered.


## Install the workflow

The supported installation is run from a checkout so the installer and all
bundled specialist skills are available together:

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
```

Select the host with `--target`. Codex is the default:

| `--target` | Destination | Reads agent definitions from |
|---|---|---|
| `codex` (default) | `${CODEX_HOME:-$HOME/.codex}/skills` | `.codex/agents/` |
| `claude` | `$HOME/.claude/skills` | `.claude/agents/` |

```bash
bash scripts/install-all.sh --target claude
```

Both targets install the same fourteen managed bundles under the bare skill name; the
Claude target omits the Codex-only `agents/openai.yaml` metadata, so the two
installations are not byte-for-byte identical. The destination root and that
metadata are the only differences. `--dest PATH` overrides either destination.

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
bash scripts/install-all.sh --update                  # Codex destination
bash scripts/install-all.sh --target claude --update  # Claude Code destination
```

`--update` acts on the destination selected by `--target` (or `--dest`), so an
update without `--target` always targets the Codex default. Repeat the target
you installed with.

Without `--update`, an existing skill directory is reported as `skip` and is
left unchanged. With `--update`, an existing destination is replaced only when
it carries the matching marker written by this installer; an unmarked path is
preserved and reported as `ownership unverified`. Retired skill destinations, including previously managed `context-efficiency`,
are removed under the same ownership check. Back up any local edits before
using this option.

![Installer overview: destination, ownership, and retirement decisions](../diagrams/installer-overview.svg)

Source: [`installer-overview.puml`](../diagrams/installer-overview.puml)

Detailed diagrams-as-code view:

![Installer decision flow: destination resolution, the ownership-marker check, and the install, skip, preserve, and remove outcomes](diagrams/installer-decision-flow.svg)

Source: [`diagrams/installer-decision-flow.puml`](diagrams/installer-decision-flow.puml)

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

Use `--dest PATH` when the host uses a non-default skills directory:

```bash
bash scripts/install-all.sh --target claude --dest /path/to/skills
```

`--dest` overrides the `--target` destination and can be combined with
`--update`.

## Verify the result

After the command completes, verify the destination the installer printed
contains the expected skill folders and each folder contains `SKILL.md`. Set
`SKILLS_DIR` to that printed location first:

```bash
SKILLS_DIR="$HOME/.claude/skills"   # or ${CODEX_HOME:-$HOME/.codex}/skills
find "$SKILLS_DIR" -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort
```

The installer prints the number of installed and skipped skills, the resolved
destination, and the host to restart.

### Diagram checks in pull requests

The diagram workflow checks only `.puml` sources added, copied, modified, or
renamed in a pull request. It validates their committed SVGs and any existing
same-name PNGs in a temporary tree, leaving the checkout read-only. Missing or
out-of-date renders fail the check. A manual `workflow_dispatch` still renders
the complete diagram set and commits regenerated outputs to the selected
branch.

### Installer regression checks

From the repository checkout, run:

```bash
python3 -m unittest discover -s scripts/tests -p 'test_install_all.py'
```

The tests use temporary destinations and cover target selection, destination
precedence, invalid arguments, skip/update behavior, ownership protection and
host-specific metadata. They compare every installed `SKILL.md` byte for byte
with its root or specialist source for Codex and Claude, both on initial install
and after replacing stale installed content with `--update`: 56 comparisons
across 14 bundles. They also preserve stale bundles on a skip and check that
user/project configuration and instructions stay unchanged through install,
skip and update. This verifies package contents and the installer's write
boundary; it does not prove model availability or execute Claude Code.

## Host-specific configuration

The installer copies managed skills only. Project-scoped runtime configuration
is not installed into another repository, and each host reads its own:

| File | Read by | Purpose |
|---|---|---|
| `.codex/config.toml` | Codex | Enables agents and sets project-local runtime defaults under [Codex model routing](#codex-model-routing). |
| `.codex/agents/*.toml` | Codex | Optional scoped Sol repair and independent-verification definitions under [Codex model routing](#codex-model-routing). |
| `agents/openai.yaml` (in each bundle) | Codex | Skill interface metadata. The Codex target requires it and installs it; the Claude target installs the bundle without it, because Claude Code never reads it. |

Codex may use built-in agents and project-defined agents under
`.codex/agents/` when present. Claude Code may use built-in agents and
project-defined agents under `.claude/agents/`. Claude Code does **not** read
`.codex/` and does not read `agents/openai.yaml`; Codex does **not** read
`.claude/agents/`. Neither host reads the other's project-scoped
configuration. Agent selection and escalation remain dynamic; the workflow does
not bind task classes to named agents.

Project-scoped runtime configuration stays in this checkout and is not installed
by `scripts/install-all.sh`.

### Codex model routing

The portable worker defaults, escalation triggers, precedence and dispatch
requirements have one canonical owner:
[`codex-development-workflow`'s model routing policy](../../SKILL.md#codex-worker-model-routing).
The installer already copies that root `SKILL.md`. Root and direct
develop/verify/test coordinators read the discovered root Skill through the
host catalog's location/access mechanism, so arbitrary projects need neither
this checkout nor this repository-only guide. The stages link to that policy
at runtime rather than carrying copies of its model table. Each stage is
associated with the root in its active installation, including project-scoped
`.agents/skills` installations; duplicate global/project catalog names do not
change that association. The canonical policy defines explicit-path priority
and actionable missing/ambiguous/stale-policy handling.

Install or update the complete bundle and start a new host session for discovery.
A skip preserves the installed version, including its policy; an ownership
unverified destination is also preserved. Check the installer output and
installed `SKILL.md` before assuming the new policy is active. A session that
has already loaded a Skill is not evidence that an update changed its guidance.

This guide owns the separate, repository-local configuration. In this checkout,
[`.codex/config.toml`](../../.codex/config.toml) enables agents and sets no
concurrency ceiling. Execution follows actual host capacity, with no project-set
upper cap or total/lifetime agent quota. The optional Sol repair and verifier
roles support the canonical policy's restricted repair trigger and independent
acceptance checks; configuration does not count failed repair rounds or switch
models automatically. The installed policy leaves the main agent's model,
provider and permissions unchanged and explicitly selects each dispatched
worker's model and effort. Explicit target-project routing applies as defined
by that canonical policy.

Standalone agent files require `name`, `description` and
`developer_instructions`. A selected named role's effective configuration must
be checked before dispatch, as required by the portable policy; explicit
dispatch settings do not require exploring unrelated/global model defaults. See the
[official subagent schema and precedence](https://learn.chatgpt.com/docs/agent-configuration/subagents).
The local custom roles serve only their described triggers.

The verifier sets `sandbox_mode = "read-only"` and explicitly forbids repository
edits except caches and temporary evidence. Live parent permission overrides,
including `--yolo`, can supersede its sandbox default, so its no-write
instructions still apply. See [official subagent permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Root model and effort defaults are supported [configuration keys](https://learn.chatgpt.com/docs/config-file/config-reference).
Session overrides can supersede coordinator defaults. Configuration applies to
new sessions; editing these files does not change the current conversation's
model mid-turn. Project-local files and instructions stay in this checkout;
only Skill guidance is copied into the destination. Config parsing, discovery,
offline catalog checks and a proposed dispatch do not prove account availability
or successful inference. Runtime evidence must identify requested versus
effective settings and distinguish a refusal from successful execution.

### Project instructions for each host

The delegation policy is owned by [`AGENTS.md`](../../AGENTS.md), and the two
hosts reach it differently:

- **Codex** reads `AGENTS.md` directly as its project instruction file.
- **Claude Code** reads `AGENTS.md` as project instructions only when no
  `CLAUDE.md` exists in the working directory or above it (v2.1.277+). This
  repository intentionally versions `AGENTS.md` and no `CLAUDE.md`, so the
  fallback applies here.

When a target project already has its own `CLAUDE.md`, Claude Code will not fall
back to that project's `AGENTS.md`. Link the project's authoritative delegation
and context policy from `CLAUDE.md` when that policy lives in `AGENTS.md`;
avoid maintaining a second copy. Installed root/develop/verify/test Skills
retain the minimum worker/context rules when a target has no `AGENTS.md`.

## Installation behavior and trust boundary

The installer copies only the configured paths from this checkout; it does not
access GitHub, install dependencies, or execute specialist scripts during
installation. Review changes to
[`references/skill-map.md`](../../references/skill-map.md) and
[`scripts/install-all.sh`](../../scripts/install-all.sh) before publishing or
using a new bundle mapping. Review changes under `skills/` as the source code
for the specialist skills themselves. Review migrated explanatory material
under [`docs/skills/`](../skills/) when changing a skill's documented behavior.
