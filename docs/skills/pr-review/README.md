# PR Review

`pr-review` is the single pull-request merge gate. It is invoked after a PR is
created or updated and returns either `PASS` or `BLOCKED` with actionable file
references. The runtime [`SKILL.md`](../../../skills/pr-review/SKILL.md) is the
authoritative review policy.

The bundled `run_review.py` runner is an implementation detail used to execute
the configured `ocr review` command while preserving recoverable local state.
Its logs, lock, saved execution, and focused tests live with this Skill:

```text
skills/pr-review/
├── SKILL.md
├── agents/openai.yaml
├── references/review-execution.md
├── rules/document-review.json
├── scripts/run_review.py
└── tests/test_run_review.py
```

When the selected PR range contains Markdown, `run_review.py` uses the bundled
document rule to route `.md` and `.markdown` files through the same OpenCode
Review execution. The rule is trusted Skill content, not a rule loaded from
the reviewed branch; documentation remains under the single `PASS`/`BLOCKED`
merge decision.

`github-push-when-ready` stops at a PR-ready state. Tests and redaction remain
separate workflow gates, and merge/cleanup remain owned by the root workflow.

## Maintenance

Keep this index aligned with [`skills/pr-review/`](../../../skills/pr-review/)
and [`references/skill-map.md`](../../../references/skill-map.md). Keep review
decision policy in the runtime Skill rather than duplicating it in publication
or execution documentation.
