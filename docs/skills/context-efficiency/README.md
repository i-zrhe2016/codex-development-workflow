# Context Efficiency

`context-efficiency` is the repository's focused guidance for long-running
coding, search, and debugging work. Its purpose is to keep only the context
needed for the current decision while preserving the goal, constraints,
evidence, and recovery state.

The runtime instructions live in [`SKILL.md`](../../../skills/context-efficiency/SKILL.md).

## What it provides

- Mandatory RTK execution for task shell commands: supported summaries for
  navigation, `rtk proxy` for exact output, unsupported commands, and existing
  test/review/publication gates. Bootstrap checks and installation are the only
  shell exception; missing RTK must be resolved or reported as blocked.
- The [RTK operating reference](../../../skills/context-efficiency/references/rtk.md)
  defines command selection, log/exit-code preservation, and dependency checks.
  The skill installer copies these instructions; it does not install the RTK
  binary or enable global command-rewriting hooks.

- Extract the current goal, scope, acceptance criteria, constraints, and known
  state before reading broadly.
- Search first with targeted tools such as `rtk proxy rg` and `rtk proxy rg --files`; read only the
  files and sections relevant to the current slice.
- Bound command output and validation scope so a long session does not turn
  into an unbounded repository scan.
- Keep a short recovery summary covering completed work, important decisions,
  unresolved issues, and the next action.

## How it fits the workflow

Use this skill while understanding the repository and executing a Slice. It is
an efficiency aid, not a replacement for planning, acceptance criteria,
testing, review, or correctness checks. The main agent keeps the decision
context focused; delegated workers load only their bounded task context and
return concise evidence.

Efficiency must not weaken correctness, security, privacy, or the user's
explicit request. When evidence is insufficient, expand the context or the
verification scope deliberately and record why.

See the [workflow usage guide](../../workflow/usage.md) for the surrounding
Plan/Ticket/Slice/Execute lifecycle.

## Maintenance

Update this document when the skill's purpose or repository integration
changes. Detailed operational rules belong in the runtime [`SKILL.md`](../../../skills/context-efficiency/SKILL.md).
