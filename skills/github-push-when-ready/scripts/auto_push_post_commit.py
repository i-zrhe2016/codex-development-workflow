#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from pathlib import Path

from github_about import ensure_github_about
from git_push_utils import AUTO_PUSH_SKIP_ENV, GitError, assess_repo, run_git_or_raise
from publish_identity import (
    ensure_git_identity,
    github_push_environment,
    load_publish_identity,
    verify_unpublished_commit_identities,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Push the latest commit after post-commit when the repo is safe to publish."
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress skip messages and only print push results or errors.",
    )
    return parser


def emit(message: str, quiet: bool) -> None:
    if not quiet:
        print(message)


def main() -> int:
    args = build_parser().parse_args()
    if os.environ.get(AUTO_PUSH_SKIP_ENV):
        emit(f"auto-push skipped: {AUTO_PUSH_SKIP_ENV} is set.", args.quiet)
        return 0

    report = assess_repo(Path(args.repo))
    action = report["recommended_action"]
    if action != "push" or not report["safe_to_push"]:
        reason = report["reasons"][0] if report["reasons"] else action
        emit(f"auto-push skipped: {reason}", args.quiet)
        return 0

    repo = Path(str(report["repo_path"]))
    remote = report["preferred_remote"]
    branch = report["branch"]
    upstream = report["upstream"]
    if not remote or not branch:
        emit("auto-push skipped: remote or branch could not be determined.", args.quiet)
        return 0

    try:
        identity = load_publish_identity(repo)
        ensure_git_identity(repo, identity)
        verify_unpublished_commit_identities(
            repo,
            identity,
            upstream=str(upstream) if upstream else None,
            remote=str(remote),
        )

        about = ensure_github_about(repo, str(remote))
        if not about.ok:
            emit(f"auto-push skipped: GitHub About check failed: {about.message}", args.quiet)
            return 0
        if about.changed:
            emit(f"GitHub About updated: {about.description}", args.quiet)

        with github_push_environment(repo, str(remote), identity) as push_env:
            if upstream:
                run_git_or_raise(repo, "push", env=push_env)
            else:
                run_git_or_raise(
                    repo,
                    "push",
                    "-u",
                    str(remote),
                    str(branch),
                    env=push_env,
                )
    except GitError as error:
        print(f"auto-push failed: {error}")
        return 1

    print(f"auto-pushed branch {branch} to {remote}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
