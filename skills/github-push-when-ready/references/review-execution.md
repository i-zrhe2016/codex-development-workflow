# Recoverable Codex review

Run from a clean, published PR branch. Resolve and refresh the actual PR base
before starting; a stale local base cannot detect upstream changes.

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main
```

The runner invokes built-in `codex review`, streams output, and saves logs and
base/head identities under the worktree's Git metadata directory `codex-review/`.
Keep logs local: review output may contain repository-sensitive material.
The runner neither publishes changes nor merges PRs.

After reading the complete conclusion, the main agent records its assessment:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main --record blocking --note 'Confirmed findings and affected behavior'
```

Use `--record pass` only after confirming no blocking findings remain, including
findings carried forward from earlier runs. Exit zero means execution completed,
not review passed. Missing conclusions, interruption and errors are incomplete.

Batch the round's fixes, run affected tests and applicable redaction, commit and
push. If only bounded fixes remain and the main agent has checked their impact:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main --incremental
```

Incremental review covers every commit after the previous assessed head. The
runner falls back to full coverage when the base changed or history diverged.
The main agent must omit `--incremental` for interface/security boundary changes,
cross-module behavior or uncertain impact. Filename/line-count heuristics alone
cannot establish eligibility. Original findings must be verified separately;
the CLI does not automatically inherit the previous review's conversation.

Matching completed executions are reused; inspect the saved log rather than
starting again. One active runner per worktree is enforced. If an orphaned child
is reported, inspect that exact process and its log before restarting. Do not
infer failure or health merely from process existence or silence.

Use `--force-full` when new evidence requires full coverage of an already reviewed
head. This bypasses result reuse and incremental scope, but never the active lock.

Progress notices report elapsed and output-idle time every five minutes. After
15 minutes inspect logs and process/error evidence: continue useful work, and
terminate only a confirmed stalled or failed run. There is no automatic timeout
pass or blind retry. Preserve evidence when a session is interrupted.
