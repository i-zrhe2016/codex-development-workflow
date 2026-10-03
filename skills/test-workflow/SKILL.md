---
name: test-workflow
description: "Verify feature, bug-fix, refactor or Ticket acceptance across backend, frontend, API, library and CLI work. Map acceptance to risk-based evidence; use focused checks, justified RED/GREEN, boundary/negative, property/fuzz, mutation, integration, regression, browser and flake checks; require the Test Quality Gate before PASS."
---

# Test Workflow

Own verification procedure/results; `verify-workflow` chooses when and how
broadly to verify. Stop at the result: no commit, push, PR or merge. Prefer the
lightest reliable, deterministic automated evidence over repeated inspection.

## Execution roles

These minimum rules work without `AGENTS.md` (not installed); it owns the full
policy when present. Implementation workers may use this procedure for local
feedback; independent acceptance is owned by a separate fresh verification
agent per Ticket, including docs/config/test and inline one-Slice work. One
implementer executes all dependency-ordered Slices; one verifier checks all
Ticket scenarios. Neither is reused across Tickets, and workers never spawn agents.
The coordinator dispatches them and owns the final Test Quality Gate and stages.

Codex dispatch uses `spawn_agent` with `fork_turns="none"`; other hosts require
equivalent fresh agents and independent context, or report BLOCKED without
main-agent fallback. The manual contract contains only role, current Ticket
goal/scope/non-goals, Slice dependencies/acceptance, relevant files/ownership,
Plan branch/base and verified prerequisites, validation commands and expected
summary; never the parent conversation or unrelated history. Same-Ticket
follow-up is allowed; interrupted/failed workers use fresh replacements from
verified checkpoints. Context isolation does not isolate filesystem/test state;
serialize conflicts on the shared Plan branch, without Ticket branches.

The independent verifier is read-only except caches/temporary evidence; code,
test, config and docs fixes belong to implementation. After fixes, a new
verifier rechecks the affected functionality and retains prior failures;
agent replacement or retries never erase unexplained flakiness.

## Strategy and bounded levels

Derive expectations from requirements, Function Checklist, acceptance and
existing public contracts, never by mirroring implementation. Test observable
behavior/stable contracts; implementation details only when themselves the
contract. Reuse existing frameworks, scripts, fixtures/helpers and conventions.

Choose a Slice level **before checks**:

| Level | Use |
|---|---|
| `minimal` | Tiny/docs/config/styling/dependency/typo/simple-refactor work. |
| `focused` | Default: smallest checks proving Slice acceptance. |
| `regression` | Bug fix, cross-module change or demonstrated regression risk. |
| `full` | High risk, release gate or explicit full-suite requirement. |

Level bounds breadth, never bypasses the quality gate. Identify mandatory risk
dimensions first; satisfy each or record concrete N/A reasons. Escalate for
acceptance, failures, affected boundaries, release policy or risk.

- **Tiny:** nearest existing checks after implementation; add regression tests
  when fixing behavior that could recur. No ceremonial RED/GREEN for formatting,
  docs or mechanically verifiable changes.
- **Normal:** define/update focused changed-contract tests, implement, then run
  them and relevant regression checks.
- **Complex/high-risk:** meaningful RED -> GREEN before production work when
  practical, especially permissions/authentication, money, state transitions,
  concurrency, parsing, data integrity and regressions.
- **Browser-visible:** smallest relevant user flow after lower-level checks.

Before complex/high-risk implementation, or ordinary validation, make a short
checklist of success/contract, boundary/failure, transitions/invariants and
regression risks, with relevant static, unit/component/API, integration and
interaction-only browser evidence. Prefer high-signal cases, not fixed counts
or exhaustive low-signal matrices.

## Acceptance-to-test matrix

Before Slice test-completion map **every** acceptance criterion to executed
evidence. Untested requirements keep the gate open; unmapped passing tests
prove no requirement.

| Acceptance criterion | Risk | Required dimension | Evidence | Result |
|---|---|---|---|---|
| <criterion> | low/medium/high | unit/integration/negative/... | <command/test> | pass/fail/blocked |

## Select mandatory test dimensions

Select by behavior/risk, not habit. Record concrete N/A reasons for otherwise
expected high-value dimensions:

| Dimension | Relevant contracts/risks |
|---|---|
| Happy path/contract | Expected observable behavior. |
| Boundary | Empty, min/max, off-by-one, thresholds, size, encoding, order, timeout, lifecycle. |
| Negative/failure | Invalid input/state, permissions/dependencies, rollback/partial failure, useful errors. |
| State transition/invariant | Before/after, idempotency, uniqueness, conservation, monotonicity/domain invariants. |
| Integration/contract | Database, filesystem, queue, network/service, schema/serialization, CLI process/public API. |
| Regression | Plausible recurrence: test fails for the protected defect/behavior. |
| Property/fuzz | Parsers, transformations, numerics, codecs, validation/protocols, complex inputs/strong invariants. |
| Mutation/test-strength | High-risk business logic or suspiciously easy tests/weak assertions. |
| Browser/E2E | Critical visible flow lower layers cannot prove. |
| Isolation/flake | Concurrency/time/shared state, external services, nondeterministic order, intermittent failures. |

Coverage percentage is diagnostic evidence only. High line/branch coverage
never proves meaningful assertions or complete requirements; pursue contract
coverage, not percentages.

## Test ladder

Run the cheapest relevant check first, broaden after focused checks pass, and
follow this applicable order:

1. Static: compiler/type/lint/schema/config validation.
2. Focused unit/component/API/package tests.
3. **Boundary and negative tests** for edges/failures.
4. Property/fuzz using existing generators/fuzzers when justified.
5. Integration/contract tests for touched boundaries/multiple modules.
6. Existing mutation tool or practical targeted manual mutation for high-risk
   logic or weak-test suspicion.
7. Affected module/package regression; full suite only for justified scope,
   risk or policy.
8. Critical browser/E2E flows lower layers cannot establish.
9. Isolation/flaky checks: diagnostic repeats only when nondeterminism suspected.

Stop at the first useful failure, diagnose before higher layers, then resume
from the cheapest check that can disprove the fix. Avoid repeated expensive
full-suite/browser checks in the inner loop unless required by repository
policy; use cheaper deterministic unit/API tests when sufficient.

## RED -> GREEN

For complex/risky Tickets/Slices:

1. Translate acceptance into focused cases and identify/write the smallest
   meaningful test for missing behavior.
2. Confirm RED for the expected reason. If behavior already exists, verify it
   and adjust the Ticket; never manufacture failure.
3. Implement the minimum production change; rerun the same test and direct
   checks until GREEN.
4. Run affected integration/regression; refactor only with relevant tests GREEN.

Keep the current behavior Slice explicit, never batch unrelated cycles into an
opaque loop.

## Property, fuzz, and mutation rules

Define an invariant/oracle before generating combinations example tests miss;
“did not crash” suffices only when crash-freedom is the contract. Preserve and
minimize failing seeds into deterministic regression tests.

Mutation evaluates **tests**, not production. Target changed/high-risk modules,
not repository-wide inner-loop mutation. For meaningful survivors strengthen
assertions/cases or explain equivalence/irrelevance or unreachable code; do not
chase a universal mutation-score target.

## Flaky and isolation policy

A retry is diagnostic evidence, never a PASS mechanism. Same commit/test state
FAIL then PASS without verified external cause is flaky: keep the gate
blocked/partial until understood, fixed or quarantined by explicit project
policy. A later pass never erases an unexplained failure.

Prefer deterministic clocks, seeded randomness, isolated fixtures, unique data,
event/state waits and hermetic dependencies. Never weaken assertions, delete
meaningful tests, add blind retries or fixed sleeps solely to obtain GREEN.

## Failure handling

Classify before returning fixes to implementation (the independent verifier never edits):

| Failure | Action |
|---|---|
| Implementation defect | Smallest relevant production fix for violated requirement. |
| Test defect | Fix assertion/fixture/selector/setup contradicting verified requirement, not product. |
| Regression | Fix broken unrelated expected behavior or stop if outside scope. |
| Environment/data | Missing dependency/service/account/fixture/permission/network/data: blocked, no fake code fix. |
| Requirement/design conflict | Ambiguous behavior/wrong architecture assumption: stop patch expansion and re-plan. |

For local implementation feedback, fix clear ordinary causes and rerun focused
checks. Independent verification returns the failure to implementation, then a
new verifier rechecks the affected function. Repeated failure without new
evidence, unclear cause or high risk needs targeted root-cause analysis. Code
review is not the default first response to every red test.

## Browser branch

Use only for changed browser-visible interaction or explicit E2E acceptance.
Prefer existing Playwright/Selenium/Cypress; without a harness, use real
Chromium if Playwright CLI is available.

- Decide flow/assertions before exploratory clicks; prove the smallest flow.
- Begin with known URL/session/data; use role/label/accessible name/stable test
  IDs rather than CSS hierarchy/XPath/nth-child. Wait for application state,
  never arbitrary sleeps or retry-based success.
- On failure capture screenshot, URL, visible state, console/request errors,
  and trace when useful.
- Source inspection, `curl`, static HTML or screenshots alone cannot pass
  browser behavior. Browser evidence complements unit/integration checks.
- Avoid destructive production actions; writes/deletes/payments/messages need
  a safe test environment or explicit authorization.

Direct CLI procedure:

```bash
playwright-cli open --browser=chromium <url>
playwright-cli snapshot
# click/fill/select/press as required
playwright-cli screenshot
playwright-cli close
```

## Test Quality Gate and report

Ticket Slices are test-complete only when:

- every acceptance criterion has concrete executed evidence;
- every mandatory dimension is satisfied or explicitly N/A with reason;
- selected level checks and every applicable dimension above are GREEN;
- failures are resolved or explicitly blocked/out of scope, with no unexplained
  flake promoted to PASS, no test weakened for GREEN, and coverage diagnostic
  only.

For multi-Ticket work keep inner checks focused per Ticket, then run appropriate
integration/regression after dependency-related Tickets are GREEN. Later
behavior fixes require affected reruns and an updated result. Across many
Tickets keep state in repository tests and authoritative GitHub Issues, not
fragile conversation memory.

Return a concise `Test Report` containing scope, mode
(`tiny / normal / RED-GREEN / browser`), level
(`minimal / focused / regression / full`) and result
(`pass / partial / fail / blocked`), the acceptance-to-test matrix above, and:

A `Test Quality Gate` table (`Dimension | Result | Evidence / N/A reason`)
covers acceptance coverage and every dimension above. Use `pass/fail` for
acceptance and `pass/fail/N/A` for other dimensions.

List failures with root cause, evidence and next action. Report **only executed
checks**; unavailable tools, environment, services, accounts or data never count
as passed.
