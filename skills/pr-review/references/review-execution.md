# Review Runner Implementation

`run_review.py` is the recoverability layer behind `pr-review`; it is not a
second review policy. Run it from a clean, published PR branch with the actual
remote base ref:

```bash
python3 <skill-dir>/scripts/run_review.py --base origin/main
```

The runner invokes `ocr review --from <scope> --to <head>`, streams the output,
and stores state and logs under the worktree Git metadata directory
`ocr-review/`. For a range containing `.md` or `.markdown` files, it adds the
trusted rule at `rules/document-review.json` from the installed Skill bundle.
That rule uses OpenCode Review's include mechanism to admit Markdown and adds
checks for factual consistency, links, commands, contradictions, operational
prerequisites, and sensitive data. Code-only ranges keep the original command
unchanged. A worktree lock prevents concurrent runs; matching completed
executions can be reused.

The saved state records `document_review`, the detected `document_paths`, and
the trusted rule path. A successful process with no supported files, a missing
conclusion, or an empty output is still pending assessment and is never a
review pass by itself.

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
