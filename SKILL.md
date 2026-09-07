---
name: codex-development-workflow
description: "Orchestrate an end-to-end Codex development workflow using the user's GitHub skills: context-efficiency, plan-to-ticket, frontend-click-test when applicable, code-review, repo-current-state, and github-push-when-ready. Use for feature development, bug fixes, refactors, and repository changes that should follow a gated Plan, Ticket, Implement, Test, Review, State, Commit, and Push lifecycle."
---

# Codex Development Workflow

Coordinate the specialist skills. Do not duplicate their detailed logic.

## Pipeline

Use this order for non-trivial repository work:

1. `context-efficiency` — establish the minimum working context and keep it compact.
2. `plan-to-ticket` — convert the requested change into dependency-ordered tickets.
3. Implement exactly one ticket.
4. Run the relevant test skill or project tests.
5. For frontend interaction changes, run `frontend-click-test`.
6. Run `code-review` as the review gate.
7. If review changes code, re-run affected tests and review again when meaningful.
8. Run `repo-current-state` to reconcile `docs/Repo_Current_State.md` with verified repository truth.
9. Run `github-push-when-ready` before every commit or push.
10. Continue with the next ticket only after the current ticket is complete and safely published.

## Gates

Do not advance past a failed gate.

### Test failure

`Implement -> Test FAIL -> Fix -> Retest`

Do not review or publish known failing work unless the user explicitly requests a failing-state diagnostic or WIP publication.

### Review failure

`Review FAIL -> Fix -> Retest -> Review again`

A review finding that requires a code change invalidates prior test evidence for the affected behavior.

### State gate

Update repository state only after implementation and required verification are complete. Keep implementation, relevant tests, and the corresponding current-state update in one coherent commit when they describe the same work unit.

### Publish gate

Never bypass `github-push-when-ready` for commit or push actions.

## Ticket Discipline

- Work on one ticket at a time.
- Do not implement future-ticket functionality opportunistically.
- Keep unrelated refactors out of the ticket.
- Prefer one coherent ticket or functional unit per commit.
- Preserve explicit dependencies between tickets.

## Skill Resolution

Read `references/skill-map.md` when exact GitHub repository paths or install locations are needed.

If a specialist skill is unavailable locally, report the missing skill instead of silently replacing it with a weaker workflow. The repository provides `scripts/install-all.sh` to install the complete workflow skill set.

## Installation

Install all workflow skills into Codex with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

Update existing installations with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Codex uses `${CODEX_HOME:-$HOME/.codex}/skills` by default. Restart Codex after installation so newly installed skills are discovered.

## Completion

A ticket is complete only when:

- its acceptance criteria are met;
- relevant tests have passed or an explicit blocker is recorded;
- required frontend browser verification has passed when applicable;
- code review has no unresolved blocking findings;
- `docs/Repo_Current_State.md` is current when repository state changed; and
- commit/push readiness has passed before publication.
