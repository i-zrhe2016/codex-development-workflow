# Document Templates

Use the template that matches the document `Type`. Remove sections that do not
apply; do not leave empty headings.

## Architecture

```markdown
# <Title>

> Type: Architecture
> Status: Active
> Scope: <components and boundaries this document owns>

## Purpose
## Context
## Components
## Data / Control Flow
## Interfaces
## Constraints
## Related Decisions
## Related Documentation
```

Record what exists, how the parts connect, and where the boundaries are. Leave
rationale to the ADR.

## ADR

```markdown
# ADR-0001: <Decision>

> Type: ADR
> Status: Accepted
> Scope: <decision and the area it constrains>

## Context
## Decision
## Alternatives Considered
## Consequences
## Related Documentation
```

One decision per record, in `docs/adr/NNNN-kebab-case.md`. Never edit an
accepted ADR to describe a later decision; write a new ADR and mark the old one
`Superseded`.

## Guide

```markdown
# <Task>

> Type: Guide
> Status: Active
> Scope: <task this guide owns>

## Goal
## Prerequisites
## Steps
## Verification
## Troubleshooting
```

## Runbook

```markdown
# <Operation>

> Type: Runbook
> Status: Active
> Scope: <system and operation this runbook owns>

## Purpose
## Preconditions
## Procedure
## Verification
## Failure Handling
## Rollback
## Related Documentation
```

A runbook answers four questions: how to perform the operation, how to know it
succeeded, what to do when it fails, and how to undo it.

## Reference

```markdown
# <Surface> Reference

> Type: Reference
> Status: Active
> Scope: <surface this reference owns>

## Overview
## Configuration
## Defaults
## Constraints
## Examples
## Related Documentation
```

Facts before explanation. Keep values exact and verifiable.

## Diagrams

Embed a diagram directly under the section it illustrates, using the image as
the figure and the `.puml` source as the link:

```markdown
![<what the diagram shows>](diagrams/<name>.svg)

Source: [`diagrams/<name>.puml`](diagrams/<name>.puml)
```

When the diagram could not be rendered, link the source instead of the image and
say so, so no reader mistakes a missing figure for a broken link:

```markdown
Diagram (not yet rendered): [`diagrams/<name>.puml`](diagrams/<name>.puml)
```

- Write alt text that states the fact the diagram carries, not the file name. A
  reader who cannot see the image must still get the point.
- Use a path relative to the document, so the image resolves on GitHub and in a
  local checkout alike.
- Keep the diagram in the document's own `diagrams/` directory; placement and
  naming are defined in `doc-file-standard.md`.
- Do not paste the PlantUML source into the document. The `.puml` file is the
  editable artifact; the document carries the image and the link.

## State

`docs/Repo_Current_State.md` follows `repo-current-state`, not this file.
