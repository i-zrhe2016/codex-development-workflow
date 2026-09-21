# Repository Current State

Last verified: 2026-09-21 @ 8a2b79e

## Current Focus

- None.

## Implemented

- Work is routed to the stage that owns it: `plan-workflow` (requirement to
  work definition), `develop-workflow` (implementation to Development Complete),
  `verify-workflow` (verification scope and conclusion), `publish-workflow`
  (documentation impact, redaction, commit, push, PR ready), and
  `integrate-workflow` (merge once, cleanup, Issue closure, state and docs).
  `codex-development-workflow` routes to those stages and carries the invariants
  shared by all of them.
- A persisted Plan Issue owns one branch, one PR, and one merge for all of its
  child Tickets. A plan is persisted when the work is complex, must survive a
  session boundary, or the user asks for it; small single-session work keeps its
  plan inline.
- The five stage-workflow bundles and the six capability bundles install for
  both hosts: `scripts/install-all.sh` reports 12 bundles for the Codex target
  and 12 for the Claude target, which omits the Codex-only
  `agents/openai.yaml` metadata.
- The bundle installs for two hosts. `scripts/install-all.sh --target codex`
  (default) writes to `${CODEX_HOME:-$HOME/.codex}/skills`; `--target claude`
  writes to `$HOME/.claude/skills`. `--dest` overrides either. The Claude target
  omits the Codex-only `agents/openai.yaml` metadata from each bundle.
- Agent selection is delegated to the host. `AGENTS.md` owns the delegation
  policy and maps no task class to an agent; Codex reads `.codex/agents/` and
  Claude Code reads `.claude/agents/`, selecting by each definition's
  `description`.
- `github-push-when-ready` owns branch, commit, push, and PR readiness. It
  publishes any non-default verified branch; Plan metadata is validated when the
  branch carries it, and a persisted Plan is not a publication precondition.
- `repo-documentation` governs documentation as one canonical document per
  fact. Its impact check runs inside `publish-workflow`, between verification and
  the staged redaction scan, and it
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
- `plan-to-ticket` uses one canonical `[PLAN]` Issue per persisted plan,
  `[T####]` child Issue titles, repository-scoped non-reused Ticket IDs, and one
  shared branch/PR/merge for all Tickets and Slices of that plan.
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
- Diagram rendering tooling is part of this repository:
  `scripts/render-diagrams.sh` renders every `docs/**/*.puml` source through
  Kroki and `bash scripts/render-diagrams.sh --check` currently reports no render
  drift for any of the nine sources. The `.drawio` overviews have no render
  branch in that script, so their `.svg` previews are hand-synced with the
  `.drawio` XML.
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

- `codex-development-workflow` is the router and the optional full
  orchestration; each stage workflow owns one boundary and states its own
  non-responsibility, so a stage never performs another stage's work.
- A persisted Plan owns one branch, PR, and merge for its child Tickets;
  `github-push-when-ready` owns publication through PR readiness, and
  `integrate-workflow` merges once the verification and publication gates pass.
- `repo-documentation` owns documentation governance and `repo-current-state`
  owns only the recovery snapshot. This repository routes its documentation from
  the root `README.md` instead of `docs/README.md`.
- Runtime skills remain under `skills/`; explanatory documentation is under
  `docs/skills/`; the installer packages the local skill bundles. See
  `docs/architecture/overview.md` for the topology and
  `docs/deployment/installation.md` for the install procedure.

## Next

- Start the next authorized Plan from the updated default branch, or run a
  single stage workflow when the request only needs that stage.
