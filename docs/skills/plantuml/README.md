# PlantUML Skill

> Type: Reference
> Status: Active
> Scope: PlantUML diagram generation, rendering, review, and repository integration

Use PlantUML when an engineering concern is clearer as a diagram. Choose a view that answers one question: context for boundaries, component for decomposition, sequence for interactions, state for lifecycle, activity for decisions, deployment for runtime placement, or ERD/class for data structure.

Keep sources deterministic and reviewable, use meaningful node names and labeled edges, and preserve local style conventions. Avoid remote includes. Check rendered output for readability and keep the `.puml` source and same-basename `.svg` together.

The `repo-documentation` skill owns whether a diagram is needed and where it belongs. This skill owns diagram type, source quality, rendering, and visual review. The repository renderer is `scripts/render-diagrams.sh`; it uses public Kroki, so send only non-sensitive source.

Runtime guidance: [`skills/plantuml/SKILL.md`](../../../skills/plantuml/SKILL.md).
