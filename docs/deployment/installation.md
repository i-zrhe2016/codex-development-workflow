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

Both targets install the same thirteen managed bundles under the bare skill name; the
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

### Installer regression checks

From the repository checkout, run:

```bash
python3 -m unittest discover -s scripts/tests -p 'test_install_all.py'
```

The tests use temporary destinations and cover target selection, destination
precedence, invalid arguments, skip/update behavior, ownership protection and
host-specific metadata. They compare every installed `SKILL.md` byte for byte
with its root or specialist source for Codex and Claude, both on initial install
and after replacing stale installed content with `--update`: 52 comparisons
across 13 bundles. This verifies package contents; it does not execute Claude
Code or publish a real GitHub PR.

## Host-specific configuration

The installer copies managed skills only. Project-scoped runtime configuration
is not installed into another repository, and each host reads its own:

| File | Read by | Purpose |
|---|---|---|
| `.codex/config.toml` | Codex | Sets coordinator and worker defaults and the concurrency ceiling under [Codex model routing](#codex-model-routing). |
| `.codex/agents/*.toml` | Codex | Optional scoped Sol implementation and independent verification definitions under [Codex model routing](#codex-model-routing). |
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

This section owns the project's model configuration and coordinator dispatch
policy. [`AGENTS.md`](../../AGENTS.md#who-chooses-the-subagent) requires the
coordinator to apply it before each dispatch.

| Scope | Required model | Reasoning effort | Configuration / selection |
|---|---|---|---|
| Main/coordinator | `gpt-6.1-sol` | `high` | Root `model` and `model_reasoning_effort` in [`.codex/config.toml`](../../.codex/config.toml), before `[agents]`. |
| Ordinary clear implementation or Ticket verification | `gpt-6-luna` | `high` | `[agents]` worker defaults; request these settings at dispatch. |
| Demanding scoped implementation | `gpt-6.1-sol` | `xhigh` | Explicit spawn settings or matching [`sol_escalation`](../../.codex/agents/sol-escalation.toml). |
| High-risk independent verification after development | `gpt-6.1-sol` | `high` | Explicit spawn settings or matching [`sol_verifier`](../../.codex/agents/sol-verifier.toml). |
| Final Plan/branch/PR acceptance after development | `gpt-6.1-sol` | `high` | Explicitly request Sol/high for one fresh independent verifier of the whole scope; the custom role is optional. |

Use Sol for API/schema changes, complex cross-module work, security/AuthZ
high-risk checks, or after **two failed repair rounds**. Use `xhigh` for
escalated implementation and `high` for verification. At dispatch, the
coordinator evaluates scope, risk and retained repair evidence, selects an
available capability matching the role, and explicitly requests the required
model and effort. Do not bind Explore/Coding/Test task classes to named agents.
If custom definitions are not exposed by the host, explicit spawn model and
reasoning settings are a valid alternative with the same scoped instructions.

Failures preserve verified checkpoints and prior evidence. Apply existing
[fresh replacements and role isolation](../../AGENTS.md#roles-and-ticket-ownership);
never reuse an implementation worker as its verifier or erase unexplained
flakiness through a passing retry. If the required model or effort is unsupported
or unavailable, report the actual condition and stop that dispatch; do not
silently fall back or change providers.

The TOML files do not detect repair failures or switch models automatically;
the coordinator applies this policy at dispatch. `[agents]` remains enabled,
with a concurrency ceiling of three, subject to effective host capacity and
safe execution waves.

Standalone agent files require `name`, `description` and
`developer_instructions`. Their model/effort fields override explicit spawn
settings; otherwise explicit spawn settings override `[agents]` defaults,
then parent values. See the [official subagent schema and precedence](https://learn.chatgpt.com/docs/agent-configuration/subagents).
The two custom roles serve only their described escalation/verification triggers.

The verifier sets `sandbox_mode = "read-only"` and explicitly forbids repository
edits except caches and temporary evidence. Live parent permission overrides,
including `--yolo`, can supersede its sandbox default, so its no-write
instructions still apply. See [official subagent permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents).

Root model and effort defaults are supported [configuration keys](https://learn.chatgpt.com/docs/config-file/config-reference).
Session overrides can supersede coordinator defaults. Configuration applies to
new sessions; editing these files does not change the current conversation's
model mid-turn. These project-local files and instructions are not installed
into target repositories. Config parsing and offline catalog checks do not
prove account availability or successful model execution.

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
