---
name: test-workflow
description: "Verify repository changes against acceptance criteria with risk-bounded testing. Use for feature, bug-fix, refactor, API, library, CLI, frontend, or backend verification. Map requirements to evidence, run the cheapest relevant checks first, select mandatory risk dimensions, and return PASS/FAIL/BLOCKED through an explicit Test Quality Gate."
---

# Test Workflow

Verify behavior with the lightest reliable evidence. `verify-workflow` decides when/how broadly to invoke this skill; this skill owns the verification procedure.

## Core rules

- Derive checks from requirements, acceptance criteria, and existing public contracts.
- Reuse the repository's existing test tools/fixtures/conventions.
- Run the smallest relevant check first; broaden only when risk/evidence requires it.
- Test observable behavior, not implementation details unless they are the contract.
- Never weaken assertions, remove meaningful tests, add blind retries, or add fixed sleeps to manufacture GREEN.
- Coverage is diagnostic, not proof.

## Level

Choose one bounded level:

- `minimal`: tiny docs/config/style/dependency/typo/simple-refactor work.
- `focused`: default; checks directly tied to changed behavior.
- `regression`: bug fixes, cross-module changes, or demonstrated regression risk.
- `full`: high-risk/release gates or explicit full-suite requirements.

The level bounds breadth; it does not replace the quality gate.

## Procedure

1. List the behavior/acceptance criteria being verified.
2. Select mandatory dimensions from actual risk: happy path, boundary, negative/failure, state/invariant, integration/contract, regression, and—only when justified—property/fuzz, mutation/test-strength, browser/E2E, or isolation/flake.
3. Map every acceptance criterion to planned evidence.
4. Run checks cheapest-first: static/type/lint -> focused tests -> boundary/negative -> integration/regression -> advanced dimensions when applicable.
5. Stop at the first useful failure, classify it, fix only when this invocation owns the fix, then resume from the cheapest check that can disprove the correction.
6. Close the Test Quality Gate and return one result.

Load [references/advanced-testing.md](references/advanced-testing.md) only when property/fuzz, mutation, browser/E2E, or flaky/isolation handling is actually applicable.

## Test mode

Use RED -> GREEN for complex/high-risk behavior when a meaningful failing test can be established before production implementation. For ordinary changes, define/update focused tests and validate directly. Do not force ceremonial TDD on trivial or mechanically verifiable changes.

## Failure classification

- **Implementation defect**: behavior violates requirement.
- **Test defect**: assertion/fixture/setup contradicts the verified requirement.
- **Regression**: unrelated expected behavior broke.
- **Environment/data blocker**: dependency/service/account/permission/test data unavailable.
- **Requirement/design conflict**: expected behavior or architecture assumption is wrong/ambiguous.

A blocked environment is not a product PASS.

## Test Quality Gate

Return `PASS` only when:

- every acceptance criterion maps to executed evidence;
- every mandatory risk dimension is GREEN or explicitly N/A with a concrete reason;
- the selected level's checks are GREEN;
- no unexplained flaky FAIL is erased by a retry;
- no test was weakened only to pass.

Otherwise return `FAIL` for failed evidence or `BLOCKED` when required verification could not run.

## Report

Keep the report compact:

```markdown
## Test Report
- Scope: <Slice/Ticket/branch>
- Level: minimal | focused | regression | full
- Result: PASS | FAIL | BLOCKED

| Acceptance criterion | Required dimension | Evidence | Result |
|---|---|---|---|
| ... | ... | command/test | ... |

Blockers/failures: <only when present>
```

Report only checks actually executed.
