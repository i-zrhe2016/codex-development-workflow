# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for non-trivial repository work. The orchestrator chooses the lightest path that preserves correctness.

## Task paths

- **Tiny:** `Implement -> Relevant tests -> Completion gates`
- **Normal:** `Minimal plan -> Implement -> Relevant tests -> Completion gates`
- **Complex:** `Understand -> Minimal design -> Plan/Tickets -> TDD Ticket Loop -> Integration tests -> Completion gates`

Tickets are a complexity-control tool, not mandatory ceremony.

## TDD Ticket Loop

For complex work, select one dependency-ready ticket at a time. Each ticket should expose its goal, scope, function checklist, acceptance criteria, test cases, dependencies, and validation command.

`Ticket -> tests/spec -> RED when meaningful -> minimum implementation -> GREEN -> next ticket`

Use tests, compiler diagnostics, linting, and static analysis as the primary inner feedback loop. Ordinary test failures should be diagnosed and fixed directly.

Escalate to targeted `codex review` only when a failure is repeated or unexplained, the root cause is unclear, the patch is high-risk, or the failure exposes a design/architecture conflict. Re-plan instead of growing the patch when the ticket assumptions are wrong.

After all tickets are GREEN, run integration/regression tests across the complete change set.

## Review policy

The final review is a completion gate, not a mandatory step inside every ticket iteration.

- `codex review --uncommitted` reviews the working tree.
- `codex review --base BRANCH` reviews against a base branch.
- `codex review --commit SHA` reviews a specific commit.

After a blocking review fix, rerun the affected tests. Repeat the final review when the fix materially changes the reviewed behavior.

## Output classification and redaction

Classify the complete final output set before staging or committing and before every separate sharing, export, upload, or publication boundary. Include source, docs, logs, configs, images, screenshots, exports, filenames, and metadata.

Record recipient/environment, purpose, required utility, and whether controlled reversibility is allowed. Default to non-reversible handling.

If no potentially sensitive surface exists, record the inspected scope and skip reason. Otherwise invoke `data-document-redaction` and follow [redaction.md](redaction.md). Only `pass` advances; `needs_review` and `blocked` stop the boundary transition.

## Completion order

`Integration tests -> Repo state/docs if needed -> Output classification -> Redaction if needed -> Final review -> Commit/Push`

For specialist repositories and installation locations, see [`../../references/skill-map.md`](../../references/skill-map.md).
