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

`Requirement -> Understand -> Plan -> Slice -> Execute/Test -> Integrate -> Review -> State/Docs if needed -> Redact if needed -> Commit/Push -> Notify`

Use `codex-development-workflow` to orchestrate the lifecycle.

For each slice:

`Acceptance Criteria -> Test Strategy -> Minimal Change -> Focused Validation -> Complete`

* Work on one clear functional unit at a time.
* Split complex or dependency-driven work into small, independently verifiable slices.
* Run the smallest validation set that provides sufficient evidence.
* Use test-first development when it materially improves correctness, especially for bugs, regressions, business logic, APIs, and high-risk behavior.
* Do not force strict TDD, planning, or ticket overhead onto trivial changes.
* If an implementation exposes an incorrect design assumption, re-plan instead of expanding the patch.
* Do not mix unrelated features, refactors, formatting, or dependency upgrades.

## Skill Routing

| Situation                                                              | Skill                        |
| ---------------------------------------------------------------------- | ---------------------------- |
| Non-trivial repository development lifecycle                           | `codex-development-workflow` |
| Large, unfamiliar, or context-heavy repository exploration             | `context-efficiency`         |
| Complex, multi-step, dependent, or incremental work                    | `plan-to-ticket`             |
| Feature, bug fix, regression, integration, or browser validation       | `test-workflow`              |
| Architecture or flow visualization materially improves understanding   | `plantuml-skill`             |
| Verified repository state materially changed                           | `repo-current-state`         |
| Potentially sensitive output crosses a sharing or publication boundary | `data-document-redaction`    |
| Deployment, release automation, rollout verification, or rollback      | `auto-deploy`                |
| Commit or push is required                                             | `github-push-when-ready`     |
| Implementation and required validation are complete                    | `bark-finish-notify`         |

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

After implementation and required validation are complete, invoke `bark-finish-notify` once before the final response.
