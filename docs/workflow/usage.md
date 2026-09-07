# Workflow Usage Guide

## When to use it

Use this skill for non-trivial feature work, bug fixes, refactors, and
repository changes that need a repeatable path from planning to publication.
For a small, self-contained change, apply only the gates relevant to the
change.

## Lifecycle

| Stage | Invoked skill or tool | Purpose | Required outcome |
|---|---|---|---|
| Context | `context-efficiency` | Establish the minimum repository context. | Relevant architecture, files, constraints, and existing behavior are understood. |
| Plan / Ticket | `plan-to-ticket` | Turn the request into dependency-ordered work. | One current ticket with explicit acceptance criteria. |
| Implement | Codex / target repository | Change only the current ticket. | The requested behavior is implemented without unrelated refactoring. |
| Test | Project tests or relevant test skill | Run the relevant project or specialist tests. | Tests pass, or a concrete blocker is recorded. |
| Frontend verification | `frontend-click-test` (conditional) | Run the real-browser click test when interaction behavior changed. | The required user path passes in Chromium. |
| Review | `code-review` | Run the code-review gate. | No unresolved blocking findings remain. |
| Repo State | `repo-current-state` | Reconcile the repository state documentation. | `docs/Repo_Current_State.md` is current when the target repository uses it. |
| Commit / Push | `github-push-when-ready` | Check repository readiness before publication. | The change is ready for a focused commit or push. |

The frontend verification stage is conditional. It is not a substitute for
project tests, and it is not required for backend-only or documentation-only
changes.

## Gate rules

### Test gate

If tests fail, fix the affected behavior and rerun the tests before review or
publication. Do not publish known failing work unless the user explicitly asks
for a failing-state diagnostic or work-in-progress publication.

### Review gate

If review identifies a code-changing issue, rerun the affected tests and review
the result again when the change is meaningful.

### State gate

Update repository-state documentation only after implementation and required
verification are complete. Keep the implementation, relevant tests, and the
corresponding state update together when they describe one coherent work unit.

### Publish gate

Before committing or pushing, check the repository status and diff scope. Keep
one functional unit per commit and do not include secrets, local credentials,
or unrelated changes.

## Ticket discipline

- Work on one ticket at a time.
- Preserve explicit dependencies between tickets.
- Do not implement future-ticket functionality opportunistically.
- Keep unrelated formatting, dependency upgrades, and refactors out of the
  current ticket.

## Completion checklist

Before calling a ticket complete, confirm:

- acceptance criteria are met;
- relevant tests have passed or an explicit blocker is documented;
- real-browser verification passed when the change affects frontend behavior;
- code review has no unresolved blocking findings;
- repository-state documentation is current when applicable; and
- commit/push readiness has been checked before publication.
