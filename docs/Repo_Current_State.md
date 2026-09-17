# Repository Current State

Last verified: 2026-09-17 @ 0f45b7d

## Current Focus

- None.

## Implemented

- Repository changes follow the Issue -> feature branch -> test -> redaction ->
  PR -> Automatic Review -> merge and cleanup gates defined by `AGENTS.md`.
- `auto-deploy` provides a provider-neutral deployment contract with immutable
  artifacts, bounded health and smoke checks, authorized rollback, and a
  Tailscale-only hardening gate for publishing targets.
- Publishing targets require an approved immutable Tailscale identity and
  path, an actual hostname containing `deploy`, SSH restricted to Tailscale,
  public inbound denial, preserved outbound policy, and fenced recovery.
- The access catalog updater maintains the local Tailscale IP, service names,
  and deployment addresses in JSON and escaped HTML. The Skill requires a
  post-health refresh and Tailscale-only TCP/80 verification through the
  existing HTTP service; it does not install a server or change firewall state.
- Catalog writes use validation, atomic replacement, fenced durable recovery,
  authenticated transaction journals, and focused unit tests.
- Automatic Review uses the recoverable runner: the first PR review is full,
  bounded fixes default to incremental coverage from the last assessed head
  when base/history and named feature-branch identity match, and unbound or
  high-impact/uncertain changes fall back to full coverage.
- `Repo_Current_State.md` is the compact current-state memory; GitHub Issues
  hold plans and Tickets, while `docs/skills/` documents the managed skills.

## In Progress

- None.

## Known Issues / Failing Checks

- Targeted redaction scans report existing identity email examples and SSH URL
  literals; these require classification when publishing. This is not a clean
  repository-wide redaction result.

## Constraints

- Automatic Review requires an installed and authenticated Codex CLI.
- Shell commands use the available native tools through `context-efficiency`;
  exact evidence and publication gates preserve raw output and exit status.
- `auto-deploy` does not own target infrastructure or production approval and
  does not change an unspecified live host.
- Persisted plans and Tickets require an available, authorized GitHub Issues
  target; GitHub Issues are the durable authority for future work.

## Architecture Snapshot

- The root workflow owns lifecycle routing, Ticket and Slice gates, delegation,
  verification, publication, review, merge, and recovery guidance.
- Runtime skills remain under `skills/`; explanatory documentation is under
  `docs/skills/`; the installer packages the local skill bundles.
- `auto-deploy/SKILL.md` owns deployment-boundary behavior, while
  `update_access_catalog.py` owns catalog validation, rendering, and durable
  file reconciliation. See `docs/architecture/overview.md` for the topology.

## Next

- Start the next authorized Ticket from the updated default branch.
