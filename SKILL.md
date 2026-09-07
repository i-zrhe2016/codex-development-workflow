---
name: codex-development-workflow
description: "Entry point for the repository-wide Codex development lifecycle. Use for non-trivial feature development, bug fixes, refactors, and repository changes. AGENTS.md defines the orchestration policy and when specialist skills should be invoked."
---

# Codex Development Workflow

Use this skill as the entry point for non-trivial repository development.

## Source of Truth

Read and follow `AGENTS.md` for:

- engineering priorities and architecture principles;
- the end-to-end development lifecycle;
- validation and Git discipline;
- context and subagent policy; and
- exact conditions for invoking specialist skills.

Do not duplicate those rules here.

## Specialist Skills

This skill coordinates specialist skills but does not replace them. When `AGENTS.md` says a specialist skill applies, invoke that skill and follow its `SKILL.md` for the detailed procedure.

Read `references/skill-map.md` only when repository sources or install locations are needed.

If a required specialist skill is unavailable locally, report it rather than silently replacing its workflow.

## Installation

Install the complete workflow skill set with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash
```

Update existing installations with:

```bash
curl -fsSL https://raw.githubusercontent.com/i-zrhe2016/codex-development-workflow/main/scripts/install-all.sh | bash -s -- --update
```

Codex uses `${CODEX_HOME:-$HOME/.codex}/skills` by default. Restart Codex after installation.
