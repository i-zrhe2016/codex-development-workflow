---
name: verify-workflow
description: "Verify acceptance, regressions, incidents, review findings or branch/PR readiness. Select scope and level, invoke test-workflow and return PASS/FAIL/BLOCKED; never modify code or duplicate its quality gate."
---

# Verify Workflow

## Execution mode

Default reasoning effort is `low`, including self-verification; planning
uses `high` in either mode. Delegated development/repair uses `low` and
independent verification `high`. Report unsupported effort settings; do not
claim that editing instructions changed the running turn's effort.

Default single-agent execution: the main agent performs this stage directly,
including required checks and acceptance; do not spawn subagents. Record
self-verification accurately, without claiming independent verification.
Worker-only dispatch, independent-verifier and no-main-agent-fallback rules
below apply only in explicitly authorized delegated mode. Stage transitions
and an initial failure do not activate delegation. After two consecutive failed
same-problem repair rounds, checkpoint and pause; ask the user to choose an
escalation model and whether to authorize delegation. Model selection alone
does not authorize subagents. Missing subagent support does not block default
single-agent execution. Keep the existing Test Quality Gate, durable evidence
and publication boundaries in both modes.

Owns **trigger -> verification scope -> conclusion**; `test-workflow` owns
procedure and Test Quality Gate.

When the user controls the overall flow, verification reports evidence, residual
risks and available next actions, but must not choose fixes, expanded scope,
publication, PR updates or merge timing for the user.

Invoke for Development Complete acceptance before publication, explicit
verification, regression/incident/review confirmation, final Plan/branch/PR
acceptance, or PR readiness. Exploratory implementation feedback belongs to
`develop-workflow`.

1. Establish whether verification is warranted (record any skip reason), and
   scope: Ticket, branch, Plan or single criterion.
2. Choose `minimal`, `focused`, `regression` or `full` from behavior/risk.
3. Prove Same-Surface Verification before judging behavior: verify the intended
   artifact, instance and user-facing surface match the requested scope.
4. Invoke `test-workflow` for acceptance-to-test matrix, mandatory dimensions,
   RED/GREEN, flaky/isolation policy and quality gate. Do not restate/relax it.
5. Follow the coordinator/worker boundary below. Independent Ticket checks may
   run concurrently only without filesystem or shared test-state interference.
   Escalate breadth only for evidence, acceptance or explicit requirements.

## Verification proof protocol

These are hard verification rules. Report `BLOCKED` when the intended artifact,
runtime instance or surface cannot be proven.

- **Same-Surface Verification:** exercise the same public surface the user or
  release will use: artifact/build, process/container, URL/host/path, CLI entry,
  browser/client, account/role/tenant and configuration. Do not substitute an
  inner function, local default service, stale build or alternate environment
  unless the requested contract is explicitly that substitute surface.
- **Runtime Identity/Doctor:** before behavior checks, capture a non-secret
  runtime identity and health/doctor signal such as commit/version/build ID,
  image digest/package version, process/container ID, endpoint, feature flag or
  config fingerprint, database/schema target and authenticated principal/tenant
  where relevant. If the app has no doctor command/endpoint, use the smallest
  safe equivalent that proves the running instance.
- **Launch -> Doctor -> Drive -> Evidence -> Cleanup:** launch or select the
  intended instance, run identity/doctor checks, drive behavior through the real
  surface, record reproducible evidence, then clean up test data/sessions and
  temporary runtime state. Cleanup failure is residual risk or `BLOCKED` when it
  compromises further evidence.
- **Reproducible evidence:** report exact commands, URLs or entrypoints, checked
  artifact/instance IDs, profiles/config names, test accounts/roles as
  placeholders, seeds/fixtures, timestamps where useful and observed results.
  Never record secrets, unrelated chat URLs, raw tokens or private values.
- **Verification profile freshness:** use repository-specific verification
  profiles/feature maps only when they match the current branch, artifact,
  topology, entrypoints and acceptance scope. Treat missing, stale or ambiguous
  profile knowledge as a reason to inspect/doctor the runtime, and report
  `BLOCKED` if current scope cannot be mapped to a provable surface. Store such
  target-project knowledge under `docs/verification/` when useful; it is not a
  workflow Skill.

## Verification workers

The worker and parallel scheduling scenarios below apply only in explicitly
authorized delegated mode. Default single-agent verification is performed by
the main agent against the same acceptance criteria and Test Quality Gate.

### Scheduling policy scenario checks

When verifying a scheduling-policy change, exercise the real coordinator/worker
workflow:

- Confirm an independent Ticket can start while another dependency chain is
  blocked, and that an individual completion immediately requeues a newly ready
  Ticket.
- Confirm a dependent Ticket stays write-locked until prerequisite work is
  integrated, the fixed snapshot independently passes, and PASS evidence is
  saved to its section and Ticket-ID-tagged append-only evidence in the Plan record. Force a Plan-write failure and confirm it stays locked.
- Confirm overlapping paths, interfaces, schemas, fixtures and runtime
  resources serialize. Use a no-commit Git fixture with staged and unstaged
  edits plus binary, added, deleted and renamed files; confirm the patch captures
  every change while preserving the primary index and dirty baseline.
- Confirm concurrent checks use isolated databases, ports, caches and service
  instances. Change an integrated prerequisite and confirm its dependent
  closure is invalidated, active descendants stop or remain isolated, and their
  outputs are reconciled against the new base before integration.

These checks exercise the actual workflow; a toy scheduler tested only against
its own selection logic is not sufficient evidence.

These minimum rules apply without `AGENTS.md`; when present, it owns full
scheduling policy.

- The main agent directly dispatches one fresh independent Sol/high verifier
  for all scenarios across each Ticket after Development Complete. Verifiers
  are leaves, never spawn, and never implement fixes.
- Before deciding publication, PR update or merge readiness, verify the whole
  current Plan scope with a fresh independent Sol/high verifier. One NEW
  verifier may satisfy both Ticket and final gates only for a one-Ticket Plan
  whose full scope, artifact/version, configuration and deployment surface are
  exactly the same. Otherwise use a separate fresh final verifier. Any change
  after verification requires a new verifier for the affected scope.
- Count the active main agent and workers against actual host capacity. There
  is no project cap or lifetime quota; each direct dispatch needs one free slot
  for its worker. Queue when no slot is free.
- Verify one fixed, integrated Plan-branch snapshot. Independently identify its
  content and runtime/environment against acceptance before exercising it; hold
  that identity fixed for the run. Integration must precede this verification,
  and durable PASS evidence must precede dependent delivery. A failed Plan
  write blocks the unlock. Follow `develop-workflow` for snapshot capture,
  runtime isolation, event requeue, and stale-descendant reconciliation.
- The main agent identifies this active entrypoint and its same-installation
  root Skill routing policy before dispatch, preserving the active-copy and
  unsupported-setting BLOCKED rules. Request explicit model, effort and
  `fork_turns="none"`; distinguish requested settings from observed identity.
- Verifiers invoke `test-workflow`, gather evidence and return a result. They
  are read-only except caches/temporary evidence. Other hosts need equivalent
  fresh independent context. If that is unavailable, report BLOCKED.
- Hand off only role, Ticket goal/scope, dependencies and acceptance, relevant
  files/ownership, Plan branch/base, prerequisites and validation summary. Do
  not include parent conversation or unrelated history. Replace interrupted
  workers from verified checkpoints and preserve failures.
- FAIL returns the affected functionality to a fresh implementation worker,
  followed by a new independent verifier for all affected Ticket scenarios.
  The initial implementation failure does not count as a repair round. After
  two consecutive failed same-problem repair rounds, the main agent diagnoses,
  saves a durable Plan/Ticket checkpoint, pauses the affected problem and asks
  the user to choose an escalation model under the canonical routing policy.
  Until selection, dispatch no further same-problem repair or new model.
  Repair implementation defaults to Sol/low; verification defaults to Sol/high.
  Apply explicit user-selected settings with a compatible role or no named role;
  unavailable settings block dispatch without fallback. Preserve counts and evidence.
- The main agent retains the Test Quality Gate, stage transitions and final
  judgment. Preserve unexplained flaky failures; a passing retry does not erase
  them.

Return exactly one conclusion with evidence, then stop:

- `PASS`: selected level and all applicable mandatory dimensions passed.
- `FAIL`: identify failing check/evidence; return fixes to `develop-workflow`.
- `BLOCKED`: checks could not run; explain why.

PASS may end the requested work as local verified functionality; it grants no
commit/push/PR/merge authority, and awaiting the user's publication decision is
not BLOCKED. With expanded unmerged Plan scope, preserve prior evidence and
recheck impacted acceptance plus batch readiness; an existing PR is not ready
for that scope until those checks, the single-verifier final Plan/branch/PR
acceptance gate and an authorized update succeed.

No code/test/config/docs edits to pass checks, commit/push/PR/merge, legacy Issue closure
or state updates. Subagents cannot advance stages or replace main-agent judgment.

## Legacy checkpoint compatibility

Existing Issue requirements, including extensions, retain original contracts,
checkpoints, statuses and evidence. Follow [legacy continuation](../plan-to-ticket/SKILL.md#legacy-continuation);
never migrate or dual write. New requirements use Plan Markdown sections.
