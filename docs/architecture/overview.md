# Zero-Skill Architecture

> Type: Architecture
> Status: Active
> Scope: Codex-native execution with repository contracts in AGENTS.md

## Core model

Codex is the execution engine. The repository does not package runtime Skills.

```text
Codex native capabilities
        |
        v
AGENTS.md repository-specific contracts
        |
        +--> scripts/redaction/       deterministic sensitive-data gate
        +--> scripts/publication/     deterministic publication guards
        +--> scripts/render-diagrams.sh
        |
        v
GitHub Issues / docs / GitHub PR
```

## Responsibility boundary

| Surface | Responsibility |
|---|---|
| Codex | planning, decomposition, architecture, implementation, verification, delegation, integration, Git/GitHub use, diagram authoring |
| AGENTS.md | repository-specific policy and durable contracts |
| scripts/redaction/ | staged sensitive-data detection |
| scripts/publication/ | publication readiness, identity, commit, push and hook checks |
| GitHub Issues | authoritative task records |
| docs/Repo_Current_State.md | compact verified repository-state snapshot |
| docs/reference/ | repository documentation standards |

No repository `SKILL.md` is allowed.

## Why

A Skill should not duplicate model-native ability. Requirements that are not model capabilities are more direct and cheaper as repository instructions or deterministic scripts.

This keeps one runtime instruction surface, avoids Skill discovery/context overhead, and makes hard policy visible in the repository itself.
