# AGENTS.md

This file defines repository-wide engineering principles, the development lifecycle, and when specialist Skills must be invoked.

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

Use the lightest workflow that preserves correctness.

For non-trivial work:

`Requirement -> Understand repo -> Plan -> Record Plan + Tickets + Slices -> Create Plan branch -> Implement -> Test -> Redaction scan if applicable -> Commit -> Push branch -> Create / Update Plan PR -> Merge once -> Delete branch -> Update main -> Close Plan + Tickets -> Update State/Docs -> If separately authorized: external release handoff (outside this workflow)`

Use `codex-development-workflow` to orchestrate the lifecycle.

For each slice:

`Acceptance Criteria -> Test Strategy -> Minimal Change -> Focused Validation -> Complete`

* Work on one clear functional unit per agent at a time; independent Slices may run in parallel only when their ownership boundaries are disjoint.
* Record exactly one GitHub Issue Plan for each requirement before creating its Plan branch, regardless of whether the change is Docs, Code, Tests, Config, Refactor, Bugfix, Feature, Dependency, or CI/CD. A Plan may contain one or more behavior Ticket Issues; split each Ticket into independently verifiable Slices.
* Every change type uses the same Plan-branch and PR gate: docs, code, tests, configuration, refactors, bug fixes, features, dependencies, and CI/CD changes must not bypass the PR.
* Split complex or dependency-driven work into small, independently verifiable slices.
* Run the smallest validation set that provides sufficient evidence.
* Use test-first development when it materially improves correctness, especially for bugs, regressions, business logic, APIs, and high-risk behavior.
* Do not force strict TDD or multi-Slice decomposition onto trivial changes; a tiny requirement is one Plan with one Ticket and one implicit Slice, and it still requires one branch and PR.
* When the user explicitly requests workflow timing, record measured monotonic wall-clock duration for each externally observable gate and the total run; report the dominant latency source. Timing is observational, does not add a delivery gate, and must not persist session-specific timing logs.
* If an implementation exposes an incorrect design assumption, re-plan instead of expanding the patch.
* Do not mix unrelated features, refactors, formatting, or dependency upgrades.

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
| Non-trivial repository development lifecycle                           | `codex-development-workflow` |
| Complex, multi-step, dependent, or incremental work                    | `plan-to-ticket`             |
| Feature, bug fix, regression, integration, or browser validation       | `test-workflow`              |
| Architecture or flow visualization materially improves understanding   | `plantuml-skill`             |
| Verified repository state materially changed                           | `repo-current-state`         |
| Every change (documentation impact check), or docs need normalizing    | `repo-documentation`         |
| Files staged for a commit or PR may contain credentials or personal data | `data-document-redaction`    |
| Branch publication, Commit, Push, or PR readiness is required           | `github-push-when-ready`     |

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
