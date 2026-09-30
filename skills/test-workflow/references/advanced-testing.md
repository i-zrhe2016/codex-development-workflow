# Advanced Testing Paths

Load only the section required by the current risk profile.

## Property / fuzz

Use for parsers, transformations, numerical logic, codecs, validation, protocol handling, complex input spaces, or strong invariants.

Define the invariant/oracle before generating inputs. Keep and minimize any failing seed as a deterministic regression test. "Did not crash" is sufficient only when crash-freedom is the contract.

## Mutation / test-strength

Use for high-risk business logic or suspiciously weak tests. Prefer changed/high-risk modules over repository-wide mutation.

A meaningful surviving mutation indicates weak assertions, missing cases, or unreachable code. Strengthen the test or document why the mutation is equivalent/not relevant. Do not chase a universal mutation score.

## Browser / E2E

Use only when browser-visible interaction changed or acceptance explicitly requires an end-to-end flow.

Prefer the repository's existing browser harness. Prove the smallest critical user flow, starting from known URL/session/data state. Prefer role/label/accessibility/test-id selectors, wait for application state rather than fixed sleeps, and capture useful failure evidence such as screenshot/URL/console/request/trace.

Do not mark browser behavior passed from source inspection, curl, static HTML, or screenshot alone. Avoid destructive production actions unless explicitly authorized in a safe environment.

## Flaky / isolation

A retry is diagnostic evidence, never a PASS mechanism. If identical code/test state produces FAIL then PASS without a verified external cause, keep the gate blocked/partial until nondeterminism is understood, explicitly quarantined by project policy, or fixed.

Prefer deterministic clocks, seeded randomness, isolated fixtures, unique test data, state/event waits, and hermetic dependencies. Never add blind retries or fixed sleeps to convert flakiness into GREEN.
