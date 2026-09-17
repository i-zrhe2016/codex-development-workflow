---
name: pr-review
description: Review a published pull request before merge. Use after a PR is created or updated. Block merge on correctness, security, regression, or requirement violations and repeat after fixes until the PR passes.
---

# PR Review

Review the complete PR after it is created or updated.

## Flow

1. Resolve the PR's actual base branch.
2. Run the bundled recoverable review runner:

   `python3 <skill-dir>/scripts/run_review.py --base origin/<base>`

3. Read the complete conclusion and assess the findings.

Return `BLOCKED` when a finding can cause:

- incorrect behavior;
- regression;
- security or data risk;
- broken interface or contract;
- unmet acceptance criteria.

Do not block on stylistic preferences or speculative improvements.

4. If blocked:

   - batch the review findings;
   - fix them;
   - run affected tests;
   - run redaction when applicable;
   - commit and push;
   - review again.

5. Return `PASS` only when no blocking findings remain.

## Review scope

The first review always covers the complete PR.

After a small, bounded fix, incremental review may cover changes since the last reviewed head.

Run a complete review again when:

- the base changed;
- history was rewritten or rebased;
- architecture changed;
- public API or interface boundaries changed;
- security or authentication boundaries changed;
- database or schema behavior changed;
- cross-module behavior changed;
- impact is uncertain.

The runner's logs, locks, saved executions, and scope selection are
implementation details. Use [`review-execution.md`](references/review-execution.md)
only when diagnosing or recovering a review execution.

## Output

Return only:

`PASS`

or:

`BLOCKED`
followed by actionable findings with file references and brief reasoning.
