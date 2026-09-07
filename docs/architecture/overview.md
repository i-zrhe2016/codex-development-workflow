# Architecture Overview

## Scope

This repository packages a Codex development-workflow orchestrator and its specialist skills. It coordinates development gates and installs the required skills; specialist procedures remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Coordinates the end-to-end lifecycle and routes work to specialist skills. |
| `scripts/install-all.sh` | Installs the orchestrator and mapped specialist skills. |
| `references/skill-map.md` | Maps each skill to its GitHub source and Codex destination. |
| Specialist skills | Own planning, testing, review, repository-state, redaction, and publication procedures. |

## Development process

![Codex Development Workflow development process](../diagrams/architecture.svg)

Editable source: [`architecture.puml`](../diagrams/architecture.puml).

Main path:

`Context -> Plan/Ticket -> Implement -> Test -> Review -> Repo State/Docs -> Output classification -> Redaction gate -> Commit/Push`

Frontend browser verification is conditional. Test or review failures return to implementation.

### Sensitive-output gate

After verified state/docs are updated and before staging or committing, classify
the complete output set. Re-check before any separate sharing, export, upload,
or publication boundary. Include source files, documentation, logs, configs,
images, screenshots, exports, filenames, and metadata.

If no potentially sensitive surface is in scope, record the scope and skip
reason, then continue to `github-push-when-ready`.

If yes, invoke `data-document-redaction` and follow the [redaction workflow](../workflow/redaction.md).
The specialist owns detection, transformation, hidden-surface checks,
validation, and reporting. Only a `pass` report advances to
`github-push-when-ready`; `needs_review` and `blocked` stop the boundary
transition.

## Installation flow

1. Run `scripts/install-all.sh`.
2. The installer clones each mapped GitHub repository.
3. It copies the configured skill path into `${CODEX_HOME:-$HOME/.codex}/skills` or `--dest PATH`.
4. Existing skills are skipped unless `--update` is used.
5. Restart Codex to discover the installed skills.

The installer and [`references/skill-map.md`](../../references/skill-map.md) must remain aligned.

## Boundaries

- The orchestrator defines routing and gates; specialist skills define detailed procedures.
- Redaction is conditional, not a mandatory transformation of every artifact.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Installation requires GitHub access and currently follows repository default-branch contents rather than pinned commits.
