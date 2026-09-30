---
name: github-push-when-ready
description: "Guard Git commit, push, and pull-request publication in a GitHub repository. Use before committing, pushing, syncing, or opening/updating a PR. Enforce a non-default branch, repository identity, Conventional Commits, coherent staging, readiness checks, GitHub About metadata, and one PR for published work."
---

# GitHub Push When Ready

Use the bundled scripts as the deterministic publication guard. Do not restate their implementation in chat.

## Standard flow

1. Inspect status/diff and ensure the work is on a non-default branch.
2. Run:
   ```bash
   python3 <skill-dir>/scripts/assess_push_readiness.py --json
   ```
3. Stop on `feature_branch_required`, `sync_first`, `resolve_conflicts`, `manual_review`, `no_github_remote`, or `not_git_repo`.
4. Confirm the current functional unit is complete and validated. Stage only its explicit paths/hunks.
5. Publish with:
   ```bash
   python3 <skill-dir>/scripts/push_if_ready.py \
     --message "feat(scope): describe the completed task" \
     --pathspec path/to/file \
     --execute
   ```
6. After push, find the existing PR or create one against the default branch. Do not create duplicates.
7. Return the branch, commit, and canonical PR URL. A push without a PR is not `PR ready`.

## Hard gates

- Never commit or push publishable work from the default branch.
- One commit carries one coherent requirement/Plan; keep its implementation, tests, and directly related docs together when atomic.
- Use Conventional Commits 1.0.0.
- Never stage unrelated user work. Prefer explicit pathspecs/hunks; use stage-all only when the whole worktree is one intended unit.
- Do not publish unresolved conflicts, failed required validation, a detached HEAD, an unknown unsafe push target, or a branch behind upstream.
- Do not force-push unless explicitly requested.
- Require a GitHub remote and a non-empty repository About description.
- Enforce the repository-local approved Git author/committer identity and active GitHub account. Configure `codex.identity.name`, `codex.identity.email`, and `codex.github.account` per target repository; do not change global identity unless requested.
- When Plan metadata exists, preserve its recorded branch/base/PR contract. A persisted Plan is not required for ordinary publication.
- Every published Docs/Code/Tests/Config/Refactor/Bugfix/Feature/Dependency/CI change goes through a PR.

## Script ownership

- `assess_push_readiness.py`: branch/upstream/worktree/remote readiness.
- `push_if_ready.py`: guarded commit and push, including identity, commit-message, About, and path selection checks.
- `publish_identity.py`, `github_about.py`, `conventional_commits.py`, and `git_push_utils.py`: policy helpers used by the guard.
- `install_post_commit_hook.py`: optional managed commit-msg/post-commit hooks; install only when persistent hook behavior is desired.
- `auto_push_post_commit.py`: conservative post-commit push only; it never creates a PR.

Treat script failures as blockers; do not manually bypass a guard to reproduce its intended effect.
