# Workflow Usage Guide

Use `codex-development-workflow` as the entry point for repository work. It
keeps architecture and scope at the Plan/Slice level while keeping validation
inside each Slice.

## Staged workflow

```text
Requirement -> Classify -> Understand -> Plan -> Slice -> Execute
           -> Next Slice? -> Integration tests -> Self review
           -> State / Docs -> Redaction if needed -> Commit / Push
           -> Optional Deploy / Verify / Rollback
```

- **Tiny:** use a concise plan and one implicit Slice.
- **Normal:** plan the relevant area and execute one or more focused Slices.
- **Complex:** use `plan-to-ticket` for dependency-ordered Slices and load only
  the context required by the current Slice.

For every Slice, define:

```text
Goal, Scope, Out of scope, Dependencies, Acceptance criteria,
Relevant context/files, Test strategy, Test level, Test cases,
Validation command
```

Implement only one dependency-ready Slice at a time. If an implementation
assumption is wrong, stop and return to Plan or split the Slice instead of
growing the patch.

## Slice execution and verification

Use test-first development for behavior changes, bug fixes, regressions, API
behavior, core business logic, data processing, and high-risk code when a
meaningful failing test can be produced. For docs, configuration, dependency
updates, styling, typo fixes, simple refactors, and exploratory work, use
direct focused validation without forcing RED/GREEN.

Choose one bounded verification level:

| Level | Use |
|---|---|
| `minimal` | Tiny changes, docs, configuration, styling, simple scripts. |
| `focused` | Default; checks directly tied to Slice acceptance criteria. |
| `regression` | Bug fixes, cross-module changes, demonstrated regression risk. |
| `full` | High-risk, release gates, or explicit requirements. |

Run the smallest set that provides sufficient evidence. Stop after the chosen
level passes unless acceptance criteria, failure evidence, affected boundaries,
release requirements, or the user justify escalation. Report the level,
commands, result, evidence, and escalation reason.

## Review and recovery

Review is a single-agent self-review of the integrated result, not a mandatory
review step inside every Slice. Run integration/regression checks after all
Slices, then review the final safe diff. A blocking finding requires an affected
test rerun; repeat review when the fix materially changes behavior.

Read `docs/Repo_Current_State.md` at the start of planning and update it after
meaningful verified work. Use it as a compact recovery point for current focus,
implemented behavior, in-progress Slice, known failures, constraints, and the
next Slice. It is not a session transcript, full backlog, or test report.

## Output classification and redaction

Classify the complete final output set before staging or committing and before
every separate sharing, export, upload, or publication boundary. Include
source, docs, logs, configs, images, screenshots, exports, filenames, and
metadata.

Record recipient/environment, purpose, required utility, and whether controlled
reversibility is allowed. Default to non-reversible handling.

If no potentially sensitive surface exists, record the inspected scope and skip
reason. Otherwise invoke `data-document-redaction` and follow
[redaction.md](redaction.md). Only `pass` advances; `needs_review` and
`blocked` stop the boundary transition.

## Completion order

`Integration tests -> Self review -> Repo state/docs if needed -> Output classification -> Redaction if needed -> Commit/Push -> Optional Deploy/Verify/Rollback`

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
