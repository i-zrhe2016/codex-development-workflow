# Skill Map

`scripts/install-all.sh` copies this repository's bundles, without cloning
specialist repositories. Each is an independently installable folder with
`SKILL.md`; the root bundle keeps its historical repository-root location and
installs selected runtime files, not the whole checkout.

| Skill | Repository source | Documentation |
|---|---|---|
| `codex-development-workflow` | `SKILL.md`, `agents/`, selected workflow references | `docs/workflow/`, `docs/architecture/` |
| `plan-workflow` | `skills/plan-workflow/` | — |
| `develop-workflow` | `skills/develop-workflow/` | — |
| `verify-workflow` | `skills/verify-workflow/` | — |
| `publish-workflow` | `skills/publish-workflow/` | — |
| `integrate-workflow` | `skills/integrate-workflow/` | — |
| `plan-to-ticket` | `skills/plan-to-ticket/` | `docs/skills/plan-to-ticket/` |
| `test-workflow` | `skills/test-workflow/` | `docs/skills/test-workflow/` |
| `skill-eval` | `skills/skill-eval/` | — |
| `plantuml` | `skills/plantuml/` | `docs/skills/plantuml/` |
| `repo-current-state` | `skills/repo-current-state/` | `docs/skills/repo-current-state/` |
| `repo-documentation` | `skills/repo-documentation/` | `docs/skills/repo-documentation/` |
| `data-document-redaction` | `skills/data-document-redaction/` (staged scanner) | `docs/skills/data-document-redaction/` |
| `github-push-when-ready` | `skills/github-push-when-ready/` (publication scripts) | `docs/skills/github-push-when-ready/` |

Destination folders use the skill names under:

- `--target codex` (default): `${CODEX_HOME:-$HOME/.codex}/skills`.
- `--target claude`: `$HOME/.claude/skills`.
- `--dest`: overrides either root.

Codex requires/installs each `agents/openai.yaml`; missing metadata blocks that
target. Claude omits this Codex-only interface file. Project `.codex/`/`.claude/`
configuration is separate and never installed. This map ships in the root
bundle; repository documentation paths above resolve only in a full checkout.

The root bundle's `SKILL.md` owns **Codex worker model routing**. Direct
develop/verify/test coordinators find that Skill in the host's discovered
catalog at the same installation root as their active entrypoint; duplicate
global/project names do not switch bundle association. No source-checkout path
or copied project configuration is needed. Claude model selection remains host-specific.

The five stage skills own **when** and stopping boundaries: planning/persistence
decision, Development Complete, verification scope/conclusion, docs/redaction/
commit/push/PR ready (never merge), and merge/cleanup/Issue closure/state/docs reconciliation.
Read their `SKILL.md` for contracts. Capability skills own **how**:

- `plan-to-ticket`: Plan-first decomposition, Issue persistence and Slice
  contracts (boundaries, acceptance, context, strategy, level, cases and validation
  command); one branch/PR/merge per persisted Plan.
- `test-workflow`: minimal/focused/regression/full validation and evidence;
  browser/E2E when browser-visible interaction changes.
- `skill-eval`: blind A/B skill-effectiveness evaluation with Static, Trigger,
  Behavior and outcome-decisive Outcome evidence.
- `plantuml`: type/source/render/readability; `repo-documentation` owns canonical
  placement, naming, impact and lifecycle, plus router and duplicate/orphan checks.
- `repo-current-state`: current-state snapshot only.
- `data-document-redaction`: staged next-commit scan, repeated after staged fixes.
- `github-push-when-ready`: guarded feature-branch Commit/Push/Create-or-Update-PR readiness.
