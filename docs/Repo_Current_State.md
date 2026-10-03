# Repository Current State

Last verified: 2026-10-02 @ working tree

## Current Focus

- [Plan #196](https://github.com/i-zrhe2016/codex-development-workflow/issues/196)
  on `refactor/ticket-context-batch-delivery-policy`; changes remain unmerged
  and unreleased.

## Implemented

- Five stage workflows route planning, development, verification, publication
  and integration; full orchestration requires explicit end-to-end scope.
- The working tree requires fresh Ticket implementation and independent
  verification workers, with scoped context and durable Issue checkpoints. See
  [worker policy](../AGENTS.md#multi-agent-delegation) and
  [Context Management](../AGENTS.md#context-management).
- Plans may explicitly batch multiple functionalities under one branch, commit
  and PR with per-Ticket evidence and complete batch descriptions; existing
  verification and publication gates remain in force.
- The installer packages 13 bundles for Codex and Claude. Regression checks
  compare installed `SKILL.md` bytes with current sources on install and stale
  update for both targets. See the
  [installation guide](deployment/installation.md#installer-regression-checks).

## In Progress

- Documentation reconciliation and remaining delivery work belong to the active
  Plan; Issue records own status, acceptance and failure evidence.

## Known Issues / Failing Checks

- Inherited publication guidance has unresolved non-default-base and
  changed-content revalidation ambiguity; the active Plan records the evidence.

## Constraints

- `.codex/config.toml` still sets a concurrency ceiling of three; effective host
  capacity governs safe waves. Parallel-first scheduling is not implemented.
- Installer evidence covers Claude packaging, not Claude runtime execution or
  a real GitHub publication/merge flow for this working tree.
- The installer does not copy project instructions or runtime configuration;
  Codex requires `agents/openai.yaml`, while Claude packages omit it.
- GitHub Issues are the sole durable authority for persisted Plans and Tickets.

## Architecture Snapshot

- Runtime sources are root `SKILL.md` and `skills/`; root
  [README.md](../README.md) is the sole documentation router.
- [Architecture overview](architecture/overview.md) owns detailed topology and
  worker boundaries; this file holds only repository recovery truth.

## Next

- Continue the active Plan through its remaining authorized stage gates.
