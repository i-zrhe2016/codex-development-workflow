# Context Efficiency

`context-efficiency` is the repository's focused guidance for long-running
coding, search, and debugging work. Its purpose is to keep only the context
needed for the current decision while preserving the goal, constraints,
evidence, and recovery state.

The runtime instructions live in [`SKILL.md`](../../../skills/context-efficiency/SKILL.md).

## What it provides

- Extract the current goal, scope, acceptance criteria, constraints, and known
  state before reading broadly.
- Search first with targeted tools such as `rg` and `rg --files`; read only the
  files and sections relevant to the current slice.
- Bound command output and validation scope so a long session does not turn
  into an unbounded repository scan.
- Keep a short recovery summary covering completed work, important decisions,
  unresolved issues, and the next action.

## How it fits the workflow

Use this skill while understanding the repository and executing a slice. It is
an efficiency aid, not a replacement for planning, acceptance criteria,
testing, review, or correctness checks. The workflow remains single-agent:
load the smallest sufficient context, make one scoped change, validate it, and
record the resulting state.

Efficiency must not weaken correctness, security, privacy, or the user's
explicit request. When evidence is insufficient, expand the context or the
verification scope deliberately and record why.

See the [workflow usage guide](../../workflow/usage.md) for the surrounding
Plan/Slice/Execute lifecycle.

## Maintenance

Update this document when the skill's purpose or repository integration
changes. Detailed operational rules belong in the runtime [`SKILL.md`](../../../skills/context-efficiency/SKILL.md).
