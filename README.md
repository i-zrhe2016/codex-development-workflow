# Codex Development Workflow

An adaptive, test-driven Codex development workflow built from GitHub-hosted skills.

```text
Tiny:    Implement -> Test
Normal:  Plan -> Implement -> Test
Complex: Plan/Tickets -> TDD Ticket Loop -> Integration Test

All paths -> State/Docs if needed -> Redaction if needed -> Final Review -> Commit/Push
```

Complex tickets carry a function checklist, acceptance criteria, test cases, dependencies, and validation. Tests are the primary development feedback loop; targeted code review is used when failures are repeated/unexplained or risk is high, followed by one final review before commit/push.

## Architecture

![Codex Development Workflow development process](docs/diagrams/architecture.svg)

See the [architecture overview](docs/architecture/overview.md) for task classification, TDD Ticket Loops, review escalation, redaction, and package boundaries.

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
- `repo-current-state`
- `data-document-redaction`
- `github-push-when-ready`

Code review uses the Codex CLI built-in `codex review`; no separate review skill is required.

```bash
codex review --uncommitted
```

Use `--base BRANCH` or `--commit SHA` when a specific comparison is required.

## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Skill source map](references/skill-map.md)
