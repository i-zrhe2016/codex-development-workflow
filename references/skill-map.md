# Skill Map

| Skill | Repository | Repository path | Codex destination |
|---|---|---|---|
| `codex-development-workflow` | `i-zrhe2016/codex-development-workflow` | `.` | `codex-development-workflow` |
| `context-efficiency` | `i-zrhe2016/context-skill` | `context-efficiency` | `context-efficiency` |
| `plan-to-ticket` | `i-zrhe2016/plan-to-ticket` | `.` | `plan-to-ticket` |
| `test-workflow` | `i-zrhe2016/test-skill` | `test-workflow` | `test-workflow` |
| `repo-current-state` | `i-zrhe2016/Repo_Current_State.md` | `.` | `repo-current-state` |
| `data-document-redaction` | `i-zrhe2016/data-document-redaction` | `data-document-redaction` | `data-document-redaction` |
| `github-push-when-ready` | `i-zrhe2016/github-push-skill` | `github-push-when-ready` | `github-push-when-ready` |

The installer treats each row as an independently installable Codex skill folder containing `SKILL.md`.

`test-workflow` owns the general testing ladder and conditionally performs browser/E2E verification when browser-visible behavior changes. The older `frontend-click-test` remains in its source repository for compatibility but is no longer installed by this workflow.

Code review is provided by the Codex CLI's built-in `codex review` command; it is not installed by this script.
