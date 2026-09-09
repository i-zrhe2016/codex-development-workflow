# Skill Map

This repository is the source of truth for every skill installed by
`scripts/install-all.sh`. The installer copies these local paths; it does not
clone specialist repositories at installation time.

Project-scoped runtime configuration lives separately under `.codex/`: custom
agent files such as `.codex/agents/reviewer.toml` are not Skill metadata and are
not copied by the installer. Skill interface metadata remains in each managed
bundle's `agents/openai.yaml`.

| Skill | Managed source in this repository | Documentation | Codex destination |
|---|---|---|---|
| `codex-development-workflow` | Root package: `SKILL.md`, `agents/`, selected workflow references | `docs/workflow/`, `docs/architecture/` | `codex-development-workflow` |
| `context-efficiency` | `skills/context-efficiency/` | `docs/skills/context-efficiency/` | `context-efficiency` |
| `plan-to-ticket` | `skills/plan-to-ticket/` | `docs/skills/plan-to-ticket/` | `plan-to-ticket` |
| `test-workflow` | `skills/test-workflow/` | `docs/skills/test-workflow/` | `test-workflow` |
| `repo-current-state` | `skills/repo-current-state/` | `docs/skills/repo-current-state/` | `repo-current-state` |
| `data-document-redaction` | `skills/data-document-redaction/` with its references and scripts | `docs/skills/data-document-redaction/` | `data-document-redaction` |
| `github-push-when-ready` | `skills/github-push-when-ready/` with its scripts | `docs/skills/github-push-when-ready/` | `github-push-when-ready` |
| `auto-deploy` | `skills/auto-deploy/` | `docs/skills/auto-deploy/` | `auto-deploy` |

Each managed source is an independently installable Codex skill folder
containing `SKILL.md`. The root package remains at the repository root for
backward compatibility; its installer entry copies only the files needed by
the orchestrator rather than the whole repository.

`plan-to-ticket` owns Ticket-first decomposition, Slice generation, and
mandatory persistence of the parent plan and Ticket Issues; each Slice should
provide boundaries, acceptance criteria, relevant context, test strategy, test
level, test cases, and a validation command. `test-workflow` owns the Test stage
for the selected
`minimal`, `focused`, `regression`, or `full` verification level and reports
bounded evidence. It conditionally performs browser/E2E verification when
browser-visible behavior changes.

`data-document-redaction` owns the applicable redaction scan before commit and
after blocking review fixes. `github-push-when-ready` owns the feature-branch
publication path, Commit, Push, Create/Update PR, Merge, and source-branch
cleanup gates. The built-in `codex review` command is the mandatory Automatic
Review gate; it is not installed by this script and runs after PR creation or
update. The project-scoped `.codex/agents/reviewer.toml` is optional
supplemental analysis loaded by an interactive session and never replaces
`codex review`.
