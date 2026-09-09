# Codex Development Workflow

An adaptive, main-agent-led Codex development workflow with optional bounded
delegation and all required specialist skills managed in this repository.

```text
Requirement -> Classify -> Understand -> Plan -> Ticket(s) if needed
           -> Slice(s) per Ticket
           -> Persist plan/tickets to GitHub Issues -> Delegate if useful
           -> Create/resume ticket branch
           -> Execute/Test -> Next Slice? -> Integration
           -> State / Docs
           -> Redaction if needed -> Commit / Push -> Open PR
           -> Review -> Fix findings / Re-test -> Merge -> Close ticket
           -> Optional Deploy / Verify / Rollback
```

The macro workflow controls architecture and scope. For complex or
multi-behavior requirements, define behavior Tickets first and then split each
Ticket into Slices. Each Slice carries its own
acceptance criteria, relevant context, test strategy, and validation command.
Each ticket keeps its implementation, tests, and related documentation on one
branch created from the updated default branch; ticket review happens before
that ticket is merged, after its PR is opened. Complete ticket checks before
committing and pushing, then use one PR-stage review, fix findings, re-test, and
merge before closing the ticket. Each ticket Issue records the exact branch and
base branch; the PR head and base must match those Issue fields.
TDD is used inside a Slice when the change is behavioral and a meaningful
failing test provides useful evidence; it is not forced on documentation,
configuration, styling, dependency, typo, or exploratory work.

Verification is bounded by an explicit level (`minimal`, `focused`,
`regression`, or `full`). The default is focused validation, and a passing
level stops the test expansion unless evidence or an explicit requirement
justifies escalation. The main agent owns requirements, architecture,
decomposition, integration, and final judgment; bounded exploration, Slice
implementation, and testing may be delegated when useful. The single review
occurs after the PR is opened.

## Optional project-scoped delegation

The project configuration keeps multi-agent support deliberately small:

- `.codex/config.toml` enables subagents and caps concurrent spawned-agent
  threads at three, excluding the main thread.
- `.codex/agents/reviewer.toml` defines a read-only reviewer for the single
  PR-stage review.

The built-in `explorer` and `worker` roles cover read-heavy exploration and
isolated implementation Slices. The delegation gate remains optional; keep
dependent, overlapping, or shared-interface work sequential.

## Architecture

![Codex Development Workflow development process](docs/diagrams/architecture.svg)

See the [architecture overview](docs/architecture/overview.md) for task
classification, Slice execution, bounded verification, review escalation,
recovery state, redaction, and package boundaries.

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

`plan-to-ticket` persists every generated plan and ticket to GitHub Issues
before implementation branches start. GitHub Issues are the sole durable
ticket authority; chat output and `Repo_Current_State.md` provide links and
recovery context, not a parallel backlog.

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

The single review stage happens after the PR is opened and before it is merged.
Choose one path: the built-in `codex review` command or the project-scoped
`reviewer` for an independent read-only check. They are alternatives, not
sequential review gates.

```bash
codex review --base main
```

To use the project reviewer as the single PR-stage review, start an interactive
Codex session from this project root and enter:

```text
Use the project-scoped `reviewer` subagent to inspect the current PR diff and
branch boundary. Wait for its read-only result and return only actionable
findings with file references.
```

Use `--base BRANCH` or `--commit SHA` when a specific comparison is required.

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Managed skill source map](references/skill-map.md)
