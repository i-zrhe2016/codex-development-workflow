# Codex Development Workflow

An adaptive, single-agent staged Codex development workflow with all required
specialist skills managed in this repository.

```text
Requirement -> Classify -> Understand -> Plan -> Slice -> Execute
           -> Next Slice? -> Integration -> Self Review -> State / Docs
           -> Redaction if needed -> Commit / Push
```

The macro workflow controls architecture and scope. Each Slice carries its own
acceptance criteria, relevant context, test strategy, and validation command.
TDD is used inside a Slice when the change is behavioral and a meaningful
failing test provides useful evidence; it is not forced on documentation,
configuration, styling, dependency, typo, or exploratory work.

Verification is bounded by an explicit level (`minimal`, `focused`,
`regression`, or `full`). The default is focused validation, and a passing
level stops the test expansion unless evidence or an explicit requirement
justifies escalation. The workflow uses one Codex agent and does not
orchestrate multi-agent or parallel implementation.

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

Review uses the Codex CLI built-in `codex review`; it is a final self-review of
the integrated diff, not a separate agent workflow.

```bash
codex review --uncommitted
```

Use `--base BRANCH` or `--commit SHA` when a specific comparison is required.

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Managed skill source map](references/skill-map.md)
