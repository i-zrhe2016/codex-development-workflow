# Codex Development Workflow

A gated Codex development workflow built from the author's GitHub skills:

`Plan -> Ticket -> Implement -> Test -> Review -> Repo State/Docs -> Classify outputs -> Redact when needed -> Commit/Push`

The repository contains the orchestrator skill, its installer, and the source
mapping for the specialist skills used by the workflow.

## Architecture

![Codex Development Workflow development process](docs/diagrams/architecture.svg)

See the [architecture overview](docs/architecture/overview.md) for the
development process, workflow gates, redaction gate, and package boundaries.

The [redaction workflow](docs/workflow/redaction.md) defines the pre-commit
classification, validation, report, and blocking rules for artifacts that may
contain sensitive information.

## One-command install

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

This installs all workflow skills into `${CODEX_HOME:-$HOME/.codex}/skills`.

Update existing installations:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Restart Codex after installation.

## Installed skills

- `codex-development-workflow`
- `context-efficiency`
- `plan-to-ticket`
- `frontend-click-test`
- `code-review`
- `repo-current-state`
- `data-document-redaction`
- `github-push-when-ready`

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Skill source map](references/skill-map.md)
