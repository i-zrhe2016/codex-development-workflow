# PlantUML Overview Diagrams

This index links the repository's shared overview diagrams. Each overview uses
an editable `.puml` canonical source and a generated same-basename SVG. Detailed
views retain their existing locations beside the documents they illustrate.

| View | Overview source | Purpose | Detailed source |
|---|---|---|---|
| [workflow-overview.svg](workflow-overview.svg) | [workflow-overview.puml](workflow-overview.puml) | Authorized full delivery and stage boundaries | [architecture.puml](../architecture/diagrams/architecture.puml) |
| [components-overview.svg](components-overview.svg) | [components-overview.puml](components-overview.puml) | Stage workflows, capability skills, and boundaries | [components.puml](../architecture/diagrams/components.puml) |
| [plan-ticket.svg](plan-ticket.svg) | [plan-ticket.puml](plan-ticket.puml) | Requirement → Plan → Ticket ownership and sizing | [ticket-lifecycle.puml](../architecture/diagrams/ticket-lifecycle.puml) |
| [test-quality-gate.svg](test-quality-gate.svg) | [test-quality-gate.puml](test-quality-gate.puml) | Risk-aware verification evidence | [test-workflow-flow.puml](../skills/test-workflow/diagrams/test-workflow-flow.puml) |
| [docs-publication-flow.svg](docs-publication-flow.svg) | [docs-publication-flow.puml](docs-publication-flow.puml) | Documentation and authorized publication | [repo-documentation-flow.puml](../skills/repo-documentation/diagrams/repo-documentation-flow.puml) |
| [installer-overview.svg](installer-overview.svg) | [installer-overview.puml](installer-overview.puml) | Installation ownership and retirement decisions | [installer-decision-flow.puml](../deployment/diagrams/installer-decision-flow.puml) |

## Maintenance

Follow the [diagram standard](../../skills/repo-documentation/references/doc-file-standard.md#diagrams)
for source, render and placement requirements. Regenerate and check renders:

```bash
bash scripts/render-diagrams.sh render
bash scripts/render-diagrams.sh --check
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
```

Before publication, visually inspect generated diagrams for overlap, clipping,
crossings, routing and label readability. Repository contract tests check
source/render pairing and documentation reachability.
