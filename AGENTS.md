# AGENTS.md

This file is the repository-wide source of truth for development behavior and skill orchestration.

Detailed implementation procedures belong in specialist skills. Do not duplicate those procedures here; this file defines when they are used and how they fit together.

## Priority

Use this priority order for engineering decisions:

`Correctness -> Simplicity -> Architecture Clarity -> Maintainability -> Extensibility`

If a simpler solution satisfies the requirement safely, do not introduce a more complex one.

## Core Principles

- Follow Occam's razor in planning, architecture, implementation, and troubleshooting: prefer the smallest necessary and maintainable solution.
- Architecture first for non-trivial work: understand the current architecture, design the minimum change, then implement.
- Introduce only basic and necessary components early in a project. Preserve future extensibility through clear interfaces instead of speculative infrastructure.
- Prefer mature frameworks, existing project capabilities, and reusable components over rebuilding equivalent functionality.
- Do not implement features without a concrete requirement.

## Architecture

- Focus on system structure, module boundaries, data flow, call relationships, and deployment relationships.
- Apply service boundaries around clear business capabilities and single responsibility.
- Do not split services merely to follow a microservice style. Keep simple, tightly coupled behavior in one module unless independent deployment, scaling, ownership, or evolution justifies separation.
- Services interact through explicit interfaces and must not depend on another service's internal implementation.
- Use diagrams for important architecture, data flow, call chains, and deployment topology.
- Prefer `plantuml-skill` for architecture diagrams, flowcharts, sequence diagrams, component diagrams, deployment diagrams, and other non-trivial technical visualizations when the skill is available.
- Create a diagram when it materially improves understanding, especially for 3+ interacting components, cross-service flows, important sequences, or deployment topology. Do not draw diagrams for trivial changes.

## Documentation

- Put detailed documentation under `docs/`.
- Keep the root `README.md` as the project introduction and documentation index.
- Split documentation by responsibility as the project grows, for example: `architecture`, `services`, `api`, `database`, `deployment`, `testing`, `troubleshooting`, and `diagrams`.
- One document should focus on one module or topic.
- Avoid large catch-all documents.
- Record important architecture, interfaces, data structures, deployment methods, and technical decisions.
- Update affected documentation when meaningful code changes make it stale.
- Update the README documentation index when the documentation structure changes.

## Context Efficiency

- Protect tokens and working context.
- For commands with unknown or potentially large output, default to `COMMAND 2>&1 | head -c 4000`.
- Search before reading code.
- Prefer `rg` or `grep` for discovery.
- Read only relevant files and relevant line ranges.
- Do not dump large files, logs, or complete diffs unless necessary.
- Do not reread unchanged content that is already understood.
- For long tasks, keep only a compact state record: `current goal`, `completed work`, `important decisions`, `unresolved issues`, and `next step`.
- Do not preserve verbose history or full logs as task state.

## Development Workflow

Use this as the default lifecycle for non-trivial repository changes:

`Requirement -> Search existing code -> Understand architecture -> Minimal design -> Plan/Tickets -> Documentation/Diagram when useful -> Implement one module/ticket -> Targeted validation -> Review -> Update repository state/docs -> Commit readiness -> Commit/Push -> Completion notification`

Detailed flow:

1. Clarify the requested outcome and acceptance criteria from the available context.
2. Search existing code and documentation before opening large files.
3. Understand the affected architecture, module boundaries, dependencies, and current behavior.
4. Design the minimum change that satisfies the requirement.
5. For non-trivial work, create dependency-ordered tickets before implementation.
6. Update or create architecture/documentation before implementation only when doing so materially clarifies the design; otherwise update docs after verified implementation.
7. Implement exactly one clear work unit at a time.
8. Run the smallest validation that can prove the changed behavior.
9. Expand validation only when the change affects broader interfaces, shared modules, architecture, or integration behavior.
10. Run code review after relevant tests pass.
11. If review causes code changes, rerun affected validation and repeat review when meaningful.
12. Update repository-state documentation and other affected docs only after behavior is verified.
13. Check repository status and diff scope before commit or push.
14. Commit one coherent purpose at a time; do not mix unrelated work.
15. Send the completion notification once, then provide the final response.

### Troubleshooting

- Collect evidence first and reduce the problem to the smallest failing scope before modifying code.
- Check simple causes first: configuration, parameters, environment, permissions, network, data, and dependencies.
- Fix the root cause instead of adding complexity that hides the failure.
- Do not mix unrelated cleanup or refactoring into a bug fix.

## Skill Invocation Policy

Skills are specialist procedures. Invoke them only when their trigger is met; do not run every skill mechanically for every task.

| Skill | Invoke when | Skip when |
|---|---|---|
| `codex-development-workflow` | A feature, bug fix, refactor, or repository change needs the full multi-stage development lifecycle. | The task is a tiny isolated edit with no meaningful planning/review/state workflow. |
| `context-efficiency` | Repository exploration may consume significant context, the codebase is unfamiliar/large, or a long task needs compact state tracking. | The relevant file and exact change are already known and small. |
| `plan-to-ticket` | Work is non-trivial, spans multiple modules/steps, has dependencies, or should be implemented incrementally. | A single obvious self-contained change can be safely completed directly. |
| `plantuml-skill` | Architecture, flow, sequence, component, deployment, ER, or other technical relationships are easier to understand visually. Prefer it for 3+ interacting components, cross-service flows, important sequences, and deployment topology. | The change is trivial or a diagram would add no information. |
| Relevant project/test skill | Behavior changed and a specialist test procedure exists for that area. | Documentation-only or non-behavioral changes do not require it. |
| `frontend-click-test` | Frontend interaction, navigation, forms, buttons, routing, or user-visible browser behavior changed. | Backend-only, infrastructure-only, or documentation-only changes. |
| `code-review` | Implementation is complete and relevant tests pass; use it before publication for meaningful code changes. | Pure documentation or trivial edits where review would add no value. |
| `repo-current-state` | Verified repository behavior, architecture, dependencies, deployment, or important project state changed and the repository maintains `docs/Repo_Current_State.md`. | No repository-state facts changed or the target repository does not use that state document. |
| `github-push-when-ready` | Before any commit or push. | Never skip when a commit or push is going to happen. |
| `bark-finish-notify` | After implementation and validation are finished, immediately before the final response. | Do not invoke during intermediate steps; invoke only once per task. |

### Skill Rules

- The orchestration policy lives here; specialist procedural details live in their respective `SKILL.md` files.
- When a specialist skill is invoked, follow that skill rather than reimplementing its procedure from this file.
- Do not invoke a specialist skill only because it is installed.
- Prefer the most specific applicable skill.
- If two skills overlap, use the narrower specialist skill for its domain and keep this file as the high-level lifecycle.
- If a required specialist skill is unavailable, report that limitation instead of silently inventing a weaker substitute.
- Avoid duplicate exploration across skills or subagents.

## Validation

Use progressive validation:

`Local check -> Unit test -> Module test -> Integration test -> Full test`

- Start with the smallest relevant validation.
- Do not repeatedly run full build, test, or typecheck for small changes.
- Expand validation when architecture, public interfaces, shared modules, or integration paths changed.
- Before completion, run the level of verification justified by the actual change scope.

## Subagents

- Do not use subagents for simple tasks.
- Use them only when independent work can clearly proceed in parallel.
- Give each subagent one small, explicit, independent responsibility.
- Avoid having multiple agents explore the same code or solve the same problem.
- Keep each subagent's context minimal.

## Completion Notification

- After implementation and validation are finished, send exactly one Bark notification before the final response.
- Follow `/root/.codex/skills/bark-finish-notify/SKILL.md` when available.
- Command:

```bash
python3 /root/.codex/skills/bark-finish-notify/scripts/send_bark.py --summary "<short concrete result>"
```

- The summary must be short, concrete, and reflect the actual result.
- For blocked or partial work, state that clearly in the summary.
- Bark failure does not block task completion, but mention the notification failure in the final response.

## Git

- One commit should contain one feature or one clear purpose.
- Split larger work into multiple functional commits.
- Before commit, inspect at least `git status` and `git diff --stat`.
- Read only relevant file diffs when full diff output would be large.
- Use `i-zrhe2016` as the Git commit identity where repository policy allows it.
- Do not commit or push `AGENTS.md` or `CLAUDE.md` into target projects when those files are local agent instructions. This workflow repository itself is an exception because `AGENTS.md` is intentionally versioned as workflow documentation.
- Never commit passwords, tokens, API keys, private keys, `.env`, or other secrets.
