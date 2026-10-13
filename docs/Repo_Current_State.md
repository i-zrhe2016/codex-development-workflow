# Repository Current State

Last verified: 2026-10-13 @ working tree (single-Issue contract update; local
contract checks only, not a whole-state audit)

## Current Focus

- [Plan #249](https://github.com/i-zrhe2016/codex-development-workflow/issues/249)
  and [Ticket T0077](https://github.com/i-zrhe2016/codex-development-workflow/issues/249#t0077):
  accepted single-Issue Plan/Ticket behavior; publication and acceptance status
  are tracked in that Issue.

## Implemented

- Five stage workflows route planning, development, verification, publication
  and integration; full orchestration requires explicit end-to-end scope.
- Every independent requirement has a Plan Issue before branch work; ordinary
  requirements use one Ticket, while additional Tickets require distinct
  behavioral, dependency, or acceptance boundaries. The main agent directly
  dispatches a fresh owner per Ticket, who retains context across that Ticket
  and local repairs without dispatching workers.
  Optional module assistants require fixed interfaces and isolated ownership;
  fresh independent verifiers and repair replacements remain main-dispatched.
  Final Plan acceptance uses a separate fresh verifier, with a one-Ticket
  exact-scope coalescing exception. See
  [worker policy](../AGENTS.md#multi-agent-delegation) and
  [Context Management](../AGENTS.md#context-management).
- Root and direct develop/verify/test entrypoints use the portable worker model
  policy from the root Skill associated with the active installation. See
  [installation boundaries](deployment/installation.md#codex-model-routing).
  Project-local configuration remains separate. The global instruction and
  managed-bundle sync check is tracked by [Ticket #236](https://github.com/i-zrhe2016/codex-development-workflow/issues/236);
  its selected installed bundles match the installer-managed source files.
- Verification now requires Same-Surface proof: runtime identity/doctor,
  Launch -> Doctor -> Drive -> Evidence -> Cleanup, reproducible evidence and
  fresh verification-profile knowledge. If the intended artifact, instance or
  surface cannot be proven, verification reports BLOCKED.
- The Test Quality Gate includes explicit AuthN/AuthZ and assertion-strength
  dimensions. Authentication and authorization are proven separately when
  relevant, denied operations require protected side-effect absence, and tests
  must fail for the defect they claim to protect.
- Every independent requirement has its own Plan Issue with Ticket sections before
  branch work. Ordinary work uses one Ticket; supplementary same-requirement
  work updates its Ticket or adds one for a distinct boundary. Independent
  requirements use separate Plans even while an earlier Plan remains unmerged.
  See the [Plan scope contract](../skills/plan-to-ticket/SKILL.md#updating-scope).
- Local verification is a normal stopping point. The user controls publication
  and merge timing and scope; added scope requires impacted readiness checks
  and grants no new publication authority. See
  [publication decisions](workflow/usage.md#publication-decisions).
- Development uses a native dynamic Ready Queue: dispatch newly ready Tickets,
  integrate accepted outputs, then verify dependent work on the integrated
  snapshot. Accepted, uncommitted Plan contents are preserved as baseline `S`
  for isolated dependent workers. See
  [Ticket owner and Ready Queue rules](../skills/develop-workflow/SKILL.md#ticket-owners-and-workers).
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
- The last full global diagram check reported 13 renderer-drift pairs. Eight
  source/render pairs have changed since that baseline, so the current global
  drift count has not been remeasured. The eight changed pairs pass the
  isolated source/render check and visual review; no global diagram-check PASS
  is claimed.
- Comparative performance for native one-, two- and three-owner scheduling is
  unmeasured. Live GitHub checkpoint-failure recovery has not been exercised; see
  [Plan #241](https://github.com/i-zrhe2016/codex-development-workflow/issues/241)
  for current evidence.

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
