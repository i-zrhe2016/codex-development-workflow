# Documentation File Standard

Rules for content documents under `docs/`. Index files, the state snapshot, and
ADRs follow the exceptions at the end of this file.

## Naming

- Use lowercase `kebab-case.md` for content documents.
- Name the fact, not the format: `deployment-process.md`,
  `database-migration.md`, `authentication-flow.md`.
- Do not use `DeploymentProcess.md`, `deployment_process.md`, `doc1.md`, or
  version suffixes such as `new-doc-final-v2.md`. Git holds history.
- ADRs are the one exception: `NNNN-kebab-case.md` with a zero-padded sequence,
  such as `0001-use-postgresql.md`, so the records stay ordered.

## Title

- The first line is the single `#` title.
- One file has one `#` title. Several independent topics in one file mean the
  file should be split.

## Header

Immediately after the title, add a blockquote header with the three required
fields. Index files and `docs/Repo_Current_State.md` are exempt; see Exceptions.

```markdown
# Authentication Architecture

> Type: Architecture
> Status: Active
> Scope: OAuth authentication and session lifecycle
```

- `Type` is one of `Architecture`, `ADR`, `Guide`, `Runbook`, `Reference`, or
  `State`. Type routing is defined in `document-types.md`.
- `Status` is one of `Draft`, `Active`, `Deprecated`, or `Superseded`. ADRs use
  `Proposed`, `Accepted`, `Deprecated`, or `Superseded`. Transitions are defined
  in `documentation-lifecycle.md`.
- `Scope` names the facts this document owns, not its audience. From `Scope`
  alone, a reader or an agent must be able to decide whether this is the
  document to change.
- A superseded document adds one more field: `> Superseded by: <path>`.

## No Last Updated field

Do not add `Last updated` to a content document. It becomes a false freshness
signal: a document can be edited without becoming true, and Git already records
author, commit, date, and diff.

Verify a document against code, configuration, and tests rather than against its
date. `docs/Repo_Current_State.md` is the only exception, because it is a
snapshot of what is true now and therefore keeps `Last verified`.

## Links

- Link to the owning document instead of repeating its fact.
- Use repository-relative paths. Do not link in-repo content through a branch,
  a commit, or an absolute URL.
- Update incoming links when a document is renamed, moved, deprecated, or
  superseded.

## Index

Every document is reachable from the repository's documentation router, or from
a parent index that the router links to. A document that the router does not
reach is an orphan: index it or delete it.

## Size

- Prefer a few hundred tokens of dense, verifiable content.
- Treat roughly 300 lines, or two unrelated topics in one file, as a signal to
  split.
- Move detail that only one reader group needs into a linked document.

## Exceptions

- A `README.md` page keeps its conventional name and does not carry the header.
  README pages are entry or index pages for the repository, a directory, or a
  documentation area.
- `docs/Repo_Current_State.md` keeps its name and its `Last verified` field, and
  follows `repo-current-state` instead of the header defined here.
- An ADR is exempt only from the ordinary filename rule and the ordinary status
  values. It still uses a single `#` title and the header, with the numbered
  filename and the ADR status values defined above.

Everything else under `docs/` is a content document and follows every rule in
this file.

## Adoption

The standard applies to every content document a change creates or modifies.
An existing document that predates the standard is brought into compliance when
it is next modified, or during an explicit normalization pass. A normalization
audit reports existing noncompliance and fixes what it can without rewriting
meaning; it does not silently rename or restructure the tree.
