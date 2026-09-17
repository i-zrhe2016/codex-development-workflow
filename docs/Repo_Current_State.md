# Repository Current State

Last verified: 2026-09-17 @ 9b942cbc08918a97a60aff56876fc40717ea2740

## Current Focus

- None.

## Implemented

- Repository changes follow the Issue -> feature branch -> test -> redaction ->
  commit -> push -> PR -> `pr-review` -> merge and cleanup gates defined by
  `AGENTS.md`.
- `pr-review` is the single merge decision gate. The first review covers the
  complete PR; bounded fixes may use incremental runner coverage, while
  high-impact or uncertain changes require full coverage.
- `github-push-when-ready` owns branch, commit, push, and PR readiness. The
  recoverable review runner is packaged with `pr-review` as an implementation
  detail.
- `auto-deploy` provides a provider-neutral deployment contract with immutable
  artifacts, bounded health and smoke checks, authorized rollback, and a
  Tailscale-only hardening gate for publishing targets.
- `Repo_Current_State.md` is the compact current-state memory; GitHub Issues
  hold plans and Tickets, while `docs/skills/` documents the managed skills.
- `plan-to-ticket` uses canonical `[PLAN]` and `[T####]` Issue titles,
  repository-scoped non-reused Ticket IDs, and linked Slice/branch identifiers.
- The installer records per-bundle ownership markers, protects unmarked paths,
  and offers recoverable `--adopt-legacy` migration for pre-marker installs.

## In Progress

- None.

## Known Issues / Failing Checks

- Pre-existing identity and SSH test fixtures remain under
  `skills/github-push-when-ready/`; the staged redaction scan for PR #69
  passed, but this is not a repository-wide redaction classification.

## Constraints

- `pr-review` requires an installed and configured Alibaba Open Code Review CLI
  (`ocr`) and a reachable provider endpoint with a supported model.
- Shell commands use the available native tools through `context-efficiency`;
  exact evidence and publication gates preserve raw output and exit status.
- `auto-deploy` does not own target infrastructure or production approval and
  does not change an unspecified live host.
- Persisted plans and Tickets require an available, authorized GitHub Issues
  target; GitHub Issues are the durable authority for future work.

## Architecture Snapshot

- The root workflow owns lifecycle routing, Ticket and Slice gates, delegation,
  verification, and merge/cleanup guidance.
- `github-push-when-ready` owns publication through PR readiness; `pr-review`
  owns the single PASS/BLOCKED merge decision and its recoverable runner.
- Runtime skills remain under `skills/`; explanatory documentation is under
  `docs/skills/`; the installer packages the local skill bundles. See
  `docs/architecture/overview.md` for the topology.

## Next

- Start the next authorized Ticket from the updated default branch.
