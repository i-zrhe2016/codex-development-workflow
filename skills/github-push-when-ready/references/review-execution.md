# Recoverable Codex review

Run from a clean, published PR branch. Resolve and refresh the actual PR base
before starting; a stale local base cannot detect upstream changes. Before
starting a new review, the runner refuses a bare local base branch that differs
from its configured upstream (`<remote>/<branch>`, falling back to
`origin/<branch>`) instead of silently reviewing the wrong range, and it points
at that remote ref in the error. Recording and saved-execution reuse do not
start a new review, so the stale-base guard is skipped there; branch-identity
checks still apply.

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main
```

The runner invokes built-in `codex review`, streams output, and saves logs,
branch, and base/head identities under the worktree's Git metadata directory
`codex-review/`. Incremental reuse is bound to the exact current feature branch;
an unbound legacy state or a state from another branch falls back to a full
review. Keep logs local: review output may contain repository-sensitive material.
The runner neither publishes changes nor merges PRs.

After reading the complete conclusion, the main agent records its assessment:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main --record blocking --note 'Confirmed findings and affected behavior'
```

Use `--record pass` only after confirming no blocking findings remain, including
findings carried forward from earlier runs. Exit zero means execution completed,
not review passed. Missing conclusions, interruption and errors are incomplete.

Batch the round's fixes, run affected tests and applicable redaction, commit and
push. For the normal post-review fix loop, after the main agent confirms that
the fixes are bounded:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main
```

The runner automatically selects incremental coverage for every commit after
the previous completed, assessed `pass` or `blocking` head when the base is
unchanged and history is still a descendant. `--incremental` remains accepted
as an explicit request, but is not required. The main agent must use a full
review for architecture, public API or interface, security or authentication,
database or schema, cross-module behavior, base/history changes, rewrites or
rebases, or uncertain impact. Filename/line-count heuristics alone cannot
establish eligibility. Original findings must be verified separately; the CLI
does not automatically inherit the previous review's conversation.

Matching completed executions are reused; inspect the saved log rather than
starting again. One active runner per worktree is enforced. If an orphaned child
is reported, inspect that exact process and its log before restarting. Do not
infer failure or health merely from process existence or silence.

Use `--force-full` when new evidence requires full coverage of an already
reviewed head. This bypasses result reuse and incremental scope, but never the
active lock. A first review, a pending or incomplete assessment, a changed
base, or rewritten/divergent history already falls back to full coverage.

Before merge, current CI and affected tests must still pass. A passing
incremental review is sufficient; do not repeat a full AI review merely because
the PR head advanced.

Progress notices report elapsed and output-idle time every five minutes. After
15 minutes inspect logs and process/error evidence: continue useful work, and
terminate only a confirmed stalled or failed run. There is no automatic timeout
pass or blind retry. Preserve evidence when a session is interrupted.
