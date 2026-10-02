# Documentation Lifecycle

## States and transitions

| State | Meaning |
|---|---|
| Draft | Unverified; do not rely on it |
| Active | Verified/current |
| Deprecated | Readable but unauthoritative; name replacement or explain none |
| Superseded | Replaced; retain record and `> Superseded by: <path>` |

Draft -> Active -> update/verify -> Active if valid; otherwise Deprecated ->
Superseded if replaced, or deletion when eligible. ADRs use Proposed/Accepted/
Deprecated/Superseded and are never deleted, including reversed decisions.

- Update non-ADR documents in place, keeping Active; no changelog (Git owns it).
- Update ADRs only to correct factual errors, keeping status. Later decisions
  require a new ADR and superseding the old; never rewrite Accepted records.
- Set `Status: Deprecated` on deprecation; retain while references remain.
  Supersession sets `Status: Superseded`, adds the replacement header, and updates
  all incoming links in the same change.
- Delete non-ADRs only when unauthoritative, unreferenced by docs/index, and
  without historical/decision value; update index in the same change.

## Staleness and misfits

Staleness means repository contradiction, not age. Verify task-relevant claims
against code/config/tests/Git; correct/deprecate contradicted claims and remove
unverifiable claims instead of retaining warnings.

- Duplicate facts: retain one canonical owner; others link.
- Orphans: link from the router or use deletion rules.
- Misplaced content/directory/Type: report, then move/correct and repair links;
  never automatically move legacy directories.
- Unrelated topics: split into linked canonical documents.
