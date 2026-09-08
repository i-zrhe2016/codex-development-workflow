# Repository Current State

Last verified: 2026-09-08 @ working tree

## Current Focus

- Single-agent staged Codex workflow with Plan/Slice execution, bounded verification, and repository-managed specialist bundles.

## Implemented

- The workflow classifies work, understands the current repository, plans small Slices, executes one Slice at a time, integrates, self-reviews, and delivers.
- Normal and complex Slices define scope, exclusions, dependencies, acceptance criteria, relevant context, test strategy, verification level, test cases, and validation commands.
- Verification levels are `minimal`, `focused`, `regression`, and `full`; focused is the default and passing evidence stops expansion unless escalation is justified.
- Test-first behavior is conditional on meaningful behavioral risk; non-behavioral changes use direct minimal validation.
- The installer packages seven local skills from the root skill and `skills/`; specialist repositories are not cloned at install time.
- `Repo_Current_State.md` is the compact recovery point; the architecture diagram and workflow documentation reflect the same lifecycle.

## Constraints

- Code review requires an installed and authenticated Codex CLI.
- Specialist behavior is bundled under `skills/` and installed from this repository's local source.
- `context-efficiency` remains an optional context-loading aid, not a workflow stage.
- The workflow does not orchestrate multiple agents, sub-agents, parallel implementations, or agent handoffs.
- `scripts/install-all.sh` requires a complete checkout and copies local bundles; it does not clone specialist repositories.

## Architecture Snapshot

- `SKILL.md` owns single-agent stage routing, Slice contract, bounded verification, review policy, delivery gates, and recovery-state guidance.
- `plan-to-ticket` owns Slice generation; `test-workflow` owns selected verification execution and evidence reporting. Both are managed in `skills/`.
- `repo-current-state`, `data-document-redaction`, and `github-push-when-ready` remain conditional gates.
- See `docs/architecture/overview.md` and `docs/diagrams/architecture.puml` for the workflow topology.
