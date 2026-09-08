# Repository Current State

Last verified: 2026-09-08 @ working tree

## Current Focus

- [Plan #9](https://github.com/i-zrhe2016/codex-development-workflow/issues/9): make GitHub Issues the mandatory durable authority for plans and tickets; finish T0001/T0002 on the stacked feature branches.

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
- Project-scoped `.codex/config.toml` enables subagents with a three-thread concurrency cap; `.codex/agents/reviewer.toml` provides an optional read-only integrated-change reviewer.
- Built-in `codex review` and the project-scoped `reviewer` are documented as separate review paths; the latter is explicitly requested from an interactive Codex session.
- `Repo_Current_State.md` is the compact recovery point; ticket detail and lifecycle metadata remain in GitHub Issues.

## In Progress

- [T0001 / Issue #10](https://github.com/i-zrhe2016/codex-development-workflow/issues/10) is in progress on `feature/t0001-github-issues-persistence`; the core `plan-to-ticket` persistence contract is committed as `56d1ed3`, with no PR opened yet.
- [T0002 / Issue #11](https://github.com/i-zrhe2016/codex-development-workflow/issues/11) is in progress on `feature/t0002-issues-authority-docs`; supporting workflow, state, documentation, and diagram updates are present in the working tree.

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

- Open a review PR for [T0001 / Issue #10](https://github.com/i-zrhe2016/codex-development-workflow/issues/10), then review the stacked [T0002 / Issue #11](https://github.com/i-zrhe2016/codex-development-workflow/issues/11) branch before merging and closing the Issues.
