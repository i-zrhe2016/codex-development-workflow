# Document Templates

Use the matching `Type`; remove inapplicable/empty sections.

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

Record existing relationships/boundaries; rationale belongs in ADRs.

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

One decision per `docs/adr/NNNN-kebab-case.md`; later decisions require new ADRs
and supersede the old, never rewrite accepted records.

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

Include operation, success verification, failure handling and rollback.

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

Exact, verifiable facts before explanation.

## Diagrams

Under the illustrated section, embed the image and link editable source:

```markdown
![<what the diagram shows>](diagrams/<name>.svg)

Source: [`diagrams/<name>.puml`](diagrams/<name>.puml)
```

If unrendered, link source instead of a missing image and say so:

```markdown
Diagram (not yet rendered): [`diagrams/<name>.puml`](diagrams/<name>.puml)
```

Alt text states the fact, not filename, so it is useful without the image. Paths
are document-relative for GitHub/local rendering. Follow
[placement/naming](doc-file-standard.md) for the owner's `diagrams/` directory;
never paste PlantUML source into prose.

## State

`docs/Repo_Current_State.md` follows `repo-current-state`, not this file.
