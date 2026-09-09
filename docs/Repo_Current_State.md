# Repository Current State

Last verified: 2026-09-09 @ working tree

## Current Focus

- The unified PR-gated workflow is being applied to every change type; the
  working tree contains the corresponding process, documentation, diagram, and
  default-branch guard updates.

## Implemented

- The workflow now runs Requirement -> Understand repo -> Plan -> Slice/Ticket
  if needed -> Create feature branch -> Implement -> Test -> applicable
  Redaction -> Commit -> Push -> Create/Update PR -> Automatic Review -> Fix
  loop when blocked -> Merge -> branch cleanup/default synchronization -> State/
  Docs -> Deploy if needed.
- Docs, Code, Tests, Config, Refactor, Bugfix, Feature, Dependency, and CI/CD
  changes all use the feature-branch and PR path; no direct default-branch
  delivery exception remains.
- Complex requirements are split into behavior Tickets before their dependency-ordered Slices; tiny requests may remain one implicit Slice without Ticket overhead.
- A ticketless focused Slice still requires the same branch, test, redaction,
  commit, push, PR, Automatic Review, merge, and cleanup gates.
- Normal and complex Slices define scope, exclusions, dependencies, acceptance criteria, relevant context, test strategy, verification level, test cases, and validation commands.
- Verification levels are `minimal`, `focused`, `regression`, and `full`; focused is the default and passing evidence stops expansion unless escalation is justified.
- Test-first behavior is conditional on meaningful behavioral risk; non-behavioral changes use direct minimal validation.
- The installer packages eight local skills from the root skill and `skills/`; specialist repositories are not cloned at install time.
- Specialist documentation for all seven managed specialist skills (`plan-to-ticket`, `test-workflow`, `repo-current-state`, `context-efficiency`, `data-document-redaction`, `github-push-when-ready`, and `auto-deploy`) is grouped under `docs/skills/`; committed diagram sources and renderings are retained where applicable.
- `github-push-when-ready` enforces a per-repository non-root identity policy; this repository is configured for `i-zrhe2016` and verifies the same GitHub account and push credentials before publishing.
- The publication workflow requires a non-default feature branch, verifies a PR
  is merged before deleting its source branch remotely and locally, and retains
  the default branch.
- The readiness utility blocks local changes or unpublished commits on the
  resolved default branch and directs the work to a feature branch/manual
  recovery path.
- `auto-deploy` defines a provider-neutral deployment contract with immutable artifacts, bounded health verification, least-privilege credentials, and authorized rollback handling.
- Project-scoped `.codex/config.toml` enables subagents with a three-thread concurrency cap; `.codex/agents/reviewer.toml` provides optional supplemental read-only analysis.
- Automatic Review is the built-in `codex review` command and starts after PR
  creation or update without user confirmation; blocking findings repeat Fix ->
  Test -> applicable Redaction -> Commit -> Push -> `codex review` on the updated
  PR.
- Ticket Issues and implementation branches are one-to-one through `Branch`/`Base` metadata, and PR head/base must match those fields.
- `Repo_Current_State.md` is the compact recovery point; ticket detail and lifecycle metadata remain in GitHub Issues.
- `plan-to-ticket` now requires a parent plan Issue and one Issue per ticket before branch work, with stable markers, lifecycle metadata, and no Markdown/chat fallback.
- The root workflow creates or resumes a feature branch before implementation,
  requires a PR for every change, and merges only after Automatic Review passes.

## In Progress

- The unified PR-gated workflow update is prepared in the working tree; its
  commit, push, PR, Automatic Review, merge, and cleanup gates remain to be run.

## Known Issues / Failing Checks

- The baseline redaction scan reports three pre-existing email patterns in the
  publication-identity documentation; no new personal email was added by this
  change. Treat the findings as an explicit publication review item rather than
  claiming a clean redaction pass.

## Constraints

- Code review requires an installed and authenticated Codex CLI.
- Specialist behavior is bundled under `skills/` and installed from this repository's local source.
- `context-efficiency` remains an optional context-loading aid, not a workflow stage.
- Delegation is optional; dependent, overlapping, or shared-interface work remains sequential, and integration/final judgment stay with the main agent.
- `scripts/install-all.sh` requires a complete checkout and copies local bundles; it does not clone specialist repositories.
- Persisted plans and tickets require a resolvable GitHub repository target and an available, authorized GitHub Issues connector; failed required writes block completion without a Markdown fallback.

## Architecture Snapshot

- `SKILL.md` owns main-agent stage routing, Ticket/Slice hierarchy, the optional Delegation Gate, Slice contract, bounded verification, review policy, delivery gates, and recovery-state guidance.
- `plan-to-ticket` owns Ticket-first decomposition, dependency-ordered Slice generation, and mandatory GitHub Issue persistence; `test-workflow` owns selected verification execution and evidence reporting. Both are managed in `skills/`.
- `docs/skills/` contains explanatory documentation for every managed specialist skill; operational references and scripts remain beside the runtime bundles under `skills/`.
- `repo-current-state`, `data-document-redaction`, and `github-push-when-ready` remain conditional gates.
- `auto-deploy` is a conditional deployment gate and does not own target-project infrastructure or production approvals.
- The parent workflow and `repo-current-state` use GitHub Issues as the durable ticket authority; this file only points to active and next Issues. See `docs/workflow/usage.md` and `docs/skills/plan-to-ticket/architecture.md`.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.

## Next

- Start the next authorized ticket from the updated default branch.
