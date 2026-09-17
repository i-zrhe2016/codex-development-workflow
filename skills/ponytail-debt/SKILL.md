---
name: ponytail-debt
description: >
  Harvest every `ponytail:` comment in the codebase into a debt ledger, so the
  deliberate shortcuts and deferrals ponytail leaves behind get tracked instead
  of rotting into "later means never". Use when the user says "ponytail debt",
  "$ponytail-debt", "what did ponytail defer", "list the shortcuts", "ponytail
  ledger", or "what did we mark to do later". One-shot report, changes nothing.
---

Every deliberate ponytail shortcut is marked with a `ponytail:` comment naming
its ceiling and upgrade path. This collects them into one ledger so a deferral
can't quietly become permanent.

## Scan

Search source files for comment markers, skipping prose files, `node_modules`,
`.git`, and common build output:

`rg -n --hidden -g '!node_modules/**' -g '!.git/**' -g '!dist/**' -g '!build/**' -g '!coverage/**' -g '!vendor/**' -g '!*.md' -g '!*.rst' -g '!*.txt' '(^|[[:space:]])(#[[:space:]]*|//[[:space:]]*|/\*\*?[[:space:]]*|\*[[:space:]]*|<!--[[:space:]]*)ponytail:' .`

The source-file exclusions filter prose examples, while the comment-prefix
alternatives match both standalone and inline markers. Add the comment form or
source-file exclusion used by the target language when needed.

Each hit is one ledger row. The comment prefix keeps prose that merely mentions
the convention out of the ledger.

## Output

One row per marker, grouped by file:

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`

The convention is `ponytail: <ceiling>, <upgrade path>`, so pull the ceiling
and the trigger straight from the comment. Want an owner per row too? add
`git blame -L<line>,<line>`.

Flag the rot risk: any `ponytail:` comment that names no upgrade path or
trigger gets a `no-trigger` tag, those are the ones that silently rot.

End with `<N> markers, <M> with no trigger.` Nothing found: `No ponytail: debt. Clean ledger.`

## Boundaries

Reads and reports only by default. If the user explicitly asks to persist the
ledger (for example as `PONYTAIL-DEBT.md`), treat that as a normal repository
change and follow the workflow's branch, test, redaction, commit, PR, and review
gates. One-shot; later requests are unaffected.
