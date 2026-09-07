# Codex Development Workflow

A gated Codex development workflow built from the author's GitHub skills:

`Plan -> Ticket -> Implement -> Test -> Review -> Repo State -> Commit/Push`

## One-command install

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

This installs all workflow skills into `${CODEX_HOME:-$HOME/.codex}/skills`.

Update existing installations:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Restart Codex after installation.

## Installed skills

- `codex-development-workflow`
- `context-efficiency`
- `plan-to-ticket`
- `frontend-click-test`
- `code-review`
- `repo-current-state`
- `github-push-when-ready`

See `references/skill-map.md` for source repositories and paths.
