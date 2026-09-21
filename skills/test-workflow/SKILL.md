---
name: test-workflow
description: "General repository verification and test-quality workflow. Use when validating feature work, bug fixes, refactors, or ticket acceptance criteria across backend, frontend, APIs, libraries, and CLI projects. Map acceptance criteria to evidence, choose mandatory test dimensions from risk, run the cheapest relevant checks first, use RED/GREEN for complex or risky behavior, add boundary/negative, property/fuzz, mutation, integration, regression, or browser checks when justified, detect flaky tests, and require an explicit Test Quality Gate before PASS."
---

# Test Workflow

Validate behavior with the lightest reliable test strategy. This skill owns the
Test stage for every change; it does
not choose a direct-push path. Prefer deterministic automated feedback over
repeated agent inspection.

## Core rules

1. Derive tests from the requirement, ticket function checklist, acceptance criteria, and existing project contracts.
2. Reuse the repository's existing test framework, scripts, fixtures, helpers, and conventions before adding new infrastructure.
3. Run the smallest relevant check first; broaden only after the focused checks pass.
4. Test observable behavior and stable contracts, not implementation details unless the implementation detail is itself the contract.
5. Never weaken assertions, delete meaningful tests, add blind retries, or add fixed sleeps merely to obtain GREEN.
6. Do not run expensive full-suite or browser validation repeatedly inside the inner implementation loop unless the repository requires it.
7. A passing test does not prove an untested requirement. Map every acceptance criterion to evidence.

## Bounded verification levels

Choose one level for the current Slice before running checks:

| Level | Use |
|---|---|
| `minimal` | Tiny, documentation, configuration, styling, dependency, typo, or simple refactor changes. |
| `focused` | Default; the smallest checks directly tied to the Slice acceptance criteria. |
| `regression` | Bug fixes, cross-module changes, or demonstrated regression risk. |
| `full` | High-risk changes, release gates, or an explicit full-suite requirement. |

The level limits breadth; it does not replace the quality gate. Before running
checks, identify the mandatory test dimensions created by the changed behavior
and risk profile. Stop only when every mandatory dimension is satisfied, or is
recorded as N/A with a concrete reason. Escalate breadth when acceptance
criteria, failure evidence, an affected boundary, release requirements, or the
risk profile requires it.

## Choose the testing mode

Use task risk and complexity to choose the test strategy, not to choose a
different delivery path. Every change still continues through the common branch,
redaction when applicable, commit, push, PR and merge gates.

- **Tiny change:** run the closest existing checks after implementation. Add a regression test only when the change fixes behavior that could reasonably recur.
- **Normal behavior change:** define or update focused tests around the changed contract, implement, then run focused tests and relevant regression checks.
- **Complex/high-risk behavior:** use RED -> GREEN. Create or confirm a meaningful failing test before production implementation when practical, then implement the minimum change required to pass.
- **Browser-visible behavior:** after lower-level checks pass, use the browser branch below for the smallest relevant user flow.

Strict test-first behavior is especially useful for permissions, authentication, money, state transitions, concurrency, parsing, data integrity, and bug regressions. Do not force ceremonial RED/GREEN for trivial formatting, documentation, or mechanically verifiable changes.

## Build the test checklist

Before implementation for complex/high-risk work, or before validation for ordinary work, create a short checklist:

```text
Behavior / contract
- expected success path
- important boundary or failure path
- regression risk

Evidence
- static/type/lint check if relevant
- focused unit/component/API test
- integration test if boundaries are crossed
- browser/E2E test only if user-visible interaction changed
```

Prefer a compact high-signal set over a large low-signal matrix, but do not use
a fixed case count as a completeness rule. Cover contracts, boundaries, state
transitions, and failure handling first.

## Build the acceptance-to-test matrix

Before declaring a Slice test-complete, map every acceptance criterion to
executed evidence:

| Acceptance criterion | Risk | Required dimension | Evidence | Result |
|---|---|---|---|---|
| <criterion> | low/medium/high | unit/integration/negative/... | <command/test> | pass/fail/blocked |

A passing test that is not mapped to a requirement does not prove the
requirement. A requirement without evidence keeps the quality gate open.

## Select mandatory test dimensions

Choose dimensions from the behavior and risk, not from habit. Use only
applicable dimensions, but record why a high-value dimension is N/A when it
would otherwise be expected.

- **Happy path / contract:** expected observable behavior.
- **Boundary:** empty, minimum/maximum, off-by-one, threshold, size, encoding,
  ordering, timeout, or lifecycle boundaries relevant to the contract.
- **Negative / failure:** invalid input, rejected state, permission failure,
  dependency failure, rollback, partial failure, and useful error behavior.
- **State transition / invariant:** before/after state, idempotency, uniqueness,
  conservation, monotonicity, or other domain invariants.
- **Integration / contract boundary:** database, filesystem, queue, network,
  service, schema, serialization, CLI process, or public API boundaries.
- **Regression:** a test that would fail for the defect or behavior being
  protected when recurrence is plausible.
- **Property / fuzz:** parsers, transformations, numerical logic, codecs,
  validation, protocol handling, complex input spaces, or strong invariants.
- **Mutation / test-strength:** high-risk business logic or suspiciously easy
  tests where assertion quality matters more than line execution.
- **Browser / E2E:** critical browser-visible user flow that lower layers cannot
  prove.
- **Isolation / flake:** tests involving concurrency, time, shared state,
  external services, nondeterministic ordering, or prior intermittent failure.

Coverage percentage is diagnostic evidence only. Never use a high line or branch
coverage number as proof that assertions are meaningful or requirements are
complete.

## Test ladder

Run checks in this order when applicable:

1. **Static feedback:** compiler, typecheck, lint, schema/config validation.
2. **Focused automated tests:** the smallest unit/component/API/package tests covering the changed behavior.
3. **Boundary and negative tests:** exercise contract edges and expected failure behavior.
4. **Property/fuzz checks:** use the repository's existing generator/fuzzer when complex input spaces or invariants justify it.
5. **Integration/contract tests:** service, database, filesystem, queue, network, schema, process, or multi-module boundaries touched by the change.
6. **Mutation/test-strength checks:** use an existing mutation tool, or a small targeted manual mutation when practical, for high-risk logic or weak-test suspicion.
7. **Affected regression:** run the affected package/module suite; use the full suite only when justified by scope, risk, or project policy.
8. **Browser/E2E:** verify only critical browser-visible flows that lower layers cannot establish.
9. **Isolation/flaky check:** repeat only for diagnosis when nondeterminism is suspected; a later pass does not erase an earlier unexplained failure.

Stop at the first useful failure and diagnose it before spending resources on
higher layers. After fixes, resume the ladder from the cheapest check that can
disprove the fix.

## RED -> GREEN loop

For complex or risky Tickets/Slices:

1. Translate acceptance criteria into focused test cases.
2. Write or identify the smallest meaningful test that should fail for the missing behavior.
3. Run it and confirm **RED** for the expected reason. If it passes because the behavior already exists, do not manufacture a failure; verify the requirement and adjust the ticket.
4. Implement the minimum production change.
5. Run the same focused test and directly related checks until **GREEN**.
6. Run the affected integration/regression layer.
7. Refactor only while keeping the relevant tests GREEN.

Do not batch many unrelated RED/GREEN cycles into one opaque agent loop. Keep the current behavior slice explicit.

## Property, fuzz, and mutation rules

Use property/fuzz testing to explore input combinations that example tests are
unlikely to enumerate. Define the invariant or oracle before generation; do not
treat "did not crash" as sufficient unless crash-freedom is the contract. Keep
and minimize any failing seed as a deterministic regression test.

Use mutation testing to evaluate the tests, not the production implementation.
Prefer changed or high-risk modules rather than repository-wide mutation in the
inner loop. Surviving meaningful mutations indicate weak assertions, missing
cases, or unreachable code; either strengthen the tests or document why the
mutation is equivalent/not relevant. Do not chase a universal mutation-score
target.

## Flaky and isolation policy

A retry is diagnostic evidence, never a PASS mechanism. If the same commit and
test state produce FAIL then PASS without a verified external cause, classify
the check as flaky and keep the quality gate blocked or partial until the
nondeterminism is understood, quarantined by explicit project policy, or fixed.

Prefer deterministic clocks, seeded randomness, isolated fixtures, unique test
data, event/state waits, and hermetic dependencies. Never add blind retries or
fixed sleeps to convert flaky behavior into GREEN.

## Failure handling

Classify a failure before changing code:

- **Implementation defect:** product behavior violates the requirement -> fix the smallest relevant production code.
- **Test defect:** assertion, fixture, selector, or test setup contradicts the verified requirement -> fix the test, not the product.
- **Regression:** unrelated expected behavior broke -> fix or stop if outside scope.
- **Environment/data failure:** dependency, service, account, fixture, permission, network, or test data unavailable -> mark blocked; do not fake a code fix.
- **Requirement/design conflict:** expected behavior is ambiguous or the architecture assumption is wrong -> stop expanding the patch and re-plan.

For ordinary failures with a clear cause, fix and rerun the focused test. Escalate to targeted root-cause analysis when the same failure repeats without new evidence, the cause remains unclear, or the change is high-risk. Do not use code review as the first response to every red test.

## Browser branch

Use this branch only when browser-visible interaction changed or the acceptance criteria explicitly require an end-to-end user flow.

Prefer the repository's existing Playwright/Selenium/Cypress setup. If no browser harness exists and Playwright CLI is available, use real Chromium.

Browser rules:

- Test the smallest user flow that proves the changed behavior.
- Separate test discovery from execution: decide the important flow and assertions before exploratory clicking.
- Prefer role, label, accessible name, or stable test IDs over CSS hierarchy/XPath/nth-child selectors.
- Wait for application state, not arbitrary time. Avoid fixed sleeps and retry-based success.
- Start from known URL, session, and data state.
- Capture screenshot, URL, visible state, console/request errors, and trace when useful on failure.
- Never mark browser behavior passed from source inspection, `curl`, static HTML, or a screenshot alone.
- Avoid destructive production actions. Use a safe test environment or explicit authorization for writes, deletes, payments, or message sending.

When using Playwright CLI directly:

```bash
playwright-cli open --browser=chromium <url>
playwright-cli snapshot
# click/fill/select/press as required
playwright-cli screenshot
playwright-cli close
```

Browser tests complement unit/integration checks; they do not replace them.

## Efficiency guardrails

- Do not rerun the full suite after every small edit.
- Do not use browser automation to validate behavior that a deterministic unit/API test can prove more cheaply.
- Do not chase coverage percentage as the goal. Prefer meaningful contract coverage.
- Do not generate tests after reading implementation merely to mirror the code. Derive expected behavior from requirements and existing public contracts.
- Keep test state outside fragile conversational memory when the task spans many tickets; use repository test files and the authoritative GitHub Issue as the durable source of truth.

## Completion

A Ticket's Slices are test-complete only when the Test Quality Gate closes:

- every acceptance criterion maps to concrete executed evidence;
- every mandatory risk dimension is satisfied, or explicitly N/A with reason;
- the selected checks for the chosen level are GREEN;
- required boundary, negative, integration, regression, property/fuzz,
  mutation, browser, and isolation checks are GREEN when applicable;
- no unexplained flaky result is converted to PASS by rerun;
- failures are resolved or explicitly classified as blocked/out of scope;
- no test was weakened solely to make the suite pass;
- coverage metrics, if reported, are treated as diagnostics rather than proof
  of test quality.

For a multi-Ticket feature, keep inner-loop checks focused per Ticket, then run
the appropriate integration/regression suite after all dependency-related
Tickets are GREEN. When a later fix changes behavior, rerun the affected Test checks before the next redaction, commit, and push.

## Report

Return a concise report:

```markdown
## Test Report

- Scope: <ticket/feature>
- Mode: tiny / normal / RED-GREEN / browser
- Level: minimal / focused / regression / full
- Result: pass / partial / fail / blocked

### Acceptance-to-test matrix

| Acceptance criterion | Risk | Required dimension | Evidence | Result |
|---|---|---|---|---|
| ... | ... | ... | command/test/observed behavior | pass/fail/blocked |

### Test Quality Gate

| Dimension | Result | Evidence / N/A reason |
|---|---|---|
| Acceptance coverage | pass/fail | ... |
| Boundary coverage | pass/fail/N/A | ... |
| Negative-path coverage | pass/fail/N/A | ... |
| Regression protection | pass/fail/N/A | ... |
| Integration/contract | pass/fail/N/A | ... |
| Property/fuzz | pass/fail/N/A | ... |
| Mutation/test-strength | pass/fail/N/A | ... |
| Browser/E2E | pass/fail/N/A | ... |
| Flaky/isolation | pass/fail/N/A | ... |

### Failures
- <root cause, relevant evidence, and next action>
```

Report only checks actually executed. Never claim a test passed when the tool, environment, service, account, or test data was unavailable.

## Community-derived practice

This workflow incorporates recurring practitioner lessons from AI-coding discussions: strict TDD can help on complex/high-risk work but becomes costly when forced onto trivial tasks; focused tests should run before full suites; linters/type checks provide cheap feedback; browser automation is expensive and flaky when used as the default loop; and test expectations should be decided before exploratory execution so agents do not spend repeated rounds discovering what to assert.
