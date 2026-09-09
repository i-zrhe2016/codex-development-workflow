# Repository Current State

Last verified: 2026-09-09 @ working tree

## Current Focus

- Per-ticket branch setup and one PR-stage review gate are active in the workflow on `docs/pr-review-gate`.

## Implemented

- The workflow classifies work, understands the current repository, plans small Slices, optionally delegates independent bounded work, integrates, reviews, and delivers.
- Normal and complex Slices define scope, exclusions, dependencies, acceptance criteria, relevant context, test strategy, verification level, test cases, and validation commands.
- Verification levels are `minimal`, `focused`, `regression`, and `full`; focused is the default and passing evidence stops expansion unless escalation is justified.
- Test-first behavior is conditional on meaningful behavioral risk; non-behavioral changes use direct minimal validation.
- The installer packages eight local skills from the root skill and `skills/`; specialist repositories are not cloned at install time.
- Specialist documentation for all seven managed specialist skills (`plan-to-ticket`, `test-workflow`, `repo-current-state`, `context-efficiency`, `data-document-redaction`, `github-push-when-ready`, and `auto-deploy`) is grouped under `docs/skills/`; committed diagram sources and renderings are retained where applicable.
- `github-push-when-ready` enforces a per-repository non-root identity policy; this repository is configured for `i-zrhe2016` and verifies the same GitHub account and push credentials before publishing.
- The publication workflow verifies a PR is merged before deleting its source branch remotely and locally; the default branch is retained.
- `auto-deploy` defines a provider-neutral deployment contract with immutable artifacts, bounded health verification, least-privilege credentials, and authorized rollback handling.
- Project-scoped `.codex/config.toml` enables subagents with a three-thread concurrency cap; `.codex/agents/reviewer.toml` provides the single PR-stage read-only reviewer.
- Built-in `codex review` and the project-scoped `reviewer` are documented as alternative paths for the single PR-stage review; the latter is explicitly requested from an interactive Codex session.
- `Repo_Current_State.md` is the compact recovery point; ticket detail and lifecycle metadata remain in GitHub Issues.
- `plan-to-ticket` now requires a parent plan Issue and one Issue per ticket before branch work, with stable markers, lifecycle metadata, and no Markdown/chat fallback.
- The root workflow now creates or resumes one branch per ticket before implementation and requires one review after the PR is opened and before merge.

## In Progress

- Move the only routine review gate to the PR stage on `docs/pr-review-gate`.

## Constraints

- Code review requires an installed and authenticated Codex CLI.
- Specialist behavior is bundled under `skills/` and installed from this repository's local source.
- `context-efficiency` remains an optional context-loading aid, not a workflow stage.
- Delegation is optional; dependent, overlapping, or shared-interface work remains sequential, and integration/final judgment stay with the main agent.
- `scripts/install-all.sh` requires a complete checkout and copies local bundles; it does not clone specialist repositories.
- Persisted plans and tickets require a resolvable GitHub repository target and an available, authorized GitHub Issues connector; failed required writes block completion without a Markdown fallback.

## Architecture Snapshot

- `SKILL.md` owns main-agent stage routing, the optional Delegation Gate, Slice contract, bounded verification, review policy, delivery gates, and recovery-state guidance.
- `plan-to-ticket` owns dependency-ordered Slice generation and mandatory GitHub Issue persistence; `test-workflow` owns selected verification execution and evidence reporting. Both are managed in `skills/`.
- `docs/skills/` contains explanatory documentation for every managed specialist skill; operational references and scripts remain beside the runtime bundles under `skills/`.
- `repo-current-state`, `data-document-redaction`, and `github-push-when-ready` remain conditional gates.
- `auto-deploy` is a conditional deployment gate and does not own target-project infrastructure or production approvals.
- The parent workflow and `repo-current-state` use GitHub Issues as the durable ticket authority; this file only points to active and next Issues. See `docs/workflow/usage.md` and `docs/skills/plan-to-ticket/architecture.md`.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.

## Next

- Complete the PR-stage review-gate documentation change, then publish it when authorized.
