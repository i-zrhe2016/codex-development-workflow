# Review Runner Implementation

`run_review.py` is the recoverability layer behind `pr-review`; it is not a
second review policy. Run it from a clean, published PR branch with the actual
remote base ref:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main
```

The runner invokes `ocr review --from <scope> --to <head>`, streams the output,
and stores state and logs under the worktree Git metadata directory
`ocr-review/`. The state records the base, head, named feature branch, selected
scope, execution status, and assessment. A worktree lock prevents concurrent
runs; matching completed executions can be reused.

The first or unbound run uses the complete base-to-head range. When the saved
state is a completed, assessed result for the same branch and base and the
current head is a descendant, the runner can select the previous assessed head
for bounded execution. `--force-full` overrides that selection. The `pr-review`
Skill decides when full coverage is required.

Execution completion is not a review pass. After reading the complete saved
conclusion and checking prior findings, record the assessment:

```bash
python3 <skill-dir>/scripts/run_review.py \
  --base origin/main --record pass --note 'Verified no blocking findings'
```

Use `--record blocking` with evidence when confirmed blockers remain. Missing
conclusions, interrupted runs, tool errors, stale bases, and changed heads are
incomplete conditions; preserve the log and resolve the cause before retrying.
The runner never publishes changes or merges a PR.
