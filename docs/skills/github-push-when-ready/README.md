# GitHub Push When Ready

`github-push-when-ready` is the delivery gate for feature branches, commits,
pushes, pull requests, merges, and source-branch cleanup. It checks that the
repository is ready to publish, that the change has one clear purpose, that the
commit follows Conventional Commits 1.0.0, and that no secrets or unrelated
changes are being shipped.

The runtime instructions live in [`SKILL.md`](../../../skills/github-push-when-ready/SKILL.md).

## Delivery principles

- Inspect the branch, remote, diff, and repository checks before publishing.
- Create or resume a non-default feature branch before editing; every change
  type uses the branch and PR path.
- Keep one coherent feature or fix per commit.
- Use a Conventional Commit message with the correct scope and intent.
- For this repository, configure the local identity `i-zrhe2016 <zrhe2016@gmail.com>` and GitHub account `i-zrhe2016`; other target repositories must configure their own non-root identity.
- The guarded commit/push paths verify author, committer, unpublished commits, active GitHub account, and the credentials used for GitHub publication.
- If the default branch cannot be determined from the actual GitHub push target, guarded publication fails closed and requires manual review.
- The guard evaluates the effective push remote/refspec separately from a pull-tracking upstream, so fork workflows can push a feature branch while still tracking an upstream default branch.
- After a PR is verified as merged, delete its source branch remotely and locally after switching to and synchronizing the base branch; retain the default branch and unmerged branches.
- Create or update the PR after the branch is pushed, then run the built-in
  `codex review` as Automatic Review without waiting for user confirmation.
  Blocking findings repeat the affected Test, Redaction when applicable,
  Commit, Push, and `codex review` steps.
- The project-scoped `reviewer` is optional supplemental analysis and never
  replaces the mandatory `codex review` gate.
- Merge only after Automatic Review passes, update the default branch, close the
  Ticket when one exists, and then update State / Docs.
- Run the smallest verification set that provides sufficient evidence, then
  escalate when risk or failures require it.
- Check GitHub repository metadata when the task includes publishing or a pull
  request.
- Stop and report blockers instead of bypassing failing checks, missing
  credentials, or unclear scope.

The gate protects the publication boundary; it does not authorize publishing
without the user's request or an explicitly scoped workflow. Local `AGENTS.md`,
credentials, `.env` files, private keys, and other secrets must remain out of
commits.

## Managed scripts

| Script | Purpose |
|---|---|
| [`assess_push_readiness.py`](../../../skills/github-push-when-ready/scripts/assess_push_readiness.py) | Inspect repository readiness |
| [`auto_push_post_commit.py`](../../../skills/github-push-when-ready/scripts/auto_push_post_commit.py) | Guard an optional post-commit push |
| [`conventional_commits.py`](../../../skills/github-push-when-ready/scripts/conventional_commits.py) | Validate commit message format |
| [`github_about.py`](../../../skills/github-push-when-ready/scripts/github_about.py) | Check or update GitHub About metadata |
| [`git_push_utils.py`](../../../skills/github-push-when-ready/scripts/git_push_utils.py) | Shared readiness and Git helpers |
| [`install_post_commit_hook.py`](../../../skills/github-push-when-ready/scripts/install_post_commit_hook.py) | Install guarded commit/push hooks |
| [`publish_identity.py`](../../../skills/github-push-when-ready/scripts/publish_identity.py) | Enforce repository and GitHub publication identity |
| [`push_if_ready.py`](../../../skills/github-push-when-ready/scripts/push_if_ready.py) | Push after readiness checks |

For example, a local readiness assessment can be run with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/github-push-when-ready/scripts/assess_push_readiness.py --json
```

Use the exact command and authorization appropriate to the current task before
running any commit or push action.

## Maintenance

Update this index when delivery policy or managed scripts change. The runtime
[`SKILL.md`](../../../skills/github-push-when-ready/SKILL.md) remains the
authoritative operational procedure.
