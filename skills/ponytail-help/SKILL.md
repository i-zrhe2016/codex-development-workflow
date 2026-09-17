---
name: ponytail-help
description: >
  Quick-reference card for all ponytail modes, skills, and commands.
  One-shot display, not a persistent mode. Trigger: $ponytail-help,
  "ponytail help", "what ponytail commands", "how do I use ponytail".
---

# Ponytail Help

Display this reference card when invoked. One-shot, do NOT change mode,
write flag files, or persist anything.

## Levels

| Level | Trigger | What change |
|-------|---------|-------------|
| **Lite** | `$ponytail lite` | Build what's asked, name the lazier alternative in one line. |
| **Full** | `$ponytail` or `$ponytail full` | The ladder enforced: YAGNI → stdlib → native → one line → minimum. Default. |
| **Ultra** | `$ponytail ultra` | YAGNI extremist. Deletion before addition. Challenges requirements before building. |

The selected level applies to the current request. Repeat the argument on a
later request when a different level is wanted.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| **ponytail** | `$ponytail` | Lazy mode itself. Simplest solution that works. |
| **ponytail-review** | `$ponytail-review` | Over-engineering review: `L42: yagni: factory, one product. Inline.` |
| **ponytail-audit** | `$ponytail-audit` | Whole-repo over-engineering audit: ranked list of what to delete. |
| **ponytail-debt** | `$ponytail-debt` | Harvest `ponytail:` shortcut comments into a tracked ledger. |
| **ponytail-gain** | `$ponytail-gain` | Measured-impact scoreboard: less code, less cost, more speed. |
| **ponytail-help** | `$ponytail-help` | This card. |

In Codex, invoke these as `$ponytail`, `$ponytail-review`, and
`$ponytail-help`; the bundled workflow keeps the companion skills available for
explicit invocation.

## Scope

The bundled Codex integration has no persistent mode file, environment-variable
reader, or `off` command. The core skill may be selected implicitly for coding
requests; companion skills are explicitly invoked with their `$...` names.

## Update

This bundled copy is updated from the workflow repository. From a checkout of
`codex-development-workflow`, run:

```bash
bash scripts/install-all.sh --update
```

Restart Codex after the update.

## More

Full docs + examples: https://github.com/DietrichGebert/ponytail
