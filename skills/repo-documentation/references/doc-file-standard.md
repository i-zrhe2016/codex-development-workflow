# Documentation File Standard

Applies to created/modified content under `docs/`; bring legacy documents into
compliance when next modified or explicitly normalized. Report noncompliance;
never silently rename/restructure or rewrite meaning.

## Naming, title and header

Use lowercase `kebab-case.md` naming the fact, e.g. `authentication-flow.md`;
no CamelCase, underscores, meaningless names or version suffixes (Git holds
history). First line is the single `#` title. Split independent topics.
Immediately follow with:

```markdown
> Type: Architecture
> Status: Active
> Scope: <facts this document owns>
```

[Document types](document-types.md) defines Architecture/ADR/Guide/Runbook/
Reference/State and routing. Ordinary statuses: Draft/Active/Deprecated/
Superseded; ADRs: Proposed/Accepted/Deprecated/Superseded. Follow
[lifecycle](documentation-lifecycle.md). Superseded headers also carry
`> Superseded by: <path>`. Scope must identify ownership without needing audience
context.

No `Last updated`: Git records author/commit/date/diff; freshness comes from
code/config/tests verification. Exceptions:

- `README.md` retains its conventional name as an entry/index page and no header.
- `docs/Repo_Current_State.md` retains name/`Last verified`, following
  `repo-current-state` instead of this header.
- ADRs use zero-padded `NNNN-kebab-case.md` (e.g. `0001-use-postgresql.md`) and
  ADR statuses; single title/header still required.

All other `docs/` content follows this standard.

## Diagrams

Sources/renders are files, not content documents: no title/header. Use both
layers only when useful:

| Layer | Pair | Contract |
|---|---|---|
| Draw.io overview | `<name>.drawio` + `<name>.svg` | polished/editable human overview, hierarchy/readability; detailed edge cases stay in linked PlantUML/prose |
| PlantUML detail | `<name>.puml` + `<name>.svg` | textual diffs, exact loops, deterministic regeneration |

- Place new diagrams in `diagrams/` beside their owner, named for the fact.
  Shared repository overviews may use `docs/diagrams/drawio/`; keep existing
  PlantUML locations unless deliberately migrating the owner.
- Draw.io: fitting architecture/flowchart/C4 conventions; uncompressed XML,
  stable semantic non-reserved IDs, every edge has
  `<mxGeometry relative="1" as="geometry"/>`; no node overlap/edge-through-node.
- PlantUML: activity for workflow, state for lifecycle, component for
  responsibilities, sequence for messages; prefer `!theme plain` and Kroki-safe
  features unless advanced features are necessary.
- SVG is primary; existing PNGs may remain as compatibility artifacts.
- Before claiming success, validate Draw.io XML/IDs/edges or PlantUML renderer
  success with non-empty real SVG, then visually check overlap, clipping,
  crossings, routing and labels.
- Public Kroki uploads source to a third party: non-sensitive only. Internal,
  secret, proprietary or unreleased architecture requires a local backend.
- Owner embeds SVG with descriptive alt text and immediately links source;
  [templates](templates.md) defines rendered/unrendered markup. Orphans must be
  embedded or deleted. Never replace managed source with a flattened image.

## Links, index and size

Use repository-relative links to owners instead of copying facts; no in-repo
branch/commit/absolute URLs. Update incoming links on rename/move/deprecation/
supersession. Every document must be reachable from the one router, directly or
through its linked parent index. Link orphans, or delete only when unauthoritative,
unreferenced and without historical/decision value.

Prefer a few hundred tokens of dense verified content. Roughly 300 lines or two
unrelated topics signals splitting; move audience-specific detail to a linked
document.
