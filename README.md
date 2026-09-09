# Codex Development Workflow

An adaptive, main-agent-led Codex development workflow with optional bounded
delegation and all required specialist skills managed in this repository.

```text
Requirement
  -> Understand repo
  -> Plan
  -> Slice / Ticket if needed
  -> Create branch
  -> Implement
  -> Test
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> Automatic Review
  -> Fix / Test / Redaction / Commit / Push / Review loop when blocked
  -> Merge PR
  -> Delete branch
  -> Update main
  -> Close Ticket
  -> Update State / Docs
  -> Deploy if needed
```

The macro workflow controls architecture and scope. If requirements span
multiple behaviors, define behavior Tickets first and then split each Ticket
into Slices. A single-behavior request may use one Slice without a Ticket, but
every change still uses a feature branch and the same PR gate. Each Slice
carries its own acceptance criteria, relevant context, test strategy, and
validation command.
Ticketed work keeps its implementation, tests, and related documentation on one
branch created from the updated default branch; the Ticket Issue records the
exact branch and base branch. Ticket dependencies remain separate from Slice
dependencies, and the PR head and base must match the Ticket metadata.
Test level may vary with risk, but delivery does not: Docs, Code, Tests,
Config, Refactor, Bugfix, Feature, Dependency, and CI/CD changes all require a
branch, commit, push, PR, automatic review, and merge. Blocking review findings
start a loop of fix, test, redaction when applicable, commit, push, and automatic
review again; the agent does not stop for confirmation.

Verification is bounded by an explicit level (`minimal`, `focused`,
`regression`, or `full`). The default is focused validation, and a passing
level stops the test expansion unless evidence or an explicit requirement
justifies escalation. The main agent owns requirements, architecture,
decomposition, integration, and final judgment; bounded exploration, Slice
implementation, and testing may be delegated when useful. Automatic Review
starts after the PR is opened or updated, without waiting for user confirmation.

## Optional project-scoped delegation

The project configuration keeps multi-agent support deliberately small:

- `.codex/config.toml` enables subagents and caps concurrent spawned-agent
  threads at three, excluding the main thread.
- `.codex/agents/reviewer.toml` defines an optional supplemental read-only
  reviewer; Automatic Review is always the built-in `codex review` command.

The built-in `explorer` and `worker` roles cover read-heavy exploration and
isolated implementation Slices. The delegation gate remains optional; keep
dependent, overlapping, or shared-interface work sequential.

## Architecture

![Codex Development Workflow development process](docs/diagrams/architecture.svg)

See the [architecture overview](docs/architecture/overview.md) for the unified
branch/PR lifecycle, Ticket/Slice decomposition, bounded verification, automatic
review loop, recovery state, redaction, and package boundaries.

## Install from this repository

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
```

The installer copies the local bundles under `skills/`; it does not clone
specialist repositories. This installs all workflow skills into
`${CODEX_HOME:-$HOME/.codex}/skills`.

Update existing installations:

```bash
bash scripts/install-all.sh --update
```

Restart Codex after installation.

## Installed skills

- `codex-development-workflow`
- `context-efficiency`
- `plan-to-ticket`
- `test-workflow`
- `repo-current-state`
- `data-document-redaction`
- `github-push-when-ready`
- `auto-deploy`

`plan-to-ticket` persists every generated plan and Ticket to GitHub Issues
before implementation branches start. GitHub Issues are the sole durable
Ticket authority; chat output and `Repo_Current_State.md` provide links and
recovery context, not a parallel backlog. A Ticket is optional for a single
behavior Slice, but the branch/PR gate is not optional.

## Skill documentation

Runtime skill sources live under `skills/` and are installed by
[`scripts/install-all.sh`](scripts/install-all.sh). Specialist documentation
is grouped under
[`docs/skills/`](docs/skills/); operational references remain beside the
relevant bundle.

| Skill | Runtime source | Documentation |
|---|---|---|
| `codex-development-workflow` | [`SKILL.md`](SKILL.md) | [Workflow usage](docs/workflow/usage.md) · [Architecture](docs/architecture/overview.md) |
| `context-efficiency` | [`skills/context-efficiency/`](skills/context-efficiency/) | [Skill documentation](docs/skills/context-efficiency/README.md) |
| `plan-to-ticket` | [`skills/plan-to-ticket/`](skills/plan-to-ticket/) | [Skill README](docs/skills/plan-to-ticket/README.md) · [Architecture](docs/skills/plan-to-ticket/architecture.md) |
| `test-workflow` | [`skills/test-workflow/`](skills/test-workflow/) | [Skill README](docs/skills/test-workflow/README.md) · [Architecture](docs/skills/test-workflow/architecture.md) · [Usage](docs/skills/test-workflow/usage.md) |
| `repo-current-state` | [`skills/repo-current-state/`](skills/repo-current-state/) | [Skill README](docs/skills/repo-current-state/README.md) · [Architecture](docs/skills/repo-current-state/architecture.md) |
| `data-document-redaction` | [`skills/data-document-redaction/`](skills/data-document-redaction/) | [Skill documentation](docs/skills/data-document-redaction/README.md) · [References](skills/data-document-redaction/references/) |
| `github-push-when-ready` | [`skills/github-push-when-ready/`](skills/github-push-when-ready/) | [Skill documentation](docs/skills/github-push-when-ready/README.md) |
| `auto-deploy` | [`skills/auto-deploy/`](skills/auto-deploy/) | [Skill documentation](docs/skills/auto-deploy/README.md) |

Automatic Review is the built-in `codex review` command. Run it after the PR is
created or updated and before merge, without waiting for user confirmation. If
findings block merge, fix them and repeat the Test -> Redaction (if applicable)
-> Commit -> Push -> Automatic Review loop. The project-scoped `reviewer` is
optional supplemental analysis and never replaces `codex review`.

```bash
codex review --base main
```

To run the optional supplemental project reviewer, start an interactive Codex
session from this project root and enter:

```text
Use the project-scoped `reviewer` subagent to inspect the current PR diff and
branch boundary. Return only actionable supplemental findings with file
references.
```

Use `--base BRANCH` or `--commit SHA` when a specific comparison is required.

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Managed skill source map](references/skill-map.md)
