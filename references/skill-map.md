# Skill Map

This repository is the source of truth for every skill installed by
`scripts/install-all.sh`. The installer copies these local paths; it does not
clone specialist repositories at installation time.

| Skill | Managed source in this repository | Codex destination |
|---|---|---|
| `codex-development-workflow` | Root package: `SKILL.md`, `agents/`, selected workflow references | `codex-development-workflow` |
| `context-efficiency` | `skills/context-efficiency/` | `context-efficiency` |
| `plan-to-ticket` | `skills/plan-to-ticket/` | `plan-to-ticket` |
| `test-workflow` | `skills/test-workflow/` | `test-workflow` |
| `repo-current-state` | `skills/repo-current-state/` | `repo-current-state` |
| `data-document-redaction` | `skills/data-document-redaction/` with its references and scripts | `data-document-redaction` |
| `github-push-when-ready` | `skills/github-push-when-ready/` with its scripts | `github-push-when-ready` |

Each managed source is an independently installable Codex skill folder
containing `SKILL.md`. The root package remains at the repository root for
backward compatibility; its installer entry copies only the files needed by
the orchestrator rather than the whole repository.

`plan-to-ticket` owns Slice generation; each Slice should provide boundaries,
acceptance criteria, relevant context, test strategy, test level, test cases,
and a validation command. `test-workflow` owns execution of the selected
`minimal`, `focused`, `regression`, or `full` verification level and reports
bounded evidence. It conditionally performs browser/E2E verification when
browser-visible behavior changes.

Code review is provided by the Codex CLI's built-in `codex review` command; it is not installed by this script.
