---
name: repo-documentation
description: Govern repository documentation as one canonical source of truth per fact. Use when a change may affect documented behavior, when creating or updating a Markdown document under `docs/`, or when the user asks to normalize, audit, organize, or check project documentation. Route each fact to the document type that owns it, prefer updating the canonical document over creating a new one, keep exactly one documentation router reachable from the repository entry point, and detect duplicates, orphans, and stale claims.
---

# Repo Documentation

Govern repository documentation so every fact has exactly one home, and that
home is findable from the repository entry point.

## Core contract

```text
One fact -> one canonical document -> other documents link to it
```

- The repository is the system of record. Verify a claim against code,
  configuration, tests, or Git before writing it.
- Never state the same fact in two documents. Keep it in the owner and link.
- Prefer updating the canonical document over creating a new file.
- Create a directory only when it has content. Structure follows need, not
  symmetry.
- Keep a document small enough to read in one pass.
- A document that no one can find does not exist. Every document is reachable
  from the documentation index.

## Documentation impact check

Run this check before publication for every change, and whenever the user asks
whether documentation needs updating. Ask only:

1. Did this change architecture, components, or their boundaries? A module,
   service, dependency, or data-flow change counts.
2. Did this change an interface, contract, API, CLI, or configuration surface?
   A flag, key, default, schema, or error code counts.
3. Did this change deployment, operations, or recovery? A step, command, health
   check, or rollback path counts.
4. Did this change the developer workflow or local setup? A tool, command, or
   prerequisite counts.
5. Did this change or add a design decision worth an ADR? Reversing or
   constraining a previous choice counts.
6. Did this make an existing document wrong or stale?

Tie-breaker: when an answer is unclear, treat it as yes and look. A check that
finds nothing costs one search; a skipped check leaves a wrong document behind.

Report the result in the change's existing delivery record: the pull-request
description, or the Plan Issue's delivery evidence when the workflow uses one.
The check creates no separate artifact. A yes answer names the canonical
document that changed and the fact it now owns. A no answer is one line stating
that nothing documented changed. Do not write documents to look thorough.

## Canonical owner

Resolve every fact to exactly one owner before writing anything. Owners are
routed by document type in
[`references/document-types.md`](references/document-types.md).

When two documents could own a fact, choose the more specific type and make the
other document link to it. A fact that no content document owns stays where it
already belongs: current truth in `docs/Repo_Current_State.md`, planned work in
GitHub Issues, and change history in Git.

## Document standard

Every content document under `docs/` follows
[`references/doc-file-standard.md`](references/doc-file-standard.md): a
`kebab-case` filename, a single `#` title, and a header block of `Type`,
`Status`, and `Scope` fields. The header is what lets a reader or an agent
decide which document owns a fact.

README pages, `docs/Repo_Current_State.md`, and the ADR filename and status
values are the documented exceptions in that reference.

## Update before create

Before creating any file:

1. Search `docs/` for the fact, not for the filename you imagined.
2. If a canonical document already owns the fact, update that document.
3. If the owning document has grown to cover unrelated topics, split it and
   link the parts.
4. Create a new document only when no existing document owns the fact.

Do not create a second document that restates an existing one, and do not let
two near-identical names coexist. Duplicate and orphan handling is defined in
[`references/documentation-lifecycle.md`](references/documentation-lifecycle.md).

## Documentation index

A repository has exactly one documentation router, and every document is
reachable from it.

- Default: `docs/README.md` is the router, and the repository `README.md` links
  to it.
- A repository that already routes documentation from its root `README.md` may
  keep that file as the router instead of adding `docs/README.md`.

The router groups links by type or topic. It carries links and grouping, never
the facts themselves. A document that the router does not reach is an orphan:
link it from the router, or delete it only when it is no longer authoritative,
nothing references it, and it holds no historical or decision value.

A router may keep the short entry-point facts it needs to be usable, such as
how to install the project or which components exist. Keep them brief and link
to the canonical document for detail; never let the router become the detailed
owner of a fact that a content document owns.

## Normalization

When the user asks to normalize, organize, audit, or check project
documentation:

```text
Scan docs/ -> classify by type -> detect duplicates, orphans, misplacement,
naming violations, missing index links, stale claims, mixed-topic documents
-> normalize -> update the documentation router
```

Preserve meaning. Do not rewrite documents to make the tree look tidy, and do
not invent missing content. Report what changed and what was deliberately left
alone.

## Lifecycle

State lives in the document header. Creation, update, deprecation, supersession,
and deletion rules are in
[`references/documentation-lifecycle.md`](references/documentation-lifecycle.md).
ADRs are never deleted.

## Templates

Use [`references/templates.md`](references/templates.md) for Architecture, ADR,
Guide, Runbook, and Reference documents.

## Boundaries

This Skill does not own:

- what is true right now -> `docs/Repo_Current_State.md` and `repo-current-state`
- planned or in-progress work -> GitHub Issues and `plan-to-ticket`
- change history -> Git
- the merge decision -> `pr-review`

Never copy the state snapshot, the Plan/Ticket backlog, or Git history into a
content document.

## Output behavior

- Update the canonical document and the index; do not create parallel files.
- When the impact check is negative, report that no documentation change is
  needed.
- When reporting completion, state which documents were created, updated,
  deprecated, or deleted, which index entries changed, and any claim left
  unverified.
