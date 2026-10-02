# Document Types and Canonical Owners

Choose the type before its directory, status and template.
Ordinary statuses: Draft, Active, Deprecated, Superseded.

| Type | Directory | Owns | Excludes | Status |
|---|---|---|---|---|
| Architecture | `docs/architecture/` | existing components, relationships, boundaries | choice rationale/alternatives | Ordinary |
| ADR | `docs/adr/` | one significant choice, alternatives, consequences | implementation detail | Proposed, Accepted, Deprecated, Superseded |
| Guide | `docs/guides/` | end-to-end developer tasks: setup/run/debug | exact value tables (link Reference) | Ordinary |
| Runbook | `docs/runbooks/` | operation, verification, failure handling, rollback | design rationale | Ordinary |
| Reference | `docs/reference/` | exact keys/defaults/constraints/endpoints/commands | tutorials/rationale | Ordinary |
| State | `docs/Repo_Current_State.md` | implemented/current truth | history/plans/architecture detail | `repo-current-state` owns it |

State uses `Last verified`, not this skill's header. Planned work belongs to
GitHub Issues; change history belongs to Git. The router holds links/grouping,
not detailed facts. Choices affecting no architecture/interface/deployment/
operation are implementation details, not ADRs.

Create only directories with content. This placement applies to new documents;
report legacy locations and preserve them until an explicit normalization move.
State remains a summary, never a detailed architecture, decision or procedure.
