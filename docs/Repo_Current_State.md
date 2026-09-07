# Repository Current State

Last verified: 2026-09-08 @ working tree

## Current Focus
- TDD-driven adaptive Codex development workflow.

## Implemented
- The orchestrator selects tiny, normal, or complex paths instead of forcing tickets on every change.
- Complex work uses dependency-ready Ticket Loops with function checklists, test cases, RED/GREEN feedback, and minimum-scope implementation.
- Ordinary test failures are diagnosed directly; targeted `codex review` is reserved for repeated/unexplained failures, high-risk changes, or design conflicts.
- One final review runs after integration tests, state/docs reconciliation, and any required redaction, before commit/push.

## Constraints
- Code review requires an installed and authenticated Codex CLI.
- Specialist test behavior remains owned by the relevant test skill.
- Installation follows specialist repositories' default branches rather than pinned commits.

## Architecture Snapshot
- `SKILL.md` owns task classification, orchestration, Ticket Loop policy, review escalation, and completion gates.
- `plan-to-ticket` owns ticket generation; relevant test skills own test procedures.
- `repo-current-state`, `data-document-redaction`, and `github-push-when-ready` remain conditional specialist gates.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.

## Next
- Update `plan-to-ticket` so generated tickets consistently expose function checklists and test cases.
- Update relevant test skills for explicit RED/GREEN behavior where appropriate.
