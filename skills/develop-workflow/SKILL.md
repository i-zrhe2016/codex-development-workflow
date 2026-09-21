---
name: develop-workflow
description: "Decide WHEN to implement. Take an executable work definition to Development Complete: understand the affected code, make the minimal change, and validate it locally. Use when the request is to implement, fix, refactor, or change repository content. It stops before publication and never commits, pushes, opens a pull request, merges, closes an Issue, or updates repository state."
---

# Develop Workflow

Stage workflow for the **context -> implementation -> Development Complete**
transition.

## Responsibility

- Load only the context the Slice needs: the affected files, their direct
  dependencies, the relevant tests, and the current repository state.
- Confirm the smallest useful local validation before editing.
- Use test-first development when a meaningful failing test can be written for
  behavior changes, bug fixes, regressions, API behavior, core business logic,
  data processing, or high-risk code. Use direct focused validation instead for
  documentation, configuration, dependency, styling, typo, and simple refactor
  work; do not force a RED test there.
- Make the minimum change that satisfies the Slice acceptance criteria.
- Run focused local validation and fix failures whose cause is clear.
- Refactor only inside the Slice, and only after its acceptance criteria pass.
- Stop and re-plan when implementation exposes a wrong design assumption
  instead of growing the patch.

## Development Complete

A Slice reaches Development Complete when its acceptance criteria are
implemented and its focused local validation passes. Report the Slice, the
files changed, the commands run with their results, and any unresolved risk.

## Not responsible for

- choosing the verification breadth that acceptance requires — that is
  `verify-workflow`;
- committing, pushing, opening a pull request, or merging — those are
  `publish-workflow` and `integrate-workflow`;
- closing Issues, refreshing `docs/Repo_Current_State.md`, or running the
  post-delivery process evaluation;
- unrelated refactors, formatting sweeps, dependency upgrades, or future-Slice
  work.
