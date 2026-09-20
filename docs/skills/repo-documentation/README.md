# Repo Documentation

`repo-documentation` is a Codex skill for governing repository documentation:
one fact, one canonical document, and other documents link to it. The managed
runtime source is
[`skills/repo-documentation/`](../../../skills/repo-documentation/).

## What it provides

- A governance contract in
  [`skills/repo-documentation/SKILL.md`](../../../skills/repo-documentation/SKILL.md).
- Agent-facing metadata in
  [`skills/repo-documentation/agents/openai.yaml`](../../../skills/repo-documentation/agents/openai.yaml).
- Focused references for the
  [file standard](../../../skills/repo-documentation/references/doc-file-standard.md),
  [document types](../../../skills/repo-documentation/references/document-types.md),
  [lifecycle](../../../skills/repo-documentation/references/documentation-lifecycle.md),
  and [templates](../../../skills/repo-documentation/references/templates.md).

## First-version capabilities

1. `docs/README.md` is the documentation index for a repository's `docs/` tree,
   reached from that repository's root `README.md`.
2. The Markdown file standard: `kebab-case` names, one `#` title, and no
   `Last updated` field on content documents.
3. The `Type` / `Status` / `Scope` header on every document under `docs/`.
4. Canonical owner routing with duplicate detection before any new file is
   created.
5. The documentation impact check that decides whether a change needs
   documentation work at all.

## Usage

1. Run the documentation impact check before publication for any change.
2. Route each fact to the document type that owns it, and update the canonical
   document instead of creating a parallel one.
3. Update the documentation index in the same change.
4. When the user asks to normalize, organize, audit, or check project
   documentation, scan `docs/`, classify, detect duplicates, orphans,
   misplacement, naming violations, missing index links, and stale claims, then
   normalize while preserving meaning.
5. Record `Draft`, `Active`, `Deprecated`, or `Superseded` in the header as the
   document's state changes; ADRs use `Proposed`, `Accepted`, `Deprecated`, or
   `Superseded` instead and are never deleted.

The impact check is a step inside the existing Test -> Redaction -> Commit path.
It adds no workflow stage, no second merge gate, and no documentation work when
the change touches nothing documented.

## Boundary with repo-current-state

`repo-documentation` owns documentation governance; it does not own what is true
right now. `docs/Repo_Current_State.md` stays with
[`repo-current-state`](../repo-current-state/README.md), and this skill only
links to it. Plans and Tickets stay in GitHub Issues, and change history stays
in Git.

This repository keeps its documentation index in the root
[`README.md`](../../../README.md), and `docs/Repo_Current_State.md` keeps its
`Last verified` field: index files, the state snapshot, and ADRs are the three
documented exceptions to the file standard.

## Repository layout

```text
.
├── skills/repo-documentation/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── doc-file-standard.md
│       ├── document-types.md
│       ├── documentation-lifecycle.md
│       └── templates.md
└── docs/skills/repo-documentation/
    └── README.md
```
