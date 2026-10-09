# Repository Current State

Last verified: 2026-10-08 @ working tree

## Current Focus

- [Plan #226](https://github.com/i-zrhe2016/codex-development-workflow/issues/226):
  portable two-level owner implementation with independent Sol acceptance;
  [Ticket #230](https://github.com/i-zrhe2016/codex-development-workflow/issues/230)
  covers global instruction and managed-Skill synchronization.

## Implemented

- Five stage workflows route planning, development, verification, publication
  and integration; full orchestration requires explicit end-to-end scope.
- The main agent directly dispatches a fresh owner per Ticket, who retains
  context across dependent Slices and local repairs without dispatching workers.
  Optional module assistants require fixed interfaces and isolated ownership;
  fresh independent verifiers and repair replacements remain main-dispatched.
  Final Plan acceptance uses a separate fresh verifier, with a one-Ticket
  exact-scope coalescing exception. See
  [worker policy](../AGENTS.md#multi-agent-delegation) and
  [Context Management](../AGENTS.md#context-management).
- Root and direct develop/verify/test entrypoints use the portable worker model
  policy from the root Skill associated with the active installation. Global
  instructions now carry the same two-level execution contract, and all 14
  managed Codex bundles match installer-selected source files and ownership
  markers. See
  [installation boundaries](deployment/installation.md#codex-model-routing).
  Project-local configuration remains separate.
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
- The installer packages 14 bundles for Codex and Claude, including
  `skill-eval` for blind A/B skill-effectiveness evaluation. Regression checks
  compare installed `SKILL.md` bytes with current sources on install and stale
  update for both targets, preserve skipped/unverified roots, and keep external
  configuration and instructions unchanged. See the
  [installation guide](deployment/installation.md#installer-regression-checks).

## Known Issues / Failing Checks

- Inherited publication guidance has unresolved non-default-base and
  changed-content revalidation ambiguity; evidence remains in closed
  [Plan #196](https://github.com/i-zrhe2016/codex-development-workflow/issues/196).
- Global diagram `--check` remains failing for 13 unchanged source/render pairs
  with known renderer drift; all 13 remain HEAD-identical. The two changed
  pairs passed source/render review and tracked-SVG visual review. No global
  diagram check PASS is claimed.

## Constraints

- Scheduling follows actual host capacity, without a project-set concurrency
  ceiling or total/lifetime agent quota.
- Ordinary development, docs and synchronization use Luna/medium; API/schema,
  security and complex logic use Luna/high. After two failed repair rounds on
  the same problem, a fresh Sol/high repair owner takes over that problem.
- Ticket and final acceptance use Sol/high. One new verifier may cover both
  only for a one-Ticket Plan with exactly matching scope, artifact/version,
  configuration and deployment surface. Requested settings do not establish
  underlying inference-engine identity or general host availability.
- Static configuration and package metadata do not establish the underlying
  inference-engine identity or general host/account availability.
- Installer evidence covers Claude packaging, not Claude runtime execution.
- The installer does not copy project instructions or runtime configuration;
  Codex requires `agents/openai.yaml`, while Claude packages omit it.
- GitHub Issues are the sole durable authority for persisted Plans and Tickets.

## Architecture Snapshot

- Runtime sources are root `SKILL.md` and `skills/`; root
  [README.md](../README.md) is the sole documentation router.
- [Architecture overview](architecture/overview.md) owns detailed topology and
  worker boundaries; this file holds only repository recovery truth.
