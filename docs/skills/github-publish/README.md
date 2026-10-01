# GitHub Publish

`github-publish` is the publication gate for feature branches, commits,
pushes, and pull requests. It checks that the repository is ready to publish,
that the change has one clear purpose, that the commit follows Conventional
Commits 1.0.0, and that no secrets or unrelated changes are being shipped.

The runtime instructions live in [`SKILL.md`](../../../skills/github-publish/SKILL.md).

## Delivery principles

- Inspect the branch, remote, diff, and repository checks before publishing.
- Create or resume a non-default branch before publishing; every published
  change uses the branch and PR path. When the branch carries Plan metadata, the
  gate validates it; when it does not, publication proceeds normally.
- Keep one coherent requirement or Plan per commit.
- Use a Conventional Commit message with the correct scope and intent.
- For this repository, configure the approved non-root local identity and GitHub account `i-zrhe2016`; other target repositories must configure their own non-root identity.
- The guarded commit/push paths verify author, committer, unpublished commits, active GitHub account, and the credentials used for GitHub publication.
- If the default branch cannot be determined from the actual GitHub push target, guarded publication fails closed and requires manual review.
- The guard evaluates the effective push remote/refspec separately from a pull-tracking upstream, so fork workflows can push a feature branch while still tracking an upstream default branch.
- After the PR is created or updated, return `PR ready`; the model may merge once the existing validation and publication gates are satisfied.
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
| [`assess_push_readiness.py`](../../../skills/github-publish/scripts/assess_push_readiness.py) | Inspect repository readiness |
| [`auto_push_post_commit.py`](../../../skills/github-publish/scripts/auto_push_post_commit.py) | Guard an optional post-commit push |
| [`conventional_commits.py`](../../../skills/github-publish/scripts/conventional_commits.py) | Validate commit message format |
| [`github_about.py`](../../../skills/github-publish/scripts/github_about.py) | Check or update GitHub About metadata |
| [`git_push_utils.py`](../../../skills/github-publish/scripts/git_push_utils.py) | Shared readiness and Git helpers |
| [`install_post_commit_hook.py`](../../../skills/github-publish/scripts/install_post_commit_hook.py) | Install guarded commit/push hooks |
| [`publish_identity.py`](../../../skills/github-publish/scripts/publish_identity.py) | Enforce repository and GitHub publication identity |
| [`push_if_ready.py`](../../../skills/github-publish/scripts/push_if_ready.py) | Push after readiness checks |

For example, a local readiness assessment can be run with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 skills/github-publish/scripts/assess_push_readiness.py --json
```

Use the exact command and authorization appropriate to the current task before
running any commit or push action. Once the PR is ready, return control to the model for merge.

## Maintenance

Update this index when delivery policy or managed scripts change. The runtime
[`SKILL.md`](../../../skills/github-publish/SKILL.md) remains the
authoritative operational procedure.
