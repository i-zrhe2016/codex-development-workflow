---
name: github-push-when-ready
description: "Guard every commit, GitHub push, and PR creation/update; also use after coherent GitHub-repo work or requests to ship/sync. Enforce readiness, repository identity, Conventional Commits, atomic requirements, and GitHub About metadata."
---

# GitHub Push When Ready

Invoke **before** every commit/push/PR action or equivalent script, including
amend; never publish first and assess afterward. Every change type (Docs, Code,
Tests, Config, Refactor, Bugfix, Feature, Dependency, CI/CD) follows:
`feature branch -> implement -> verify -> applicable redaction -> commit -> push
-> create/update PR -> PR ready`. Publish only completed, validated task-owned
work; prefer bundled guards. Commit/push alone never
completes delivery; a PR is mandatory, with no direct-default-branch bypass.

## Identity

Configure the approved **non-root policy locally for each target repository**:

```bash
git config --local codex.identity.name <approved-name>
git config --local codex.identity.email <approved-email>
git config --local codex.github.account <approved-account>
```

Do not inherit this repository's identity for another target or change global
Git configuration/GitHub credentials without an explicit user request.
Before committing, guards set local `user.name`/`user.email` from policy and
verify effective author/committer identities, rejecting `root`, `root@localhost`
and mismatches. Before push/PR operations, the active `gh` account must match
`codex.github.account`; guarded HTTPS pushes bind credentials to its verified
`gh` token, and SSH remotes require verifying the configured SSH account.
Unverifiable accounts block publication. Manual `gh pr create` uses the same
verified account; Git author metadata does not select the publishing account.

## Readiness and boundaries

Run from the target repository root before each commit/push, including subsequent
units; state changes invalidate earlier assessments:

```bash
python3 <skill-dir>/scripts/assess_push_readiness.py --json
```

It inspects branch/upstream, cleanliness, conflicts and GitHub wiring, returning
`recommended_action` and suggested commands:

| Action | Meaning / response |
| --- | --- |
| `push` | Clean tree; ahead of upstream or no upstream. Eligible only after validation, identity and About verification. |
| `commit_then_push` | Local changes; eligible only for a completed, validated unit with no unrelated selected changes. |
| `noop` | Nothing to publish; no empty commit or repeat push. |
| `feature_branch_required` | Work on default branch; create/resume a feature branch before committing/pushing. |
| `sync_first`, `resolve_conflicts`, `manual_review`, `no_github_remote`, `not_git_repo` | Stop publication; resolve the blocker. |

Stop immediately for non-Git repositories, missing GitHub remotes, detached HEAD,
conflicts, failed validation, behind-upstream branches (rebase/pull first), work
to publish on default, or an indeterminate default branch. Resolve the effective
push remote/refspec, including `branch.<name>.pushRemote`, `remote.pushDefault`
and `push.default`; block if the target is default or indeterminate. A
pull-tracking upstream may intentionally belong to another repository. Unknown
default requires manual review. Never force-push without an explicit user request.

Use one PR per coherent published change. One commit owns one requirement or
atomic Plan: keep its implementation,
tests and documentation together, never split merely by file type or combine
unrelated Plans/features because they share a session. Split independent units;
review each diff and stage only its paths/hunks. Prefer explicit `--pathspec`;
never `--allow-stage-all` with unrelated/independently committable work, and ask
before combining unrelated user edits. Validate each unit. Plan metadata, when
present, must validate; its absence permits normal publication—a persisted Plan
is a planning decision, not a publication prerequisite.

Use clear messages tied to the completed task boundary. Every new/unpublished
commit subject must follow Conventional Commits 1.0.0:
`<type>[optional scope][!]: <description>`; lowercase type, non-empty description
and non-empty scope when present. Specification-compliant bodies/footers allowed.
Before each push, verify all unpublished commit subjects comply; guarded
scripts do this automatically.

Before pushing, verify GitHub **About**: a non-empty repository description is
required; homepage/topics optional. If empty, derive a concise description from
README or supply one explicitly, update via GitHub CLI, and verify. Failed
update/verification blocks push. Guarded scripts perform this automatically.

## Procedure and tools

1. Inspect `git status`/relevant diff, identify default branch, and create/resume
   a non-default branch **before editing**. Assess readiness and enforce the
   gates above.
2. For the standard guarded commit/push, run:

   ```bash
   python3 <skill-dir>/scripts/push_if_ready.py \
     --message "feat(scope): describe the completed task" \
     --pathspec path/to/file \
     --execute
   ```

   Default is dry-run. Commit only for `commit_then_push`; reject invalid message
   headers; require `--pathspec` or `--allow-stage-all`. Check/complete About from
   README or `--about-description` **before commit or push**, and enforce identity.
   If one file mixes units, assess then manually stage intended hunks and use
   equivalent guarded commit/push commands. Existing upstream uses `git push`;
   missing upstream uses `git push -u <remote> <branch>`.
3. After successful push, check for an existing PR; update with `gh pr edit` as
   needed, never duplicate. If absent, verify CLI authentication/account and
   create against default:

   ```bash
   gh pr create --fill --base <default-branch> --head <feature-branch>
   ```

   Scripts do not create PRs. Return canonical PR URL and `PR ready` only when
   creation/update succeeds and publication checks pass. Failure after push:
   report branch/exact blocker; do not claim ready for review.
4. For another unit, re-inspect remaining diff and restart assessment.

Optional managed hooks:

```bash
python3 <skill-dir>/scripts/install_post_commit_hook.py --repo .
```

| Resource | Contract |
| --- | --- |
| `scripts/install_post_commit_hook.py` | Installs `commit-msg` (reject invalid Conventional Commits before creation) and `post-commit` (call `auto_push_post_commit.py` after every valid commit; exit cleanly on skipped push). Use `--force` only to intentionally replace an unmanaged hook; installer backs it up first. |
| `scripts/auto_push_post_commit.py` | Fresh assessment after each valid commit; same identity and About guards; push only safe `push` on non-default. Never auto-commit leftovers or open PRs: hooks lack PR title/body/branch intent. Skip partial work, detached/conflicted/default/unknown-default branches, behind upstream, missing GitHub remote/About, or unverified identities. Use explicit PR step afterward. |
| `scripts/publish_identity.py` | Resolve local target policy; verify effective author/committer, unpublished commits and active CLI account; supply account-bound push credentials. |

Set `CODEX_GITHUB_AUTO_PUSH_SKIP=1` to bypass one hook invocation.
`push_if_ready.py` sets it for its commit step to prevent duplicate pushes.

## Report

State: GitHub connection; ready to commit/push or blocked; PR existing/created/
blocked, with exact next command when applicable. Report each stage separately.
For executed push include branch, remote and whether a commit was created first;
for existing/created PR include URL; for skipped push give the precise blocker.
