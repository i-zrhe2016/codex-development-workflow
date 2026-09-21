# AGENTS.md

This file defines repository-wide engineering principles, the development workflow stages, and when specialist Skills must be invoked.

Detailed procedures belong in each Skill's `SKILL.md`. Do not duplicate them here.

## Principles

Priority:

`Correctness -> Simplicity -> Architecture Clarity -> Maintainability -> Extensibility`

* Follow Occam's razor: prefer the simplest necessary and maintainable solution.
* Understand the existing architecture before making non-trivial changes.
* Prefer minimal changes, existing capabilities, mature frameworks, and clear interfaces.
* Do not introduce speculative abstractions, services, features, or dependencies.
* Keep responsibilities and module/service boundaries clear.
* Fix root causes instead of hiding problems with additional complexity.

## Documentation

* Keep `README.md` as the project introduction and documentation index.
* Put detailed documentation under `docs/`.
* Keep documents focused on one module or topic.
* Update documentation only when verified behavior, architecture, interfaces, dependencies, deployment, or important project state changes.

## Development Workflow

Use the lightest workflow that preserves correctness. Work is routed to the
stage that owns it rather than running one fixed chain for every request.

| Situation | Stage |
| --- | --- |
| A requirement needs understanding, design, or decomposition | `plan-workflow` |
| Repository content must change | `develop-workflow` |
| Acceptance, a regression, or a branch needs proof | `verify-workflow` |
| A verified change must be committed, pushed, or turned into a PR | `publish-workflow` |
| A ready PR must be merged, cleaned up, or reconciled | `integrate-workflow` |
| The user explicitly authorizes a complete end-to-end delivery | the full orchestration in `codex-development-workflow` |

Feature, bug fix, refactor, and documentation work are profiles of these stages,
not separate workflows.

Persist a Plan Issue with one or more child Ticket Issues before branch work
when the work is complex, must survive a session boundary, or the user asks for
a persisted plan. A persisted Plan owns one branch, one PR, and one merge for
all of its Tickets; split each Ticket into independently verifiable Slices.

`codex-development-workflow` routes to these stages and carries the invariants
that hold in all of them. Its full orchestration is the only path that runs
several stages as one authorized delivery.

## Multi-Agent Delegation

Use subagents only when delegation materially improves speed, context isolation, or implementation quality.

The main agent owns:

* requirements;
* architecture and design decisions;
* planning and task decomposition;
* dependency ordering;
* integration;
* final judgment.

Delegate work only when the task is bounded and independently executable.

Keep dependent or overlapping work sequential.

Parallel write tasks must have clearly separated scope and should not modify the same files, interfaces, schemas, migrations, or shared configuration.

Each delegated task must define:

* goal;
* scope and out-of-scope;
* relevant files or ownership boundary;
* dependencies;
* acceptance criteria;
* validation;
* expected result summary.

Subagents should return material findings, changes, test results, and unresolved risks rather than raw logs.

The main agent must not duplicate work already delegated to an active subagent.

Prefer a single delegation level. Subagents should not create further subagents unless explicitly required.

### Who chooses the subagent

The host selects the subagent, not this document. Do not map a task class to a
named agent here or anywhere else in the repository.

* Codex selects from the agent definitions under `.codex/agents/`.
* Claude Code selects from the agent definitions under `.claude/agents/`,
  using each definition's `description` as the only selection signal.

Write an agent's `description` so that it states the exact trigger the agent
serves. An agent that must not run on ordinary work has to say so in its
description, because the host has no other rule to consult.

Each host also ships its own built-in agent types, and those remain available
for bounded delegation when the host selects one.

This section owns the delegation policy. Other documents link to it rather than
restating it.

## Skill Routing

| Situation                                                              | Skill                        |
| ---------------------------------------------------------------------- | ---------------------------- |
| Routing a request to its stage, or an authorized end-to-end delivery   | `codex-development-workflow` |
| Planning, designing, or decomposing before changes                     | `plan-workflow`              |
| Implementing or modifying repository content                           | `develop-workflow`           |
| Verifying acceptance, a regression, or a branch                        | `verify-workflow`            |
| Committing, pushing, or preparing a pull request                       | `publish-workflow`           |
| Merging, cleaning up, or reconciling after delivery                    | `integrate-workflow`         |
| Complex, multi-step, dependent, or incremental work needs a Plan/Ticket/Slice breakdown | `plan-to-ticket` |
| Feature, bug fix, regression, integration, or browser validation       | `test-workflow`              |
| Architecture or flow visualization materially improves understanding   | `plantuml-skill`             |
| Verified repository state materially changed                           | `repo-current-state`         |
| Every change (documentation impact check), or docs need normalizing    | `repo-documentation`         |
| Files staged for a commit or PR may contain credentials or personal data | `data-document-redaction`    |
| Branch publication, Commit, Push, or PR readiness is required          | `github-push-when-ready`     |

## Skill Rules

* Invoke Skills only when their trigger applies.
* Prefer the most specific applicable Skill.
* Follow the invoked Skill's `SKILL.md`.
* Do not duplicate Skill procedures here.
* Multiple Skills may be invoked when independent triggers apply.
* If a required Skill is unavailable, report it instead of inventing a replacement.

## Repository Rules

* Keep architecture and dependencies as simple as practical.
* One commit should represent one clear purpose.
* Never commit passwords, tokens, credentials, private keys, `.env`, or other secrets.
* Do not commit local `AGENTS.md` or `CLAUDE.md` unless the repository intentionally versions them.

## Completion

A change is complete only after all applicable workflow gates have passed.
