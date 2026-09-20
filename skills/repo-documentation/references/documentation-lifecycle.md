# Documentation Lifecycle

## States

```text
Draft -> Active -> Update -> still valid?
                            |- yes -> Active
                            \- no  -> Deprecated -> replaced?
                                                    |- yes -> Superseded + link
                                                    \- no  -> Delete when it has no historical value
```

- `Draft`: not yet verified against the repository. Do not rely on it.
- `Active`: verified and current.
- `Deprecated`: still readable but no longer authoritative. State what replaced
  it, or why nothing did.
- `Superseded`: replaced by another document. Keep the record and add
  `> Superseded by: <path>`.

ADRs use `Proposed`, `Accepted`, `Deprecated`, and `Superseded`, and are never
deleted. The record of a decision that was later reversed is the reason the ADR
exists.

## Transitions

- Update: change the content in place and keep `Status: Active`. Do not add a
  change log; Git holds history.
- Deprecate: set `Status: Deprecated`, say what replaced it or why nothing did,
  and keep the document while anything still references it.
- Supersede: set `Status: Superseded`, add `> Superseded by: <path>`, and update
  every incoming link in the same change.
- Delete: remove a non-ADR document only when it is no longer authoritative, no
  index or document references it, and it holds no historical or decision
  value. Update the index in the same change.

## Staleness

A document is stale when the repository contradicts it, not when it looks old.

1. Verify the claims the current task depends on against code, configuration,
   tests, or Git.
2. Correct or deprecate what no longer holds.
3. Remove a claim that cannot be verified rather than keeping it with a warning.

## Duplicates, orphans, and misfits

- Duplicate: two documents state the same fact. Choose the canonical owner, keep
  the fact there, and reduce the other document to a link.
- Orphan: a document that the documentation router does not reach. Link it from
  the router or delete it.
- Misplaced: a document whose content does not match its directory or `Type`.
  Move it or correct the type, then fix the links.
- Mixed: a document that owns two unrelated topics. Split it into two canonical
  documents and link them.
