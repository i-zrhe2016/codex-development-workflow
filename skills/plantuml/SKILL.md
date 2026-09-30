---
name: plantuml
description: Create, refactor, render, and review maintainable PlantUML diagrams for software architecture and engineering workflows. Use when architecture, runtime interaction, lifecycle, deployment, or another repository behavior is materially clearer as a diagram; when creating or editing .puml; when checking diagram readability or render drift; or when repo-documentation requires a PlantUML source/render pair. Optimize for focused scope, semantic relationships, Git-friendly diffs, and deterministic regeneration.
---

# PlantUML

Create diagrams that answer one engineering question quickly and remain maintainable as code.

## Workflow

1. Identify the audience and the single question the diagram must answer.
2. Choose the smallest useful view:
   - system boundaries and external actors -> system context;
   - services, deployables, data stores -> container/service architecture;
   - request, auth, async, failover, deploy, message flow -> sequence;
   - lifecycle -> state;
   - workflow or decision path -> activity;
   - runtime placement, hosts, regions, clusters, networks -> deployment;
   - internal service decomposition -> component, only when useful;
   - domain/data structure -> ERD or class.
3. Split mixed concerns instead of building a master diagram.
4. Inspect existing repository diagram conventions before changing dialect, aliases, includes, layout, or style.
5. Produce complete compilable PlantUML.
6. For repository changes, render and validate before claiming completion.

## Rules

- One diagram = one question.
- Prefer context -> container -> focused detail over one giant graph.
- Use static views for structure; sequence/state/activity for behavior.
- Preserve existing project dialect and includes unless change is necessary.
- Do not add C4-PlantUML or remote includes only for appearance.
- Use stable semantic aliases such as api_gateway, routing_service, config_db.
- Name nodes with nouns. Label important edges with meaningful verb phrases.
- Show cross-process protocol/technology only when it adds operational meaning.
- Minimize crossing arrows. Split by viewpoint before using layout hacks.
- Use color/style only for consistent semantic meaning.
- Prefer !theme plain or the repository shared theme for new diagrams.
- Keep rationale in ADR/docs, not long diagram notes.

## Sequence convention

Use request/command arrows for forward actions and dashed return arrows for responses unless the project already defines another convention. Use alt, opt, loop, and par only when they clarify real behavior.

## Repository integration

PlantUML is a capability skill, not a workflow stage.

- repo-documentation owns whether documentation needs a diagram, the canonical owner document, placement, naming, and lifecycle.
- plantuml owns diagram-type selection, .puml source quality, rendering, and semantic/readability validation.
- Architecture-changing code and its affected diagram source/render belong in the same PR.
- Never hand-edit a rendered SVG to hide a source problem.

For codex-development-workflow itself:

- preserve existing diagram locations unless deliberately migrating the owning documentation;
- keep .puml and same-basename .svg synchronized when required by the documentation standard;
- run bash scripts/render-diagrams.sh render to regenerate diagrams;
- run bash scripts/render-diagrams.sh --check to detect render drift;
- public Kroki is for non-sensitive source only; use an approved local/private endpoint for sensitive or unreleased architecture.

If rendering cannot be performed safely or the renderer is unavailable, keep the valid .puml source and report the render as unverified/unrendered. Never fabricate a render.

## Output behavior

For chat-only requests, return the complete PlantUML source first and keep explanation minimal.

For repository changes:

- preserve aliases, includes, style, and placement when reasonable;
- minimize source churn so Git diffs remain reviewable;
- validate renderer success and visual readability;
- report changed source/render files, validation command/result, and unresolved limitations.

## Review checklist

Before finalizing, verify:

- title and scope are clear;
- one question is answered;
- abstraction levels are not mixed without reason;
- important relationships have direction and meaningful labels;
- protocols appear where operationally relevant;
- main structure or flow is obvious within seconds;
- avoidable crossings and duplicate edges are removed;
- styling semantics are consistent;
- source is deterministic and suitable for Git review.
