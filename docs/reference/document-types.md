# Document Types and Canonical Owners

Each document type owns a different kind of fact.

## Types

| Type | Directory | Records | Does not record | Status values |
|---|---|---|---|---|
| Architecture | `docs/architecture/` | what exists and how the parts connect | why an option was chosen | Draft, Active, Deprecated, Superseded |
| ADR | `docs/adr/` | one significant decision, alternatives, consequences | implementation detail | Proposed, Accepted, Deprecated, Superseded |
| Guide | `docs/guides/` | how a developer completes a task | exact value tables | Draft, Active, Deprecated, Superseded |
| Runbook | `docs/runbooks/` | how to operate, verify, and recover | design rationale | Draft, Active, Deprecated, Superseded |
| Reference | `docs/reference/` | exact facts: options, defaults, endpoints, commands | tutorials and rationale | Draft, Active, Deprecated, Superseded |
| State | `docs/Repo_Current_State.md` | what is true now | history, plans, architecture detail | governed by `AGENTS.md` |

`docs/Repo_Current_State.md` is the State exception: it keeps `Last verified` and follows the state contract in `AGENTS.md`.

## Canonical owner routing

| Fact | Owner |
|---|---|
| component relationships and boundaries | Architecture |
| why a technology or approach was chosen | ADR |
| exact configuration keys, defaults, constraints | Reference |
| recovery or rollback procedure | Runbook |
| local setup/run/debug procedure | Guide |
| what is implemented right now | `docs/Repo_Current_State.md` |
| planned/in-progress work | GitHub Issue |
| when something changed | Git |

The documentation router is an index, not a content owner. Link instead of duplicating facts.
