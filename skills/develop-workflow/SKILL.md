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
- When several dependency-ready Slices or bounded implementation tasks exist,
  apply the adaptive execution-wave policy in `AGENTS.md`: the main agent
  decides at runtime whether to work directly or delegate, how much concurrency
  is useful, and which available agent best matches each task.
- Confirm the smallest useful local validation before editing.
- Load the Requirement IDs covered by the current Slice and the originating
  Requirement Contract before changing code. Slice acceptance criteria do not
  replace the originating requirement.
- Use test-first development when a meaningful failing test can be written for
  behavior changes, bug fixes, regressions, API behavior, core business logic,
  data processing, or high-risk code. Use direct focused validation instead for
  documentation, configuration, dependency, styling, typo, and simple refactor
  work; do not force a RED test there.
- Make the minimum change that satisfies both the Slice acceptance criteria
  and its originating Requirement IDs.
- Do not add behavior that cannot be traced to a Requirement ID or an explicit
  verified repository constraint.
- Run focused local validation and fix failures whose cause is clear.
- Refactor only inside the Slice, and only after its acceptance criteria pass.
- Integrate the material results of each execution wave before scheduling the
  next wave; recompute dependency readiness from fresh evidence.
- Keep overlapping writes, unresolved dependencies, and shared interface,
  schema, migration, or configuration changes sequential.
- Stop and re-plan when implementation exposes a wrong design assumption or a
  conflict between the Plan and the originating Requirement Contract instead
  of adapting the requirement to fit the implementation or growing the patch.

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
