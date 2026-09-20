# Document Types and Canonical Owners

Each document type owns a different kind of fact. Choose the type first; the
type decides the directory, the allowed status values, and the template.

## Types

| Type | Directory | Records | Does not record | Status values |
|---|---|---|---|---|
| Architecture | `docs/architecture/` | what exists and how the parts connect | why an option was chosen | Draft, Active, Deprecated, Superseded |
| ADR | `docs/adr/` | one significant decision, its alternatives, and its consequences | implementation detail | Proposed, Accepted, Deprecated, Superseded |
| Guide | `docs/guides/` | how a developer completes a task | exact value tables | Draft, Active, Deprecated, Superseded |
| Runbook | `docs/runbooks/` | how to operate, verify, and recover a system | design rationale | Draft, Active, Deprecated, Superseded |
| Reference | `docs/reference/` | exact facts: options, defaults, endpoints, commands | tutorials and rationale | Draft, Active, Deprecated, Superseded |
| State | `docs/Repo_Current_State.md` | what is true now | history, plans, architecture detail | owned by `repo-current-state` |

`State` is the one type that does not use this Skill's file header.
`docs/Repo_Current_State.md` keeps its `Last verified` field and is maintained by
`repo-current-state`; this Skill only routes to it.

## Canonical owner routing

| Fact | Owner |
|---|---|
| component relationships and boundaries | Architecture |
| why a technology or approach was chosen | ADR |
| exact configuration keys, defaults, and constraints | Reference |
| recovery or rollback procedure for a component | Runbook |
| how to set up, run, or debug the project locally | Guide |
| what is implemented right now | `docs/Repo_Current_State.md` |
| what will be done next | GitHub Issue |
| when something changed | Git |

## Placement

Suggested structure. Create only the directories that have content; an empty
directory is not documentation.

```text
docs/
├── README.md
├── architecture/
├── adr/
├── guides/
├── runbooks/
├── reference/
└── Repo_Current_State.md
```

## Boundaries between types

- Architecture says what is; an ADR says why. Do not explain alternatives or
  rejected options in an architecture document.
- A Guide teaches a task end to end; a Reference lists exact values. Link to the
  reference instead of copying tables into the guide.
- A Runbook is a Guide for operations and must state verification, failure
  handling, and rollback.
- `Repo_Current_State.md` summarizes. It never becomes the detailed
  architecture, decision, or procedure document.
- `docs/README.md` is an index, not a content document. It carries links and
  grouping, never the facts themselves.
- A choice that affects no architecture, interface, deployment, or operation is
  an implementation detail. Do not write an ADR for it.
