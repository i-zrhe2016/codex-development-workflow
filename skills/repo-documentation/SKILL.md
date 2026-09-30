---
name: repo-documentation
description: "Govern repository documentation so each fact has one canonical owner and remains discoverable from one documentation router. Use when a change may affect docs, when creating/updating docs/, or when auditing/normalizing documentation. Prefer updating existing owners, detect stale/duplicate/orphaned content, and load detailed standards only when needed."
---

# Repo Documentation

Use **one fact -> one canonical document -> links elsewhere**.

## Core rules

- Verify claims against code/config/tests/Git before writing them.
- Update the canonical owner before creating a new document.
- Do not duplicate the same fact across documents.
- Keep every content document reachable from exactly one documentation router: normally `docs/README.md`, with the root README linking to it; an existing root README router may remain.
- Keep current state in `docs/Repo_Current_State.md`, planned work in GitHub Issues, and history in Git/changelog.

## Documentation impact check

Before publication, or when asked whether docs need changes, check whether the change affected:

- architecture/components/boundaries or a diagram that describes them;
- API/CLI/config/schema/error contracts;
- deployment/operations/recovery;
- developer workflow/setup;
- a design decision/ADR;
- an existing documented claim that is now stale.

If no documented fact changed, report that in one line and create nothing.

## Resolve the owner

Load [references/document-types.md](references/document-types.md) when owner/type is unclear.

For a document create/update, load [references/doc-file-standard.md](references/doc-file-standard.md) for filename/header/diagram rules. Load [references/templates.md](references/templates.md) only when a template or diagram embedding block is needed. Load [references/documentation-lifecycle.md](references/documentation-lifecycle.md) only for deprecation, supersession, deletion, duplicate, or orphan handling.

Keep references one level from this file; do not load all references by default.

## Update before create

1. Search `docs/` for the fact.
2. Update the existing canonical owner when one exists.
3. Split a mixed-topic owner only when it truly owns unrelated topics.
4. Create a new document only when no owner exists.
5. Ensure the documentation router links the final owner.

For diagrams, treat the source/rendered diagram as part of its owner document. Use the host diagram skill when available; never hand-edit generated images.

## Audit/normalize

When explicitly asked to audit or normalize, scan `docs/` for owner/type, stale claims, duplicates, orphans, naming/header violations, and missing router links. Preserve meaning and avoid cosmetic churn.

## Output

Update the canonical document and router directly when tools permit. Report created/updated/deprecated/deleted documents, router changes, and any unverified claim. Do not create parallel state, plan, backlog, or history documents.
