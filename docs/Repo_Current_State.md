# Repository Current State

Last verified: 2026-10-18 @ working tree (single-agent defaults, effort and escalation;
main-agent self-verification and 54 regression/installer tests passed;
not a whole-state audit)

## Current Focus

- [Single-model and single-agent defaults](plans/single-model-escalation.md):
  default main-agent implementation and acceptance; explicit escalation decisions.
- [Markdown persistence Plan / T0078](plans/markdown-plan-records.md#t0078):
  Markdown persistence implementation and local verification.

## Implemented

- Five stage workflows route planning, development, verification, publication
  and integration; full orchestration requires explicit end-to-end scope.
- Every new independent requirement has a versioned Plan Markdown file before
  implementation edits; existing requirements retain Issue authority. Ordinary
  requirements use one Ticket, while additional Tickets require distinct
  behavioral, dependency, or acceptance boundaries. Default single-agent
  execution keeps implementation, local repair, Ticket acceptance and final Plan
  acceptance in the main agent; no subagents or independent-verification claims.
  After two failed same-problem repair rounds, checkpoint and pause for user
  model selection and explicit delegation authorization. Only delegated mode
  uses fresh Ticket owners and independent verifiers, including the exact-scope
  one-Ticket coalescing exception. See
  [worker policy](../AGENTS.md#multi-agent-delegation) and
  [Context Management](../AGENTS.md#context-management).
- Root and direct develop/verify/test entrypoints use the portable worker model
  policy from the root Skill associated with the active installation. See
  [installation boundaries](deployment/installation.md#codex-model-routing).
  Project-local configuration remains separate. The local Codex installation
  was updated with all fourteen managed bundles and verified against source;
  global AGENTS.md was synchronized after a recoverable backup. Existing
  sessions still require restart to discover refreshed Skills. Regression tests
  also compare scratch installations with repository sources.
- Verification now requires Same-Surface proof: runtime identity/doctor,
  Launch -> Doctor -> Drive -> Evidence -> Cleanup, reproducible evidence and
  fresh verification-profile knowledge. If the intended artifact, instance or
  surface cannot be proven, verification reports BLOCKED.
- The Test Quality Gate includes explicit AuthN/AuthZ and assertion-strength
  dimensions. Authentication and authorization are proven separately when
  relevant, denied operations require protected side-effect absence, and tests
  must fail for the defect they claim to protect.
- Every new requirement has one `docs/plans/<plan-id>.md` with stable Ticket
  sections on its own Plan branch before implementation edits. Ordinary work uses one Ticket; supplementary same-requirement
  work updates its Ticket or adds one for a distinct boundary. Independent
  requirements use separate Plans even while an earlier Plan remains unmerged.
  See the [Plan scope contract](../skills/plan-to-ticket/SKILL.md#updating-scope).
- Local verification is a normal stopping point. The user controls publication
  and merge timing and scope; added scope requires impacted readiness checks
  and grants no new publication authority. See
  [publication decisions](workflow/usage.md#publication-decisions).
- In explicitly authorized delegated mode, development uses a native dynamic Ready Queue: dispatch newly ready Tickets,
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
- The prior full global diagram check reported 13 renderer-drift pairs; the
  current global drift count has not been remeasured. Six pairs changed for
  Markdown persistence pass repeat-render byte comparisons; no global PASS is
  claimed.
- The delegated-mode [Ticket loop source](architecture/diagrams/ticket-loop.puml) and
  paired SVG show Sol defaults and user-selected model escalation. The SVG is
  valid XML and its embedded PlantUML matches the source. Initial independent
  POST rerendering returned HTTP 403; a subsequent independent GET rerender
  succeeded and matched the tracked SVG byte-for-byte. The
  authoritative worker policy is [AGENTS.md](../AGENTS.md#who-chooses-the-subagent).
- Comparative performance for native one-, two- and three-owner scheduling is
  unmeasured. Live GitHub checkpoint-failure recovery has not been exercised; see
  [Plan #241](https://github.com/i-zrhe2016/codex-development-workflow/issues/241)
  for current evidence.

## Constraints

- Delegated scheduling follows actual host capacity, without a project-set concurrency
  ceiling or total/lifetime agent quota.
- Default single-agent work, including self-verification, uses Sol/low; planning
  uses high in either mode. Delegated development/repair uses Sol/low and
  independent verification Sol/high. Required effort is applied through supported
  host controls; repository configuration is not proof of live switching.
  Two consecutive failed same-problem repair rounds trigger
  diagnosis, a durable checkpoint and a pause until the user selects an escalation
  model and decides whether to authorize delegation; model selection alone does
  not authorize subagents. Unavailable selected settings block dispatch without fallback. See
  [worker routing](../AGENTS.md#who-chooses-the-subagent).
- In delegated mode, Ticket and final acceptance default to Sol/high unless
  explicitly selected otherwise. One new verifier may cover both
  only for a one-Ticket Plan with exactly matching scope, artifact/version,
  configuration and deployment surface. Requested settings do not establish
  underlying inference-engine identity or general host availability.
- Static configuration and package metadata do not establish the underlying
  inference-engine identity or general host/account availability.
- Installer evidence covers Claude packaging, not Claude runtime execution.
- The installer does not copy project instructions or runtime configuration;
  Codex requires `agents/openai.yaml`, while Claude packages omit it.
- New Plan/Ticket authority is versioned Markdown; existing Issue-backed
  requirements retain their original authority without migration or dual writes.
  Effective completion requires verified PR merge, not a post-merge MD commit.

## Architecture Snapshot

- Runtime sources are root `SKILL.md` and `skills/`; root
  [README.md](../README.md) is the sole documentation router.
- [Architecture overview](architecture/overview.md) owns detailed topology and
  worker boundaries; this file holds only repository recovery truth.
