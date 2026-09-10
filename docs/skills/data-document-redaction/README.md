# Data and Document Redaction

`data-document-redaction` is the safety gate for sensitive content crossing a
commit, sharing, export, upload, or publication boundary. It covers personal
information, credentials, private keys, business-confidential material, and
other data that should not be exposed in the resulting artifact.

The runtime instructions live in [`SKILL.md`](../../../skills/data-document-redaction/SKILL.md).

## Standard flow

1. Define the output audience, purpose, allowed detail, and source scope.
2. Inventory visible, hidden, and metadata surfaces before transforming the
   content.
3. Detect sensitive values and choose the least destructive suitable action:
   remove, mask, pseudonymize, generalize, or synthesize.
4. Preserve the structure and meaning required by the task without copying
   secrets or unnecessary personal data.
5. Validate the rendered/shared artifact independently, including metadata and
   alternate representations where the format supports them.
6. Report what was checked and any remaining limitations without reproducing
   the sensitive value.

In the unified PR lifecycle, run this scan before the initial commit when
applicable and repeat it after any blocking Automatic Review fix before the
next commit. It does not create a direct-push exception for any change type.

Do not overwrite the original when a recoverable output is practical. Do not
attempt to recover or bypass redaction, and do not treat this documentation as
a substitute for applicable legal, regulatory, or organizational review.

## Managed references and tools

Detailed, format-specific guidance remains beside the runtime bundle:

| Resource | Purpose |
|---|---|
| [`authoritative-sources.md`](../../../skills/data-document-redaction/references/authoritative-sources.md) | Source and evidence handling |
| [`document-surfaces.md`](../../../skills/data-document-redaction/references/document-surfaces.md) | Visible, hidden, and metadata surfaces |
| [`transformation-matrix.md`](../../../skills/data-document-redaction/references/transformation-matrix.md) | Choosing a transformation |
| [`reddit-practices.md`](../../../skills/data-document-redaction/references/reddit-practices.md) | Practical workflow observations |
| [`output-report.md`](../../../skills/data-document-redaction/references/output-report.md) | Reporting and handoff format |
| [`scan_sensitive.py`](../../../skills/data-document-redaction/scripts/scan_sensitive.py) | Sensitive-content scan helper |
| [`verify_pdf.py`](../../../skills/data-document-redaction/scripts/verify_pdf.py) | PDF output verification helper |

Use the scripts as focused checks within the task; they do not replace
format-specific inspection or human judgment.

## Maintenance

Update this index when the skill's repository integration changes. Keep
format-specific procedures and supporting references in the runtime bundle's
`references/` and `scripts/` directories.
