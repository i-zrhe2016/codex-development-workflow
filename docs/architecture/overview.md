# Architecture Overview

## Scope

This repository packages a single-agent Codex development-workflow orchestrator
and its specialist skills. The orchestrator owns stage routing and quality
gates; specialist procedures remain inside their own `SKILL.md` files.

## Components

| Component | Responsibility |
|---|---|
| `codex-development-workflow` | Classifies work, coordinates Plan/Slice execution, bounded verification, review, and delivery gates. |
| `plan-to-ticket` | Produces small, dependency-ordered Slices with explicit scope and acceptance criteria. |
| `test-workflow` | Runs the selected verification level and reports bounded evidence. |
| `repo-current-state` | Maintains the compact, verified recovery point for the repository. |
| `context-efficiency` | Optional context-loading aid for large or unfamiliar repositories; not a workflow stage. |
| `scripts/install-all.sh` | Installs the root orchestrator and local specialist bundles. |
| `references/skill-map.md` | Maps each managed bundle to its local source and Codex destination. |
| Redaction / publication skills | Guard sensitive outputs and commit/push boundaries. |

No component orchestrates multiple agents, sub-agents, parallel implementations,
or agent handoffs.

## Development process

![Codex Development Workflow development process](../diagrams/architecture.svg)

Editable source: [`architecture.puml`](../diagrams/architecture.puml).

### Macro stages

```text
Requirement -> Classify -> Understand -> Plan -> Slice -> Execute
           -> Next Slice? -> Integration -> Self Review -> State / Docs
           -> Redaction -> Commit / Push
```

- Tiny work uses a concise plan and one implicit Slice.
- Normal work plans the relevant area and executes one or more Slices.
- Complex work uses `plan-to-ticket` for dependency-ordered Slices.
- Each Slice loads only the context needed for its own acceptance criteria.
- A wrong design assumption returns to Plan or causes a Slice split.

### Slice execution

```text
Acceptance criteria -> Test strategy -> Minimal change
                    -> Focused validation -> Fix / Refactor
                    -> Slice complete
```

Test-first is preferred for meaningful behavioral changes, bug fixes,
regressions, API behavior, core business logic, data processing, and high-risk
code. It is not forced for documentation, configuration, dependency updates,
styling, typo fixes, simple refactors, or exploratory work.

### Bounded verification

| Level | Purpose |
|---|---|
| `minimal` | Tiny and non-behavioral changes. |
| `focused` | Default evidence for one Slice. |
| `regression` | Bug fixes and cross-module risk. |
| `full` | High-risk or release verification. |

After the selected level passes, stop unless the acceptance criteria, failure
evidence, affected boundaries, release requirements, or the user justify an
escalation.

### Review and final gates

After all Slices pass their selected checks, run integration/regression tests
and perform one self-review of the integrated diff. Blocking findings require
affected test reruns and, when behavior materially changes, another review.

`Integration tests -> Self review -> Repo State/Docs if needed -> Output classification -> Redaction if needed -> Commit/Push`

Review uses the Codex CLI built-in `codex review`; it is a final quality gate,
not a replacement for tests, diagnostics, linting, or static analysis.

### Sensitive-output gate

Classify the complete output set before staging/commit and before every sharing,
export, upload, or publication boundary. Include source files, documentation,
logs, configs, images, screenshots, exports, filenames, and metadata.

If no potentially sensitive surface is in scope, record the inspected scope and
skip reason. Otherwise invoke `data-document-redaction`. Only a `pass` report
advances; `needs_review` and `blocked` stop the boundary transition.

## Installation flow

1. Obtain a checkout of this repository and run `scripts/install-all.sh`.
2. The installer validates each local `SKILL.md` and copies the configured bundle into `${CODEX_HOME:-$HOME/.codex}/skills` or `--dest PATH`.
3. Existing skills are skipped unless `--update` is used.
4. Restart Codex to discover installed skills.

The installer and [`references/skill-map.md`](../../references/skill-map.md)
must remain aligned.

## Boundaries

- The orchestrator defines stages and gates; specialist skills define detailed procedures.
- Slices are conditional for work where decomposition reduces complexity; a tiny request may remain one implicit Slice.
- Tests provide evidence inside a Slice; review is an integrated self-review and risk-based escalation gate.
- `Repo_Current_State.md` is the recovery point, not a session transcript or full backlog.
- Redaction is conditional, not a mandatory transformation of every artifact.
- The package does not own target-project source code, application data, or deployment infrastructure.
- Specialist skills are vendored under `skills/` and updated through this repository's normal review and version-control process.
