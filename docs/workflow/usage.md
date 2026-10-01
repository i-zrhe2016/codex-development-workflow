# Capability Usage Guide

> Type: Guide
> Status: Active
> Scope: Selecting repository-specific capabilities without wrapping native Codex behavior

Start from the user's goal and authoritative GitHub Issue.

| Repository-specific need | Capability |
|---|---|
| Durable Plan/Ticket Issue hierarchy, IDs, or lifecycle metadata | github-issue-persistence |
| Canonical documentation ownership or repository doc rules | repo-documentation |
| Current-state snapshot reconciliation | repo-current-state |
| Deterministic staged sensitive-data scan | data-document-redaction |
| Repository-specific commit/push/PR guards | github-publish |

Planning, coding, testing, delegation, Git/GitHub use, and diagram authoring stay native to Codex.

## Mandatory records

Every development Issue records:

- task status and branch / PR references when applicable;
- verification evidence or why verification was unnecessary;
- Documentation Impact: updated or no-change, with documents/reason;
- Repo Current State: updated or no-change, with document/reason.

Do not create a Skill call or extra artifact solely to represent a native Codex capability.
