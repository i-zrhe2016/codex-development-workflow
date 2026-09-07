# Architecture Overview

## Scope

This repository packages a Codex development-workflow orchestrator and its specialist skills. The orchestrator owns routing and quality gates; specialist procedures remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Classifies task complexity, coordinates TDD ticket loops, review escalation, and completion gates. |
| `scripts/install-all.sh` | Installs the orchestrator and mapped specialist skills. |
| `references/skill-map.md` | Maps each skill to its GitHub source and Codex destination. |
| Specialist skills | Own repository context, ticket generation, testing, state reconciliation, redaction, and publication procedures. |

## Development process

![Codex Development Workflow development process](../diagrams/architecture.svg)

Editable source: [`architecture.puml`](../diagrams/architecture.puml).

### Adaptive entry paths

- **Tiny:** implement and run relevant tests.
- **Normal:** make a minimal plan, implement, and run relevant tests.
- **Complex:** understand the repository, make a minimal design, use `plan-to-ticket`, then execute dependency-ready tickets through the TDD loop.

### TDD ticket loop

`Ticket -> function checklist/test cases -> RED when meaningful -> minimum implementation -> GREEN`

Tests are the normal inner-loop feedback mechanism. A failed test does not automatically trigger code review: diagnose and fix clear failures directly. Escalate to targeted `codex review` for repeated/unexplained failures, unclear root cause, high-risk changes, or architecture/design conflicts. If assumptions are wrong, re-plan or split the ticket instead of expanding scope.

After all tickets are GREEN, run integration/regression tests for the complete change set.

### Final gates

`Integration tests -> Repo State/Docs if needed -> Output classification -> Redaction if needed -> Final review -> Commit/Push`

The final review uses the Codex CLI built-in `codex review`. Fix blocking findings, rerun affected tests, and repeat review when fixes materially change the reviewed behavior.

### Sensitive-output gate

Classify the complete output set before staging/commit and before every sharing, export, upload, or publication boundary. Include source files, documentation, logs, configs, images, screenshots, exports, filenames, and metadata.

If no potentially sensitive surface is in scope, record the inspected scope and skip reason. Otherwise invoke `data-document-redaction`. Only a `pass` report advances; `needs_review` and `blocked` stop the boundary transition.

## Installation flow

1. Run `scripts/install-all.sh`.
2. The installer clones each mapped GitHub repository.
3. It copies the configured skill path into `${CODEX_HOME:-$HOME/.codex}/skills` or `--dest PATH`.
4. Existing skills are skipped unless `--update` is used.
5. Restart Codex to discover installed skills.

The installer and [`references/skill-map.md`](../../references/skill-map.md) must remain aligned.

## Boundaries

- The orchestrator defines routing and gates; specialist skills define detailed procedures.
- Ticket loops are conditional and reserved for work where decomposition reduces complexity.
- Tests drive the implementation loop; review is an escalation and final quality gate.
- Redaction is conditional, not a mandatory transformation of every artifact.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Installation currently follows repository default-branch contents rather than pinned commits.
