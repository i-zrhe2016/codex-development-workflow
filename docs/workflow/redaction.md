# Redaction Workflow

This document defines the orchestration-level redaction gate for the
development workflow. It routes format-specific work to
`data-document-redaction`; it does not replace that specialist skill's
detection or transformation rules.

## When the gate runs

Classify the complete artifact set before committing it, and before any
artifact crosses a separate sharing, export, upload, or publication boundary.
After a blocking Automatic Review fix, repeat the scan before the next commit.
Git history is durable, so do not rely on cleaning up a secret or personal
value after it has been committed.

The scope includes source files, documentation, logs, configs, datasets,
screenshots, images, exports, filenames, and metadata. If an input data file
must be transformed, keep the original read-only and produce a safe output
copy.

## Procedure

1. **Establish scope.** Record the recipient/environment, purpose, required
   utility, risk level, and whether controlled reversibility is allowed. The
   default is non-reversible handling.
2. **Inventory surfaces.** Identify direct identifiers, quasi-identifiers,
   sensitive attributes, secrets, free text, comments, revisions, hidden
   layers, OCR, attachments, links, filenames, and metadata.
3. **Detect before transforming.** Use a format-aware parser and local rules or
   dictionaries. Do not print matched values, full context, credentials, or
   mapping tables in logs, reports, or the conversation.
4. **Apply the minimum sufficient transformation.** Prefer deletion,
   generalization, aggregation, or synthetic data for external publication.
   Use tokenization or pseudonymization only when controlled traceability is
   required, with its mapping isolated from the output. Delete and rotate
   exposed credentials rather than replacing them with usable-looking secrets.
5. **Validate independently.** Re-open the output through an independent
   parser or reader and check visible content, hidden surfaces, metadata,
   attachments, OCR, links, and required utility. For structured data also
   check schema, row counts, relationships, uniqueness, and relevant
   distributions. Unsupported binaries, encrypted content, low-confidence OCR,
   unreviewed attachments, signatures, or failed checks are `needs_review`.
6. **Write a safe delivery report.** Report the status, artifact types and
   hashes, transformation categories, detection counts, verification evidence,
   residual risks, and unsupported surfaces. Never write original values,
   mappings, keys, or full matching context.

## Gate outcomes

| Result | Required action |
|---|---|
| No sensitive surface in the declared scope | Record the scope and skip reason; continue. |
| `pass` | Continue to the commit, push, share, or publication gate; after a review fix, continue to the next commit. |
| `needs_review` | Stop the boundary transition; resolve or explicitly review the listed gap. |
| `blocked` | Stop and record the concrete blocker; do not publish the artifact. |

The orchestrator does not treat a black rectangle, a successful command, or a
single text search as proof of safe removal. A `pass` result is limited to the
declared scope and evidence; it is not a claim of absolute anonymization or
legal compliance.

## Minimum safe handoff

The handoff report should include, without sensitive values:

- `status`, `purpose`, audience, and verification time;
- input/output types and short paths or identifiers with hashes;
- transformation categories and detection counts;
- structure, hidden-surface, visual/independent-read, and utility checks;
- unsupported or unchecked surfaces, residual risks, assumptions, and tool
  versions; and
- the final `pass`, `needs_review`, or `blocked` decision.

For the specialist report schema and format-specific checks, use the
`data-document-redaction` skill references:

- `transformation-matrix.md` for operation selection;
- `document-surfaces.md` for hidden-surface checks; and
- `output-report.md` for the delivery report fields.
