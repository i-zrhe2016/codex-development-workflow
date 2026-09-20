# Repository Current State

Last verified: 2026-09-20 @ 829c87b

## Current Focus

- None.

## Implemented

- Every requirement is recorded as exactly one Plan Issue with at least one
  child Ticket before its Plan branch starts; all change types follow the Plan
  branch -> test -> redaction -> commit -> push -> PR -> `pr-review` -> merge
  and cleanup gates defined by `AGENTS.md`.
- The bundle installs for two hosts. `scripts/install-all.sh --target codex`
  (default) writes to `${CODEX_HOME:-$HOME/.codex}/skills`; `--target claude`
  writes to `$HOME/.claude/skills`. `--dest` overrides either. The Claude target
  omits the Codex-only `agents/openai.yaml` metadata from each bundle.
- Agent selection is delegated to the host. `AGENTS.md` owns the delegation
  policy and maps no task class to an agent; Codex reads `.codex/agents/` and
  Claude Code reads `.claude/agents/`, selecting by each definition's
  `description`.
- `.claude/agents/reviewer.md` provides the optional high-risk reviewer for
  Claude Code with no write tool and no shell; it requires the task prompt to
  carry the patch text and acceptance criteria. `.codex/agents/reviewer.toml`
  remains the Codex equivalent.
- `pr-review` is the single merge decision gate. The first review covers the
  complete PR; bounded fixes may use incremental runner coverage, while
  high-impact or uncertain changes require full coverage.
- `github-push-when-ready` owns branch, commit, push, and PR readiness. The
  recoverable review runner is packaged with `pr-review` as an implementation
  detail.
- `pr-review` detects changed Markdown files and passes a trusted bundled
  document rule to the same OpenCode Review execution; documentation remains
  under the single `PASS`/`BLOCKED` merge gate.
- `repo-documentation` governs documentation as one canonical document per
  fact. Its impact check runs inside the existing Test -> Redaction path, and it
  routes each fact to its owning document type, keeps exactly one documentation
  router, and detects duplicates, orphans, and stale claims. It also owns the
  diagram policy: when a document carries a diagram, where the `.puml` source
  and rendered image live, and when an existing diagram is stale.
- `Repo_Current_State.md` is the compact current-state memory; GitHub Issues
  hold Plans and child Tickets, while `docs/skills/` documents the managed
  skills.
- `plan-to-ticket` uses exactly one canonical `[PLAN]` Issue per requirement,
  `[T####]` child Issue titles, repository-scoped non-reused Ticket IDs, and
  one shared Plan branch/PR/merge for all Tickets and Slices in that
  requirement.
- The installer records per-bundle ownership markers, protects unmarked paths,
  and offers recoverable `--adopt-legacy` migration for pre-marker installs.
- `scripts/tests/test_install_all.py` covers target selection, `--dest`
  precedence, invalid and missing `--target` values, skip/update behavior, and
  per-target bundle contents.

## In Progress

- None.

## Known Issues / Failing Checks

- Pre-existing identity and SSH test fixtures remain under
  `skills/github-push-when-ready/`; the staged redaction scan for PR #69
  passed, but this is not a repository-wide redaction classification.
- Rendered diagrams under `docs/diagrams/` and `docs/skills/*/diagrams/` still
  bake in the old "Codex" naming. Regenerating them needs PlantUML/Kroki
  tooling that is not part of this repository.
- `AGENTS.md` routes "Architecture or flow visualization" to a `plantuml-skill`
  that this repository does not bundle.

## Constraints

- `pr-review` requires an installed and configured Alibaba Open Code Review CLI
  (`ocr`) and a reachable provider endpoint with a supported model.
- `agents/openai.yaml` remains a required file for the Codex target only. A
  bundle that omits it fails the Codex install but installs for Claude Code.
- `skills/context-efficiency/SKILL.md` and `docs/skills/test-workflow/*` are
  written in Chinese; the remaining skill content is English.
- Shell commands use the available native tools through `context-efficiency`;
  exact evidence and publication gates preserve raw output and exit status.
- Persisted Plans and child Tickets require an available, authorized GitHub
  Issues target; GitHub Issues are the durable authority for future work.

## Architecture Snapshot

- The root workflow owns lifecycle routing, Plan/Ticket/Slice gates, delegation,
  verification, and merge/cleanup guidance; each requirement has exactly one
  Plan, and each Plan owns one branch, PR, and merge for its child Tickets.
- `github-push-when-ready` owns publication through PR readiness; `pr-review`
  owns the single PASS/BLOCKED merge decision and its recoverable runner.
- `repo-documentation` owns documentation governance and `repo-current-state`
  owns only the recovery snapshot. This repository routes its documentation from
  the root `README.md` instead of `docs/README.md`.
- Runtime skills remain under `skills/`; explanatory documentation is under
  `docs/skills/`; the installer packages the local skill bundles. See
  `docs/architecture/overview.md` for the topology and
  `docs/deployment/installation.md` for the install procedure.

## Next

- Start the next authorized Plan from the updated default branch.
