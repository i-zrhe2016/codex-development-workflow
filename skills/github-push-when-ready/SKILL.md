---
name: github-push-when-ready
description: Guard every Git commit, GitHub push, and pull request by assessing repository readiness, enforcing Conventional Commits 1.0.0, keeping one requirement per commit, completing GitHub About metadata, and publishing only when safe. Use whenever the agent is about to commit, push, or open a PR, finishes a coherent unit of work in a GitHub-connected repo, or is asked to ship or sync changes.
---

# GitHub Push When Ready

## Overview

Inspect the current repository and enforce the publication path for every
change: `Plan branch -> implement -> test -> applicable redaction -> commit
-> push -> create/update PR -> PR ready`. Prefer the bundled scripts for
repeatable checks; only publish after the task is complete, validations have
passed, and the working tree changes belong to the task at hand. A PR is
mandatory for Docs, Code, Tests, Config, Refactor, Bugfix, Feature, Dependency,
and CI/CD changes; none may direct-push around the gate.

## Required Git and GitHub Identity

- Identity is a per-target-repository policy. For this repository, configure the approved non-root identity and GitHub account:

  ```bash
  git config --local codex.identity.name <approved-name>
  git config --local codex.identity.email <approved-email>
  git config --local codex.github.account <approved-account>
  ```

- When targeting another repository, configure that repository's own non-root identity instead of inheriting this repository's values. Do not change global Git configuration or GitHub credentials unless the user explicitly requests it.
- Before a commit, the guarded paths set the repository-local `user.name` and `user.email` from the configured policy and verify the effective author and committer identities. They refuse `root`, `root@localhost`, and other mismatched identities.
- Before a push or pull-request operation, verify the active GitHub CLI account matches `codex.github.account`. The guarded push path also binds HTTPS Git credentials to the verified `gh` token and verifies the configured SSH account when the remote uses SSH; it refuses to publish when the account cannot be verified.
- The manual `gh pr create` step must use the same verified GitHub account. Git author metadata alone does not determine the GitHub account used for publication.

## Mandatory Use and Commit Boundaries

- Invoke this skill before every action or script that will create a Git commit, push to GitHub, or open/update a pull request. Do not run a direct `git commit`, `git push`, amend, or equivalent publishing workflow first and assess afterward.
- For every requirement, including feature, fix, documentation, configuration, dependency, test, or CI/CD work, ensure its Plan Issue and Plan branch exist before editing. Commit the completed Plan unit, push that branch, and then create or update one PR for the Plan. Direct default-branch delivery is not an allowed workflow path.
- Group changes by one coherent requirement or Plan. When the worktree contains independent units, commit each unit separately.
- Keep a Plan's implementation, directly related tests, and documentation in the same commit when they form one atomic change. Do not split commits merely by file type.
- If a pending change set contains multiple requirements, split it into one requirement per commit. A commit must not combine unrelated Plans; keep each Plan's implementation, tests, and documentation together.
- Enforce Conventional Commits 1.0.0 for every new commit: `<type>[optional scope][!]: <description>`. The type must be lowercase, the description must be non-empty, and a scope must be non-empty when present. Body and footer content remain allowed by the specification.
- Review the diff for each planned commit and stage only its paths or hunks. Prefer explicit `--pathspec` values; never use `--allow-stage-all` when unrelated or independently committable work is present.
- Validate each functional unit before committing it. Re-run the readiness assessment before each subsequent commit or push because the repository state has changed.
- Do not create empty commits or push again when the assessment returns `noop`.

## Quick Start

Run the readiness check from the repository root:

```bash
python3 <skill-dir>/scripts/assess_push_readiness.py --json
```

Interpret `recommended_action` like this:

- `push`: the repo is clean and has commits ready to publish.
- `commit_then_push`: the repo has local changes and can be committed, then pushed.
- `noop`: nothing needs to be pushed.
- `feature_branch_required`: local changes are on the default branch; create a
  Plan branch before committing or pushing.
- `sync_first`, `resolve_conflicts`, `manual_review`, `no_github_remote`, `not_git_repo`: do not push yet.

Before a GitHub push, treat the repository About as required metadata. For this skill, About means a non-empty GitHub repository description; homepage and topics are optional. If it is empty, derive a concise description from the README or provide one explicitly, update it with GitHub CLI, and verify the update before pushing. If the update cannot be completed, do not push.

After a successful Plan-branch push, check for an existing PR before creating
one. Do not create duplicate PRs. If none exists, verify that GitHub CLI is
authenticated and create the PR against the repository's default branch:

```bash
gh pr create --fill --base <default-branch> --head <feature-branch>
```

When PR creation or update succeeds, report the canonical PR and return
`PR ready`. If it fails after the push, report the branch and exact blocker; do
not claim the change is ready for review.

To enforce commit messages and auto-check/auto-push after every new commit, install the managed `commit-msg` and `post-commit` hooks:

```bash
python3 <skill-dir>/scripts/install_post_commit_hook.py --repo .
```

After that, invalid commit messages are rejected before a commit is created. Each valid local commit then triggers a fresh readiness check. The post-commit hook pushes only a non-default Plan branch when the repo reaches the existing safe `push` state; it never treats a push as a complete delivery. It will not auto-commit leftover changes, and it will skip pushes when the branch is behind upstream, detached, conflicted, on the default branch, when the default branch cannot be determined, or when a GitHub remote is missing.

## Workflow

1. Inspect `git status` and the relevant diff, identify the repository's default branch, and create or resume the Plan branch before editing.
2. Run `assess_push_readiness.py` in the target repo before the first commit or push.
3. Stop immediately if the repo is not a Git repo, has no GitHub remote, is on a detached HEAD, has conflicts, is behind its upstream branch, is on the default branch with work to publish, or has work to publish while the default branch cannot be determined.
4. Treat `commit_then_push` as eligible only when the current functional unit is complete, its checks are green, and the selected paths or hunks contain no unrelated work.
5. Before any push, verify unpublished commit subjects follow Conventional Commits 1.0.0 and check/complete the GitHub repository About description. The guarded scripts do this automatically when executed.
6. Treat `push` as eligible only when the working tree is clean, the local branch is ahead of its upstream or has no upstream yet, and About verification succeeds.
7. Use `push_if_ready.py --execute` with explicit `--pathspec` values for the standard guarded commit-and-push flow. If one file mixes multiple functional units, stage only the intended hunks manually after assessment, then use the equivalent guarded commit and push commands.
8. After the push succeeds, check for an existing PR and create or update it with `gh pr create`/`gh pr edit` as needed. Record the PR URL or blocker and return `PR ready` when the PR is available and the publication checks are satisfied.
9. For another functional unit, re-inspect the remaining diff and restart this workflow from the readiness assessment.

## Push Rules

- Refuse to push unresolved conflicts or code that failed validation.
- Refuse to commit or push work from the repository's default branch; create or resume the Plan branch first. If the default branch cannot be determined, require manual review instead of assuming the current branch is safe.
- Resolve the effective push remote and refspec, including `branch.<name>.pushRemote`, `remote.pushDefault`, and `push.default`; block publication when that target is the default branch or cannot be determined. A pull-tracking upstream may intentionally point to a different repository.
- Refuse to push if the branch is behind upstream; rebase or pull first.
- Refuse to push when the GitHub repository About description is empty or could not be verified after an attempted update.
- Refuse to force-push unless the user explicitly asks for it.
- Refuse to auto-stage all changes when unrelated user work is mixed into the same worktree; ask before combining unrelated edits into one commit.
- Refuse to combine independent features into one commit merely because they were completed in the same session.
- Prefer `git push -u <remote> <branch>` when the branch has no upstream yet.
- Prefer clear commit messages tied to the completed task boundary.
- Require one PR per coherent Plan/requirement, including fixes, documentation, configuration, tests, dependencies, and CI/CD changes; keep related tests and documentation in that PR.
- Do not treat a successful commit or push as a successful PR. Report each stage separately.

## Resources

### `scripts/assess_push_readiness.py`

Use this script first. It inspects branch state, upstream state, worktree cleanliness, conflicts, and GitHub remote wiring, then returns a recommendation plus suggested commands.

### `scripts/push_if_ready.py`

Use this script after the repo is confirmed ready. It performs the guarded flow below:

```bash
python3 <skill-dir>/scripts/push_if_ready.py \
  --message "feat(scope): describe the completed task" \
  --pathspec path/to/file \
  --execute
```

Behavior:

- Dry-run by default.
- Commit only when the readiness check returns `commit_then_push`.
- Reject commit messages whose first line does not follow the Conventional Commits 1.0.0 header format.
- Require `--pathspec` or `--allow-stage-all` before creating a commit.
- Check the selected GitHub repository About before committing or pushing; if its description is missing, fill it from the README or `--about-description`, then verify it.
- Enforce the configured repository identity and verified GitHub account before committing or pushing; the post-commit hook uses the same guard.
- Push with `git push` when upstream exists.
- Push with `git push -u <remote> <branch>` when upstream is missing.
- It does not create a pull request. After it succeeds, check for an existing PR and run `gh pr create --fill --base <default-branch> --head <feature-branch>` when needed, then return the canonical PR as `PR ready`.

### `scripts/install_post_commit_hook.py`

Installs managed Git `commit-msg` and `post-commit` hooks into the target repository. The `commit-msg` hook rejects messages that violate Conventional Commits 1.0.0. The `post-commit` hook calls `auto_push_post_commit.py` after every successful commit and exits cleanly even when the push is skipped.

Use `--force` only when you intentionally want to replace an existing unmanaged hook. The installer writes a backup file before replacing it.

### `scripts/auto_push_post_commit.py`

Runs the same readiness assessment after each valid commit, enforces the configured commit and GitHub identities, completes/verifies GitHub About metadata, and pushes only when `recommended_action` is `push` on a non-default Plan branch. It does not open PRs because a post-commit hook lacks the PR title/body and branch intent; use the explicit Create / Update PR step after the push. This keeps the automatic mode conservative: partial commits, unresolved conflicts, missing GitHub remotes, missing About metadata, unverified identities, default-branch work, and branches that are behind upstream are all skipped instead of being forced through.

### `scripts/publish_identity.py`

Resolves the target repository's local publication policy, verifies effective
author/committer identities and unpublished commits, verifies the active
GitHub CLI account, and supplies account-bound credentials for the guarded
GitHub push.

Set `CODEX_GITHUB_AUTO_PUSH_SKIP=1` to bypass one hook invocation. `push_if_ready.py` sets this automatically for its own commit step so a scripted `commit_then_push` flow does not double-trigger the push.

## Response Pattern

Summarize the decision in three parts:

1. Whether the repo is connected to GitHub.
2. Whether the repo is ready to commit, ready to push, or blocked.
3. Whether a PR already exists, was created, or is blocked, with the exact next command when applicable.

If a push was executed, report the branch, remote, and whether a commit was created first. If a PR was created or found, report its URL.
If a push was skipped, report the blocking condition instead of hand-waving.
