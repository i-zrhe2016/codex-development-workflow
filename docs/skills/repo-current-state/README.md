# Repo Current State

`repo-current-state` defines the repository-specific contract for `docs/Repo_Current_State.md`.

Codex performs repository inspection and reasoning natively. The Skill only defines:

- the snapshot's required sections;
- its evidence boundary;
- what must not be copied into the snapshot;
- the authoritative Issue reconciliation record;
- freshness expectations.

Runtime contract: [`skills/repo-current-state/SKILL.md`](../../../skills/repo-current-state/SKILL.md).

The state snapshot is an orientation/recovery aid, not a planning system, test archive, changelog, or reasoning trace.
