---
name: repo-documentation
description: "Enforce this repository's documentation ownership, indexing, file-standard, lifecycle, and documentation-impact records. Use when documented repository facts may change or when docs need normalization. Codex writes and edits documentation natively; this Skill only supplies repository-specific documentation contracts."
---

# Repository Documentation Contract

## Canonical ownership

One fact -> one canonical document -> other documents link to it.

Before creating a document, check whether an existing document already owns the fact. Update the owner instead of creating a parallel source.

Current truth belongs in `docs/Repo_Current_State.md`; planned work belongs in GitHub Issues; change history belongs in Git.

## Documentation impact record

For every development task, record one of these in the authoritative GitHub Issue:

- `Documentation Impact: updated — <documents>`
- `Documentation Impact: no-change — <concrete reason>`

Update documentation only when repository behavior, architecture, interface, configuration, operation, setup, or an existing documented claim actually changed.

## Repository document rules

Detailed file/type/lifecycle contracts live under `references/` and are authoritative:

- `references/doc-file-standard.md`
- `references/document-types.md`
- `references/documentation-lifecycle.md`
- `references/templates.md`

Keep exactly one documentation router reachable from the repository entry point. In this repository, root `README.md` is that router.

Every maintained document must be reachable from the router directly or through a clearly linked documentation page.

## Diagrams

Diagram reasoning and authoring are native Codex capabilities, not a separate Skill.

Repository-specific rules still apply:

- a diagram belongs to the document whose fact it illustrates;
- keep editable source and required render together;
- for PlantUML in this repository, keep `.puml` and same-basename `.svg` synchronized;
- use `bash scripts/render-diagrams.sh render` to regenerate and `bash scripts/render-diagrams.sh --check` to detect drift;
- never hand-edit a rendered SVG to hide a source problem;
- public rendering services must not receive sensitive or unreleased architecture.

## Normalization

When auditing documentation, preserve meaning while fixing repository-specific violations such as duplicate owners, orphaned docs, wrong placement, naming violations, stale claims, or missing index links.

Do not rewrite content merely for stylistic uniformity.
