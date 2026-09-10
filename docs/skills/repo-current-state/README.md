# Repo Current State

`repo-current-state` is a small Codex skill for keeping a repository-native
`docs/Repo_Current_State.md` as a concise, verified snapshot of the repository
as it exists now. The managed runtime source is
[`skills/repo-current-state/`](../../../skills/repo-current-state/).

## What it provides

- A maintenance contract in [`skills/repo-current-state/SKILL.md`](../../../skills/repo-current-state/SKILL.md).
- Agent-facing metadata in [`skills/repo-current-state/agents/openai.yaml`](../../../skills/repo-current-state/agents/openai.yaml).
- A current-state document that records implemented capabilities, constraints,
  known issues, and links to deeper documentation.

The state document is an orientation aid, not a changelog, decision log,
backlog, test-report archive, or permissions record.

## Usage

1. Read `SKILL.md` and the current-state document at the beginning of work.
2. Verify only the facts needed for the current task against repository
   evidence.
3. After the work unit's PR is merged, its source branch is deleted, and the
   default branch is synchronized, update `docs/Repo_Current_State.md` when the
   snapshot materially changed.
4. Keep architecture detail, history, decisions, and future work in their
   appropriate documents or project systems.

If the state update changes tracked content, make it through a new feature
branch and the same mandatory PR gate; do not commit directly to the default
branch.

## Architecture

![Repository documentation flow](diagrams/repository-state.svg)

The diagram source is
[`diagrams/repository-state.puml`](diagrams/repository-state.puml). The
repository has no application runtime or service deployment topology; the
documented flow is the skill-maintenance flow between repository evidence and
its verified state snapshot.

## Documentation index

- [Repository current state](../../Repo_Current_State.md)
- [Repository architecture](architecture.md)
- [Architecture diagram source](diagrams/repository-state.puml)

## Repository layout

```text
.
├── skills/repo-current-state/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── docs/skills/repo-current-state/
    ├── README.md
    ├── architecture.md
    └── diagrams/
        ├── repository-state.puml
        └── repository-state.svg
```
