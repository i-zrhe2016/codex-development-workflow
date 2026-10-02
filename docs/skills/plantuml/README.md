# PlantUML Skill

> Type: Reference
> Status: Active
> Scope: PlantUML diagram generation, rendering, review, and repository integration

PlantUML is a capability skill for diagrams-as-code. It is invoked when architecture, runtime flow, lifecycle, deployment, or another engineering concern is materially clearer as a diagram.

It is not a workflow stage. repo-documentation decides whether documentation needs a diagram and where the canonical source/render belong; plantuml owns diagram selection, PlantUML source quality, rendering, and readability validation.

Repository conventions:

- one diagram answers one question;
- static structure uses focused architecture views, while runtime behavior uses sequence/state/activity views;
- important relationships carry semantic labels;
- .puml source and same-basename SVG stay synchronized when required by the documentation standard;
- public Kroki is used only for non-sensitive diagrams;
- architecture-changing code and affected diagrams change in the same PR.

Runtime instructions: ../../../skills/plantuml/SKILL.md
