---
name: plantuml
description: "Create, refactor, render, and review PlantUML for architecture, runtime interactions, lifecycle, deployment, or workflows when diagrams clarify behavior. Use for .puml creation/edits, readability/render-drift checks, and repo-documentation source/render pairs; keep semantic, Git-friendly, deterministic diagrams."
---

# PlantUML

Answer one engineering question per diagram. Identify audience/question, then
choose the smallest view:

| Question | View |
|---|---|
| boundaries/external actors | system context |
| services/deployables/data stores | container/service architecture |
| request/auth/async/failover/deploy/message flow | sequence |
| lifecycle | state |
| workflow/decisions | activity |
| hosts/regions/clusters/networks/runtime placement | deployment |
| useful internal service decomposition | component |
| domain/data structure | ERD/class |

Prefer context -> container -> focused detail; split mixed concerns, not a master
graph. Static views describe structure; sequence/state/activity describe behavior.
Inspect repository conventions first; preserve dialect, aliases, includes,
layout, style, and placement unless a change is necessary.

## Source and review

Produce complete compilable, deterministic source with reviewable minimal churn.
Do not add C4-PlantUML or remote includes for appearance. Use stable semantic
aliases (e.g. `api_gateway`), noun nodes, and directed important edges labeled
with meaningful verbs. Show cross-process protocols/technology where operationally
useful. Split viewpoints before layout hacks; remove avoidable crossings and
duplicate edges. Color/style must carry consistent meaning; for new diagrams,
prefer `!theme plain` or the shared repository theme. Keep long notes/rationale
in ADRs/docs.

Sequences use forward request/command arrows and dashed response arrows unless
project conventions differ; `alt`, `opt`, `loop`, `par` must clarify real behavior.

Before finalizing, check clear title/scope, one answered question, justified
abstraction mixing only, meaningful direction/labels/protocols, immediately obvious
structure/flow, consistent styling, and deterministic Git-reviewable source.

## Integration and rendering

This is a capability, not a workflow stage. `repo-documentation` owns diagram
need, canonical document, placement, naming, and lifecycle; this skill owns type,
source quality, rendering, and semantic/readability validation. Architecture
code and affected source/render share a PR. Never hand-edit rendered SVG to hide
source problems.

For codex-development-workflow, preserve locations unless migrating the owner;
keep `.puml`/same-basename `.svg` synchronized where the documentation standard
requires it:

```bash
bash scripts/render-diagrams.sh render
bash scripts/render-diagrams.sh --check
```

The first regenerates renders; the second detects drift. Public Kroki accepts
only non-sensitive source; sensitive/unreleased architecture needs an approved
local/private endpoint. Render and verify renderer success and visual readability
before claiming repository completion. If unavailable or unsafe, retain valid
`.puml` and report unverified/unrendered; never fabricate a render.

## Output

Chat-only: complete PlantUML source first, minimal explanation. Repository work:
report changed source/render files, validation command/result and unresolved
limitations.
