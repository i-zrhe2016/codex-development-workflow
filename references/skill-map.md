# Skill Map

This repository is the source of truth for every skill installed by
`scripts/install-all.sh`. The installer copies these local paths; it does not
clone specialist repositories at installation time.

Project-scoped runtime configuration lives separately under `.codex/` and
`.claude/`: custom agent files such as `.codex/agents/reviewer.toml` and
`.claude/agents/reviewer.md` are not Skill metadata and are not copied by the
installer. Skill interface metadata remains in each managed bundle's
`agents/openai.yaml`. That file is required by the installer for both targets
but is only consumed by Codex.

| Skill | Managed source in this repository | Documentation | Codex destination | Claude Code destination |
|---|---|---|---|---|
| `codex-development-workflow` | Root package: `SKILL.md`, `agents/`, selected workflow references | `docs/workflow/`, `docs/architecture/` | `codex-development-workflow` | `codex-development-workflow` |
| `context-efficiency` | `skills/context-efficiency/` | `docs/skills/context-efficiency/` | `context-efficiency` | `context-efficiency` |
| `plan-to-ticket` | `skills/plan-to-ticket/` | `docs/skills/plan-to-ticket/` | `plan-to-ticket` | `plan-to-ticket` |
| `test-workflow` | `skills/test-workflow/` | `docs/skills/test-workflow/` | `test-workflow` | `test-workflow` |
| `repo-current-state` | `skills/repo-current-state/` | `docs/skills/repo-current-state/` | `repo-current-state` | `repo-current-state` |
| `repo-documentation` | `skills/repo-documentation/` | `docs/skills/repo-documentation/` | `repo-documentation` | `repo-documentation` |
| `data-document-redaction` | `skills/data-document-redaction/` with its staged-scan script | `docs/skills/data-document-redaction/` | `data-document-redaction` | `data-document-redaction` |
| `github-push-when-ready` | `skills/github-push-when-ready/` with its scripts | `docs/skills/github-push-when-ready/` | `github-push-when-ready` | `github-push-when-ready` |
| `pr-review` | `skills/pr-review/` with its runner and execution reference | `docs/skills/pr-review/` | `pr-review` | `pr-review` |

Both destinations are the bare skill name; only the root differs, selected by
`--target` (`${CODEX_HOME:-$HOME/.codex}/skills` for Codex, `$HOME/.claude/skills`
for Claude Code) or overridden with `--dest`. See the
[installation and update guide](../docs/deployment/installation.md) for the
procedure.

Each managed source is an independently installable skill folder containing
`SKILL.md`. The root package remains at the repository root for
backward compatibility; its installer entry copies only the files needed by
the orchestrator rather than the whole repository.

`plan-to-ticket` owns Plan-first decomposition for every requirement,
Ticket/Slice generation, and mandatory persistence of exactly one Plan Issue plus
its child Ticket Issues; each
Slice should provide boundaries, acceptance criteria, relevant context, test
strategy, test level, test cases, and a validation command. The Plan owns the
single branch, PR, and merge for all of its Tickets.
`test-workflow` owns the Test stage for the selected `minimal`, `focused`,
`regression`, or `full` verification level and reports bounded evidence. It
conditionally performs browser/E2E verification when browser-visible behavior
changes.

`data-document-redaction` owns the staged-file scan before commit and repeats it
after blocking review fixes that change staged content. `github-push-when-ready`
owns the feature-branch publication path through Commit, Push, and Create/Update
PR readiness. `pr-review` owns the single merge decision gate and invokes
Alibaba Open Code Review's `ocr review` command through its recoverable runner.
The runner is packaged with `pr-review` rather than installed separately.

`repo-documentation` owns documentation governance: the documentation impact
check, canonical ownership per fact, the documentation router, the Markdown
file standard, duplicate and orphan detection, and document lifecycle. It stays
separate from `repo-current-state`, which owns only the current-state snapshot.
