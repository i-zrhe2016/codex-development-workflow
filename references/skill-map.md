# Skill Map

This repository is the source of truth for every skill installed by
`scripts/install-all.sh`. The installer copies these local paths; it does not
clone specialist repositories at installation time.

Project-scoped runtime configuration lives separately under `.codex/` and
`.claude/`; those files are not Skill metadata and are not copied by the
installer. Skill interface metadata remains in each managed bundle's
`agents/openai.yaml`. Codex requires that file: the Codex target fails when a
bundle omits it, and installs it. The Claude target installs the same bundle
without it, because Claude Code never reads it.

| Skill | Managed source in this repository | Documentation | Codex destination | Claude Code destination |
|---|---|---|---|---|
| `codex-development-workflow` | Root package: `SKILL.md`, `agents/`, selected workflow references | `docs/workflow/`, `docs/architecture/` | `codex-development-workflow` | `codex-development-workflow` |
| `plan-workflow` | `skills/plan-workflow/` | — | `plan-workflow` | `plan-workflow` |
| `develop-workflow` | `skills/develop-workflow/` | — | `develop-workflow` | `develop-workflow` |
| `verify-workflow` | `skills/verify-workflow/` | — | `verify-workflow` | `verify-workflow` |
| `publish-workflow` | `skills/publish-workflow/` | — | `publish-workflow` | `publish-workflow` |
| `integrate-workflow` | `skills/integrate-workflow/` | — | `integrate-workflow` | `integrate-workflow` |
| `plan-to-ticket` | `skills/plan-to-ticket/` | `docs/skills/plan-to-ticket/` | `plan-to-ticket` | `plan-to-ticket` |
| `test-workflow` | `skills/test-workflow/` | `docs/skills/test-workflow/` | `test-workflow` | `test-workflow` |
| `repo-current-state` | `skills/repo-current-state/` | `docs/skills/repo-current-state/` | `repo-current-state` | `repo-current-state` |
| `repo-documentation` | `skills/repo-documentation/` | `docs/skills/repo-documentation/` | `repo-documentation` | `repo-documentation` |
| `data-document-redaction` | `skills/data-document-redaction/` with its staged-scan script | `docs/skills/data-document-redaction/` | `data-document-redaction` | `data-document-redaction` |
| `github-push-when-ready` | `skills/github-push-when-ready/` with its scripts | `docs/skills/github-push-when-ready/` | `github-push-when-ready` | `github-push-when-ready` |

Both destinations are the bare skill name; only the root differs, selected by
`--target` (`${CODEX_HOME:-$HOME/.codex}/skills` for Codex, `$HOME/.claude/skills`
for Claude Code) or overridden with `--dest`. This file ships inside the
installed root bundle, so the link below resolves only in the repository
checkout.

Each managed source is an independently installable skill folder containing
`SKILL.md`. The root package remains at the repository root for
backward compatibility; its installer entry copies only the files needed by
the orchestrator rather than the whole repository.

The managed bundles split into a workflow layer that decides *when* a stage
runs and a capability layer that defines *how* it is performed. The five
`*-workflow` bundles are the workflow layer; they own the stage boundary and
delegate the procedure. The remaining bundles are the capability layer.

`plan-workflow` owns the requirement-to-work-definition stage, including the
decision whether a plan needs to be persisted. `develop-workflow` owns
implementation up to Development Complete. `verify-workflow` is a thin stage
that selects the verification scope and level and returns the conclusion.
`publish-workflow` composes the documentation impact check, the redaction scan,
and publication, and stops at PR ready without merging. `integrate-workflow`
owns merge, cleanup, Plan and Ticket closure, state refresh, and documentation
reconciliation.

`plan-to-ticket` owns Plan-first decomposition, Ticket/Slice generation, and the
persistence contract that applies whenever a plan is persisted; each Slice
provides boundaries, acceptance criteria, relevant context, test strategy, test
level, test cases, and a validation command. A persisted Plan owns one branch,
PR, and merge for all of its Tickets.
`test-workflow` owns the verification procedure for the selected `minimal`,
`focused`, `regression`, or `full` level and reports bounded evidence. It
conditionally performs browser/E2E verification when browser-visible behavior
changes.

`data-document-redaction` owns the staged-file scan before commit and repeats it
after subsequent fixes that change staged content. `github-push-when-ready`
owns the feature-branch publication path through Commit, Push, and Create/Update
PR readiness.

`repo-documentation` owns documentation governance: the documentation impact
check, canonical ownership per fact, the documentation router, the Markdown
file standard, duplicate and orphan detection, and document lifecycle. It stays
separate from `repo-current-state`, which owns only the current-state snapshot.
