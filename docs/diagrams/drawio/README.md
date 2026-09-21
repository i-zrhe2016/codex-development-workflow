# Editable Draw.io Overview Diagrams

This directory contains the curated, human-facing diagram layer for the
repository. Each overview is stored as uncompressed editable `.drawio` XML and
paired with a same-basename SVG preview.

Detailed workflow loops and diagrams-as-code remain in the repository's
PlantUML sources. Use the Draw.io overview when information hierarchy and
presentation matter; use the linked PlantUML view when exact low-level flow and
textual diffability matter more.

| View | Purpose | Detailed diagram |
|---|---|---|
| [workflow-overview.svg](workflow-overview.svg) | Stage routing and the full orchestration | [../architecture.puml](../architecture.puml) |
| [components-overview.svg](components-overview.svg) | Stage workflows, capability skills, and boundaries | [../components.puml](../components.puml) |
| [plan-ticket-slice.svg](plan-ticket-slice.svg) | Persisted Plan → Ticket → Slice hierarchy | [../ticket-lifecycle.puml](../ticket-lifecycle.puml) |
| [test-quality-gate.svg](test-quality-gate.svg) | Risk-aware verification overview | [../../skills/test-workflow/diagrams/test-workflow-flow.puml](../../skills/test-workflow/diagrams/test-workflow-flow.puml) |
| [docs-publication-flow.svg](docs-publication-flow.svg) | `publish-workflow` documentation and publication | [../../skills/repo-documentation/diagrams/repo-documentation-flow.puml](../../skills/repo-documentation/diagrams/repo-documentation-flow.puml) |
| [installer-overview.svg](installer-overview.svg) | Installation ownership and retirement decisions | [../../deployment/diagrams/installer-decision-flow.puml](../../deployment/diagrams/installer-decision-flow.puml) |

## Maintenance contract

- Keep stable semantic IDs in the `.drawio` source.
- Do not use reserved IDs `0` or `1` for authored nodes or edges.
- Every edge carries relative `mxGeometry` and valid source/target IDs.
- Keep the source uncompressed and pair it with a same-basename SVG.
- Run repository contract tests after edits.
- Visually inspect overlap, clipping, crossings, edge-through-node routing, and
  label readability before publication.
- Run `python -m unittest discover -s scripts/tests -p 'test_*.py'` before
  publication; the repository contract tests parse every overview source and
  verify SVG pairing plus documentation reachability.
