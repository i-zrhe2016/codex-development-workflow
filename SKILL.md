---
name: codex-development-workflow
description: "Entry point for repository-wide Codex development. Use for non-trivial feature work, bug fixes, refactors, and repository changes. Classify task complexity, route complex work through plan-to-ticket and test-driven ticket loops, escalate code review when tests are repeatedly or unexpectedly failing, run a final review before commit/push, and invoke redaction before sensitive content crosses a sharing boundary."
---

# Codex Development Workflow

Use this skill as the orchestration layer for repository development. Specialist skills own their detailed procedures; this skill owns routing, gates, and completion order.

## Core principle

Use the lightest workflow that preserves correctness.

- **Tiny:** implement -> relevant tests -> completion gates.
- **Normal:** minimal plan -> implement -> relevant tests -> completion gates.
- **Complex:** understand -> minimal design -> plan/tickets -> TDD ticket loop -> integration tests -> completion gates.

Do not create tickets when ticket management costs more than the complexity it removes.

## Complex-work lifecycle

`Requirement -> Understand -> Minimal design -> Plan/Tickets -> TDD Ticket Loop -> Integration test -> Update state/docs -> Classify outputs -> Redact when needed -> Final review -> Commit/Push`

### TDD Ticket Loop

For each dependency-ready ticket, work on one ticket at a time.

1. Read the ticket goal, scope, function checklist, acceptance criteria, test cases, dependencies, and validation command.
2. Load only the repository context required for that ticket.
3. Invoke `test-workflow` to create or confirm the smallest meaningful tests from the specified behavior.
4. For complex/high-risk behavior, confirm the new behavior is not already satisfied (`RED`) when a meaningful failing test can be produced.
5. Implement the minimum necessary change.
6. Use `test-workflow` to run the smallest relevant checks until the ticket is `GREEN`.
7. Diagnose ordinary failures directly. Fix the implementation or test when the cause is clear.
8. Escalate to targeted code review only when a failure is repeated, unexplained, risky, or indicates a design/architecture conflict.
9. If the design assumption is wrong, stop expanding the patch and re-plan or split the ticket.
10. Mark the ticket complete only when its acceptance criteria and relevant tests pass, then select the next unblocked ticket.

Tests are the primary inner-loop feedback mechanism. Code review is not a mandatory per-ticket tax.

## Review policy

Use the Codex CLI built-in review command.

- `codex review --uncommitted`: review the working tree.
- `codex review --base BRANCH`: review against a base branch.
- `codex review --commit SHA`: review an explicit commit.

Run a **targeted review** during development when tests fail repeatedly or unexpectedly, the root cause is unclear, or the change is high-risk.

Run one **final review** after integration tests, state/docs reconciliation, and any required redaction are complete. Fix blocking findings, rerun affected tests, and repeat the final review only when the fix materially changed the reviewed behavior.

Do not use review as a replacement for tests, compiler diagnostics, linting, or static analysis.

## Specialist Skills

Invoke a specialist only when its trigger applies. Follow its own `SKILL.md`; do not duplicate its procedure here.

- `context-efficiency`: large, unfamiliar, or context-heavy repository exploration.
- `plan-to-ticket`: complex multi-step or dependency-driven work; tickets should expose function checklist, acceptance criteria, test cases, dependencies, and validation.
- `test-workflow`: general validation for behavior changes. It selects static, focused, integration/regression, and conditional browser/E2E checks; use RED/GREEN for complex or high-risk behavior rather than forcing strict TDD on every trivial change.
- `repo-current-state`: verified architecture, behavior, dependencies, deployment, or important repository state changed.
- `data-document-redaction`: content may contain personal information, credentials, secrets, or business-sensitive data before sharing/publishing boundaries.
- `github-push-when-ready`: before commit or push.

Read `references/skill-map.md` only when repository sources or install locations are needed.

If a required specialist is unavailable, report it instead of silently replacing its workflow.

## Completion gates

After implementation work is GREEN:

1. Use `test-workflow` to run integration or broader regression tests appropriate to the total change, including browser/E2E only when required by user-visible behavior.
2. Update repository state/docs only when verified behavior, architecture, dependencies, deployment, or important state changed.
3. Classify the complete output set before staging, committing, sharing, exporting, uploading, or publishing.
4. If potentially sensitive surfaces exist, invoke `data-document-redaction`; proceed only on `pass`.
5. Run the final code review on the final safe diff.
6. Fix blocking findings and rerun affected tests through `test-workflow`.
7. Invoke `github-push-when-ready` and commit/push only when all gates are clear.

## Redaction gate contract

Include source files, documentation, logs, configs, screenshots, exports, filenames, and metadata in classification.

- Record recipient/environment, purpose, required utility, and whether controlled reversibility is allowed.
- Assume non-reversible handling unless the task explicitly requires controlled traceability.
- If no potentially sensitive surface is in scope, record the inspected scope and skip reason.
- If sensitive content may be in scope, follow `docs/workflow/redaction.md` and the `data-document-redaction` skill.
- `needs_review` or `blocked` stops commit, push, sharing, and publication.
- Reports contain safe evidence only: types, counts, location categories, hashes, tool versions, coverage, utility checks, and residual risks. Never include original secrets or mappings.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

Update existing installations:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Codex uses `${CODEX_HOME:-$HOME/.codex}/skills` by default. Restart Codex after installation.
