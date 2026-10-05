# Repository Current State

Last verified: 2026-10-05 @ working tree

## Implemented

- Five stage workflows route planning, development, verification, publication
  and integration; full orchestration requires explicit end-to-end scope.
- Every Ticket requires fresh implementation and independent
  verification workers, with scoped context and durable Issue checkpoints. See
  [worker policy](../AGENTS.md#multi-agent-delegation) and
  [Context Management](../AGENTS.md#context-management).
- Ordinary per-Ticket verification uses one fresh verifier. Final
  Plan/branch/PR acceptance verification uses three fresh independent verifiers
  for the whole current Plan scope before readiness can pass.
- Verification now requires Same-Surface proof: runtime identity/doctor,
  Launch -> Doctor -> Drive -> Evidence -> Cleanup, reproducible evidence and
  fresh verification-profile knowledge. If the intended artifact, instance or
  surface cannot be proven, verification reports BLOCKED.
- The Test Quality Gate includes explicit AuthN/AuthZ and assertion-strength
  dimensions. Authentication and authorization are proven separately when
  relevant, denied operations require protected side-effect absence, and tests
  must fail for the defect they claim to protect.
- Plans may batch functionalities under one branch, commit and PR with
  per-Ticket evidence. New functionality extends the same unmerged Plan with
  a new Ticket; after merge it starts a new Plan. See the
  [Plan scope contract](../skills/plan-to-ticket/SKILL.md#updating-an-unmerged-plan).
- Local verification is a normal stopping point. The user controls publication
  and merge timing and scope; added scope requires impacted readiness checks
  and grants no new publication authority. See
  [publication decisions](workflow/usage.md#publication-decisions).
- Material `docs/Repo_Current_State.md` updates are included on the same Plan
  branch and PR as the work they describe, before commit/PR creation; integration
  validates merged state instead of creating a post-merge state-only PR. See
  [repo-current-state](../skills/repo-current-state/SKILL.md#read-and-update-triggers).
- The installer packages 13 bundles for Codex and Claude. Regression checks
  compare installed `SKILL.md` bytes with current sources on install and stale
  update for both targets. See the
  [installation guide](deployment/installation.md#installer-regression-checks).

## Known Issues / Failing Checks

- Inherited publication guidance has unresolved non-default-base and
  changed-content revalidation ambiguity; evidence remains in closed
  [Plan #196](https://github.com/i-zrhe2016/codex-development-workflow/issues/196).

## Constraints

- `.codex/config.toml` still sets a concurrency ceiling of three; effective host
  capacity governs safe waves. Parallel-first scheduling is not implemented.
- Installer evidence covers Claude packaging, not Claude runtime execution.
- The installer does not copy project instructions or runtime configuration;
  Codex requires `agents/openai.yaml`, while Claude packages omit it.
- GitHub Issues are the sole durable authority for persisted Plans and Tickets.

## Architecture Snapshot

- Runtime sources are root `SKILL.md` and `skills/`; root
  [README.md](../README.md) is the sole documentation router.
- [Architecture overview](architecture/overview.md) owns detailed topology and
  worker boundaries; this file holds only repository recovery truth.
