---
name: verify-workflow
description: "Verify acceptance, regressions, incidents, review findings or branch/PR readiness. Select scope and level, invoke test-workflow and return PASS/FAIL/BLOCKED; never modify code or duplicate its quality gate."
---

# Verify Workflow

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
   scope: Slice, Ticket, branch, Plan or single criterion.
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

## Coordinator and verification worker

These minimum rules apply without `AGENTS.md` (not installed); when present,
it owns the full scheduling policy.

- Coordinator: dispatch one fresh independent verifier per Ticket after
  Development Complete, including docs/config/test and inline one-Slice work.
  This ordinary per-Ticket check uses one verifier. It verifies all that
  Ticket's scenarios; never reuse its implementation agent or any other Ticket's
  verifier, or split scenarios among workers.
- Final Plan/branch/PR acceptance verification is separate. Before deciding
  publication, PR update or merge readiness, dispatch one fresh independent
  verifier agent for the whole current Plan branch/PR scope. It must PASS; any
  FAIL or BLOCKED blocks readiness.
- The final verifier must not be a Ticket implementer, per-Ticket verifier or
  prior final verifier. Do not split final scenarios across agents.
- Dispatched verifier: invoke `test-workflow`, gather evidence, return a result;
  never spawn agents. Repository access is read-only except caches/temporary
  evidence; do not fix code, tests, config or docs to pass checks.
- Codex dispatch uses `spawn_agent` with `fork_turns="none"`; other hosts require
  equivalent fresh agents and independent context. Otherwise report BLOCKED;
  the main agent cannot substitute for the verifier.
- Hand off only role, current Ticket goal/scope/non-goals, Slice dependencies/
  acceptance, relevant files/ownership, Plan branch/base and verified prerequisite
  results, validation commands and expected summary; no parent conversation or
  unrelated history. Same-Ticket follow-up is allowed; interrupted/failed workers
  require fresh replacements from verified checkpoints, never cross-Ticket reuse.
- FAIL returns fixes to the implementation role. After fixes, dispatch a new
  verifier for the affected function, preserving all prior failed evidence;
  replacing agents cannot turn unexplained flakiness into PASS.
- Context isolation does not isolate files or test state. Serialize interference
  on the shared Plan branch; create no Ticket branch. The main agent synthesizes
  evidence and owns the Test Quality Gate, stage transitions and final judgment.

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

No code/test/config/docs edits to pass checks, commit/push/PR/merge, Issue closure
or state updates. Subagents cannot advance stages or replace main-agent judgment.
