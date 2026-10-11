---
name: repo-documentation
description: "Govern one canonical document per fact and one reachable documentation router. Use for every change's documentation impact check, docs/ Markdown edits, or documentation normalization, organization, audits, and checks; detect duplicate, orphaned, or stale content."
---

# Repo Documentation

`One fact -> one canonical document -> other documents link to it`

The repository is authoritative: verify claims against code, configuration,
tests, or Git; never duplicate facts. Keep documents readable in one pass,
create directories only with content,
and make every document reachable from the documentation index.

## Documentation impact check

Before publication of **every change**, and when asked whether docs need updating,
check whether it:

1. Changes architecture, components, boundaries, dependencies, or data flow.
2. Changes an interface/contract/API/CLI/configuration surface: flags, keys,
   defaults, schemas, or error codes.
3. Changes deployment, operations, or recovery: steps, commands, health checks,
   or rollback.
4. Changes developer workflow/setup: tools, commands, or prerequisites.
5. Adds/changes an ADR-worthy decision, including reversing/constraining a choice.
6. Makes any document wrong or stale.
7. Affects a diagram's components, order, decisions, or boundaries so its claimed
   flow no longer matches.

Unclear means yes: inspect. Report in the existing PR description or Plan Issue
delivery evidence, with no separate artifact. A yes names the changed canonical
document and its fact; a no is one line that nothing documented changed. Do not
create documents merely to appear thorough.

## Owners and standards

Resolve ownership before writing via
[`references/document-types.md`](references/document-types.md); choose the more
specific type when two could own a fact and link from the other. Current truth
belongs in `docs/Repo_Current_State.md` (`repo-current-state`), planned/in-progress
work in GitHub Issues (`plan-to-ticket`), and history in Git. Never copy those
snapshots/backlogs/history into content documents.

Apply [`references/doc-file-standard.md`](references/doc-file-standard.md) to
content under `docs/`: `kebab-case` filename, one `#` title, header fields `Type`,
`Status`, `Scope`. README pages, state, and ADR naming/status exceptions are
defined there. Use [`references/templates.md`](references/templates.md) for
Architecture, ADR, Guide, Runbook, and Reference. Header state and
creation/update/deprecation/supersession/deletion follow
[`references/documentation-lifecycle.md`](references/documentation-lifecycle.md).
**ADRs are never deleted.**

## Update before create; one router

Before creating a file, search `docs/` for its fact. Update an existing owner;
split/link unrelated topics if needed; create only when no owner exists. Avoid
restated documents or near-identical names. Follow the lifecycle reference for
duplicates/orphans.

Exactly one router makes every document reachable (directly or through linked
indexes): default `docs/README.md`, linked by root `README.md`; an existing root
README router may remain instead. Group links by topic/type. Keep links and
grouping, not detailed owned facts; brief entry-point facts such as install or
components are allowed with links to canonical detail. Link orphans, or delete
only if non-authoritative, unreferenced, and without historical/decision value.

## Diagrams

A diagram belongs to the document it illustrates, with the same canonical
ownership and update obligations; do not restate facts elsewhere. Draw only when
a picture materially clarifies decisions, request/data flow, states, or component
boundaries, not for value lists, single steps, or symmetry.

Placement/naming and unrendered markup are in the file standard; embedding,
including unrendered cases, is in templates. Invoke the `plantuml` capability
skill routed by `AGENTS.md` **before drawing**; it owns rendering procedures. If
unavailable, preserve `.puml` source and report unrendered using required markup.

For changed components/order/decisions/boundaries, update `.puml`, re-render
through that skill, and commit source/render with the behavior change. Never
hand-edit images or leave a diagram contradicting adjacent prose.

## Normalize and report

For normalize/organize/audit/check requests: scan `docs/`, classify types, detect
duplicates, orphans, misplacement, naming violations, missing index links, stale
claims, and mixed topics; normalize and update the router. Preserve meaning, do
not invent content or rewrite merely to tidy the tree. Report changes and what
was deliberately left alone.

Update canonical documents and the index, never parallel files. A negative
impact check reports no documentation change needed. Completion names documents
created/updated/deprecated/deleted, changed index entries, and unverified claims.
