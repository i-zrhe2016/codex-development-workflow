# Repository Current State

Last verified: 2026-09-21 @ a38e2d3

## Current Focus

- None.

## Implemented

- Every requirement is recorded as exactly one Plan Issue with at least one
  child Ticket before its Plan branch starts; all change types follow the Plan
  branch -> test -> redaction -> commit -> push -> PR -> merge
  and cleanup gates defined by `AGENTS.md`.
- The bundle installs for two hosts. `scripts/install-all.sh --target codex`
  (default) writes to `${CODEX_HOME:-$HOME/.codex}/skills`; `--target claude`
  writes to `$HOME/.claude/skills`. `--dest` overrides either. The Claude target
  omits the Codex-only `agents/openai.yaml` metadata from each bundle.
- Agent selection is delegated to the host. `AGENTS.md` owns the delegation
  policy and maps no task class to an agent; Codex reads `.codex/agents/` and
  Claude Code reads `.claude/agents/`, selecting by each definition's
  `description`.
- `github-push-when-ready` owns branch, commit, push, and PR readiness.
- `repo-documentation` governs documentation as one canonical document per
  fact. Its impact check runs inside the existing Test -> Redaction path, and it
  routes each fact to its owning document type, keeps exactly one documentation
  router, and detects duplicates, orphans, and stale claims. It also owns the
  diagram policy: when a document carries a diagram, where the `.puml` source
  and rendered image live, how an unrendered diagram is marked, and when an
  existing diagram is stale.
- Diagrams are drawn with the host-installed `plantuml-skill` and rendered
  through Kroki. `docs/skills/repo-documentation/diagrams/` and
  `docs/deployment/diagrams/` hold the two diagrams added with the policy.
- Documentation carries two complementary diagram layers: Draw.io for polished,
  editable, human-facing overview views, and PlantUML for detailed
  diagrams-as-code. Six editable `.drawio` views and their rendered `.svg` files
  live under `docs/diagrams/drawio/`, where `doc-file-standard.md` sanctions
  shared repository-level overviews.
- `docs/` was normalized to the `repo-documentation` standard: every content
  document carries a conforming `Type` / `Status` / `Scope` header, no document
  claims a retired skill runs, no two documents share a `#` title, every
  document is reachable from the root `README.md` router, and the legacy
  directory placement and the Chinese `docs/skills/test-workflow/*` set were
  reported rather than moved or translated.
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
- Rendered diagrams still bake in the old "Codex" naming. The affected files are
  `docs/diagrams/architecture.svg`, `docs/diagrams/components.svg`,
  `docs/deployment/diagrams/installer-decision-flow.svg`,
  `docs/diagrams/drawio/workflow-overview.svg`, and
  `docs/diagrams/drawio/installer-overview.svg`; the four per-skill SVGs under
  `docs/skills/*/diagrams/` are clean. Regenerating them needs PlantUML/Kroki
  tooling that is not part of this repository.
- `AGENTS.md` routes "Architecture or flow visualization" to a `plantuml-skill`
  that this repository does not bundle; the skill is installed on the host
  instead. `repo-documentation` now states that rendering is delegated to it by
  name and defines the unrendered path, so the routing is actionable even though
  the bundle is absent.
- The older shared `docs/diagrams/` PlantUML set (`architecture`, `components`,
  `ticket-lifecycle`, `ticket-slice-loop`) predates the `repo-documentation`
  placement rule that puts new diagrams beside their owning document. Those
  diagrams stay in place until their owning document is migrated;
  `docs/diagrams/drawio/` is a sanctioned location for shared
  repository-level overviews, so it is not part of this finding.

## Constraints

- `agents/openai.yaml` remains a required file for the Codex target only. A
  bundle that omits it fails the Codex install but installs for Claude Code.
- `docs/skills/test-workflow/*` is written in Chinese; the remaining managed
  skill content is English.
- Shell commands use the available native tools directly; exact evidence and
  publication gates preserve raw output and exit status.
- Persisted Plans and child Tickets require an available, authorized GitHub
  Issues target; GitHub Issues are the durable authority for future work.

## Architecture Snapshot

- The root workflow owns lifecycle routing, Plan/Ticket/Slice gates, delegation,
  verification, and merge/cleanup guidance; each requirement has exactly one
  Plan, and each Plan owns one branch, PR, and merge for its child Tickets.
- `github-push-when-ready` owns publication through PR readiness; the parent
  workflow merges the Plan PR after the existing validation and publication
  gates pass.
- `repo-documentation` owns documentation governance and `repo-current-state`
  owns only the recovery snapshot. This repository routes its documentation from
  the root `README.md` instead of `docs/README.md`.
- Runtime skills remain under `skills/`; explanatory documentation is under
  `docs/skills/`; the installer packages the local skill bundles. See
  `docs/architecture/overview.md` for the topology and
  `docs/deployment/installation.md` for the install procedure.

## Next

- Start the next authorized Plan from the updated default branch.
