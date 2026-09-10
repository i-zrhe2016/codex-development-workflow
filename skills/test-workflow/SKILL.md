---
name: test-workflow
description: "General repository testing workflow for Codex. Use when validating feature work, bug fixes, refactors, or ticket acceptance criteria across backend, frontend, APIs, libraries, and CLI projects. Select the cheapest relevant checks first, support test-first RED/GREEN loops for complex or risky behavior, run focused tests before broader regression suites, use real-browser Playwright verification only for browser-visible behavior, and return actionable failure evidence without masking failures with retries or weak assertions."
---

# Test Workflow

Validate behavior with the lightest reliable test strategy. This skill owns the
Test stage for every change and for each blocking Automatic Review fix; it does
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

Run the smallest set that provides sufficient evidence for the selected level.
After it passes, stop by default. Escalate only when acceptance criteria,
failure evidence, an affected boundary, release requirements, or the user
justifies broader validation.

## Choose the testing mode

Use task risk and complexity to choose the test strategy, not to choose a
different delivery path. Every change still continues through the common branch,
redaction when applicable, commit, push, PR, Automatic Review, and merge gates.

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

Prefer 3-7 high-value cases over a large low-signal matrix. Cover contracts, boundaries, state transitions, and failure handling first.

## Test ladder

Run checks in this order when applicable:

1. **Static feedback:** compiler, typecheck, lint, schema/config validation.
2. **Focused automated tests:** the smallest unit/component/API/package tests covering the changed behavior.
3. **Integration tests:** service, database, filesystem, queue, network, or multi-module boundaries touched by the change.
4. **Broader regression:** affected package/module suite; full suite only when justified by change scope or project policy.
5. **Browser/E2E:** only for browser-visible behavior that lower-level tests cannot establish.

Stop at the first useful failure and diagnose it before spending resources on higher layers.

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

## Failure handling

Classify a failure before changing code:

- **Implementation defect:** product behavior violates the requirement -> fix the smallest relevant production code.
- **Test defect:** assertion, fixture, selector, or test setup contradicts the verified requirement -> fix the test, not the product.
- **Regression:** unrelated expected behavior broke -> fix or stop if outside scope.
- **Environment/data failure:** dependency, service, account, fixture, permission, network, or test data unavailable -> mark blocked; do not fake a code fix.
- **Requirement/design conflict:** expected behavior is ambiguous or the architecture assumption is wrong -> stop expanding the patch and re-plan.

For ordinary failures with a clear cause, fix and rerun the focused test. Escalate to targeted code review/root-cause analysis when the same failure repeats without new evidence, the cause remains unclear, or the change is high-risk. Do not use code review as the first response to every red test.

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

A Ticket or ticketless Slice is test-complete when:

- each acceptance criterion has concrete test or validation evidence;
- the selected checks for the chosen level are GREEN;
- required integration/browser checks are GREEN;
- failures are either resolved or explicitly classified as blocked/out of scope;
- no test was weakened solely to make the suite pass.

For a multi-Ticket feature, keep inner-loop checks focused per Ticket, then run
the appropriate integration/regression suite after all dependency-related
Tickets are GREEN. When Automatic Review returns blocking findings, rerun the
affected Test checks before the next redaction, commit, push, and review pass.

## Report

Return a concise report:

```markdown
## Test Report

- Scope: <ticket/feature>
- Mode: tiny / normal / RED-GREEN / browser
- Level: minimal / focused / regression / full
- Result: pass / partial / fail / blocked

| Check | Evidence | Result |
|---|---|---|
| ... | command or observed behavior | pass/fail/blocked |

### Failures
- <root cause, relevant evidence, and next action>
```

Report only checks actually executed. Never claim a test passed when the tool, environment, service, account, or test data was unavailable.

## Community-derived practice

This workflow incorporates recurring practitioner lessons from AI-coding discussions: strict TDD can help on complex/high-risk work but becomes costly when forced onto trivial tasks; focused tests should run before full suites; linters/type checks provide cheap feedback; browser automation is expensive and flaky when used as the default loop; and test expectations should be decided before exploratory execution so agents do not spend repeated rounds discovering what to assert.
