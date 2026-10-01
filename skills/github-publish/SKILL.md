---
name: github-publish
description: "Enforce this repository's deterministic publication guards: branch readiness, repository-local publication identity, Conventional Commit policy, GitHub About metadata, safe push state, and PR requirement. Use when committing, pushing, or opening/updating a PR. Codex already knows Git/GitHub operations; this Skill supplies only repository-specific checks and scripts."
---

# GitHub Publication Guard

Codex handles ordinary Git and GitHub operations natively. Use this Skill only to enforce repository-specific publication policy and deterministic checks.

## Required policy

Before publication:

- work must be on a non-default branch;
- required verification and applicable redaction must already be satisfactory;
- selected changes must belong to the intended task;
- commit subjects must follow Conventional Commits 1.0.0;
- repository-local author/committer identity and configured GitHub account must match policy;
- the target GitHub repository description must be non-empty;
- no unresolved conflicts or unsafe behind-upstream state may be pushed;
- every published coherent change must have a pull request;
- force-push requires explicit user authorization.

Do not direct-push repository changes to the default branch.

## Deterministic tooling

Assess readiness:

```bash
python3 <skill-dir>/scripts/assess_push_readiness.py --json
```

Use the guarded commit/push path when appropriate:

```bash
python3 <skill-dir>/scripts/push_if_ready.py \
  --message "type(scope): description" \
  --pathspec path/to/file \
  --execute
```

The scripts enforce repository-local identity, commit header policy, GitHub account binding, repository About metadata, branch/upstream safety, and explicit staging boundaries.

Optional managed hooks are installed with:

```bash
python3 <skill-dir>/scripts/install_post_commit_hook.py --repo .
```

## PR boundary

After a guarded push, create or update the task's PR using native GitHub tooling. Do not create duplicate PRs. A successful commit or push is not equivalent to PR readiness.

Stop at `PR ready` unless merge is separately authorized.

## Failure behavior

If any guard cannot be verified, stop publication and report the exact blocker. Do not bypass repository policy with raw Git commands.
