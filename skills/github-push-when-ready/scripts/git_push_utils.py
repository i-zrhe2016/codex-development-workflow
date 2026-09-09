#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import urlparse

CONFLICT_CODES = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}
AUTO_PUSH_SKIP_ENV = "CODEX_GITHUB_AUTO_PUSH_SKIP"


@dataclass
class GitResult:
    returncode: int
    stdout: str
    stderr: str


class GitError(RuntimeError):
    pass


def run_git(repo: Path, *args: str, env: Mapping[str, str] | None = None) -> GitResult:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        env=None if env is None else {**os.environ, **env},
        text=True,
    )
    return GitResult(
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def run_git_or_raise(repo: Path, *args: str, env: Mapping[str, str] | None = None) -> str:
    result = run_git(repo, *args, env=env)
    if result.returncode != 0:
        command = shlex.join(["git", "-C", str(repo), *args])
        detail = result.stderr or result.stdout or "git command failed"
        raise GitError(f"{command}: {detail}")
    return result.stdout


def is_github_url(url: str) -> bool:
    return bool(
        re.search(r"(^git@github\.com:|^ssh://git@github\.com/|github\.com[:/])", url)
    )


def github_repo_slug(remote_url: str) -> str | None:
    """Return owner/repository for a supported GitHub remote URL."""
    if remote_url.startswith("git@github.com:"):
        path = remote_url.removeprefix("git@github.com:")
    else:
        try:
            parsed = urlparse(remote_url)
        except ValueError:
            return None
        if parsed.hostname != "github.com":
            return None
        path = parsed.path

    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/")
    if len(parts) != 2 or not all(parts):
        return None
    return "/".join(parts)


def parse_remote_urls(raw: str) -> dict[str, dict[str, str]]:
    remotes: dict[str, dict[str, str]] = {}
    for line in raw.splitlines():
        match = re.match(r"(\S+)\s+(\S+)\s+\((fetch|push)\)", line)
        if not match:
            continue
        name, url, direction = match.groups()
        remotes.setdefault(name, {})[direction] = url
    return remotes


def load_remote_urls(repo: Path) -> dict[str, dict[str, str]]:
    remotes = parse_remote_urls(run_git_or_raise(repo, "remote", "-v"))
    remote_names = run_git(repo, "remote")
    if remote_names.returncode != 0:
        return remotes

    for name in [line.strip() for line in remote_names.stdout.splitlines() if line.strip()]:
        fetch_url = run_git(repo, "config", "--get", f"remote.{name}.url")
        if fetch_url.returncode == 0 and fetch_url.stdout:
            remotes.setdefault(name, {})["fetch"] = fetch_url.stdout

        push_url = run_git(repo, "config", "--get", f"remote.{name}.pushurl")
        if push_url.returncode == 0 and push_url.stdout:
            remotes.setdefault(name, {})["push"] = push_url.stdout
        elif fetch_url.returncode == 0 and fetch_url.stdout:
            remotes.setdefault(name, {})["push"] = fetch_url.stdout

    return remotes


def summarize_status(raw: str) -> dict[str, Any]:
    lines = raw.splitlines()
    branch_line = lines[0] if lines else ""
    entries = lines[1:] if branch_line.startswith("## ") else lines
    staged = 0
    unstaged = 0
    untracked = 0
    conflicted = 0
    for entry in entries:
        code = entry[:2]
        if code == "??":
            untracked += 1
            continue
        if code in CONFLICT_CODES or "U" in code:
            conflicted += 1
        if len(code) >= 1 and code[0] not in {" ", "?"}:
            staged += 1
        if len(code) >= 2 and code[1] not in {" ", "?"}:
            unstaged += 1
    return {
        "branch_line": branch_line[3:] if branch_line.startswith("## ") else branch_line,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "conflicted": conflicted,
        "total_changes": staged + unstaged + untracked + conflicted,
    }


def parse_branch(branch_line: str) -> tuple[str | None, bool]:
    if not branch_line:
        return None, False
    if branch_line.startswith("No commits yet on "):
        branch_line = branch_line.removeprefix("No commits yet on ")
        return branch_line.split("...", 1)[0], False
    head = branch_line.split("...", 1)[0]
    if head.startswith("HEAD "):
        return None, True
    return head, False


def parse_ahead_behind(branch_line: str) -> tuple[int, int]:
    ahead = 0
    behind = 0
    match = re.search(r"\[(.+)\]$", branch_line)
    if not match:
        return ahead, behind
    for item in match.group(1).split(","):
        item = item.strip()
        if item.startswith("ahead "):
            ahead = int(item.removeprefix("ahead "))
        if item.startswith("behind "):
            behind = int(item.removeprefix("behind "))
    return ahead, behind


def choose_remote(github_remotes: dict[str, dict[str, str]], upstream: str | None) -> str | None:
    if upstream:
        upstream_remote = upstream.split("/", 1)[0]
        if upstream_remote in github_remotes:
            return upstream_remote
    if "origin" in github_remotes:
        return "origin"
    if github_remotes:
        return sorted(github_remotes)[0]
    return None


def resolve_push_remote(
    repo: Path,
    github_remotes: dict[str, dict[str, str]],
    branch: str | None,
    upstream: str | None,
) -> str | None:
    """Resolve the remote selected by plain ``git push``."""
    config_keys = []
    if branch:
        config_keys.append(f"branch.{branch}.pushRemote")
    config_keys.append("remote.pushDefault")
    for key in config_keys:
        configured = run_git(repo, "config", "--get", key)
        if configured.returncode == 0 and configured.stdout:
            return configured.stdout
    return choose_remote(github_remotes, upstream)


def load_effective_push_urls(repo: Path, remote: str | None) -> list[str]:
    """Return every push URL after Git's push-url and rewrite rules are applied."""
    if not remote:
        return []
    result = run_git(repo, "remote", "get-url", "--all", "--push", remote)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line]


def resolve_effective_push_branch(
    repo: Path,
    branch: str | None,
    upstream: str | None,
    push_remote: str | None,
) -> str | None:
    """Resolve the branch targeted by plain ``git push`` when it is unambiguous."""
    if not branch or not push_remote:
        return None

    configured_refspec = run_git(repo, "config", "--get-all", f"remote.{push_remote}.push")
    if configured_refspec.returncode == 0 and configured_refspec.stdout:
        return None

    mirror = run_git(repo, "config", "--bool", "--get", f"remote.{push_remote}.mirror")
    if mirror.returncode not in (0, 1):
        return None
    if mirror.returncode == 0 and mirror.stdout.lower() == "true":
        return None

    push_default = run_git(repo, "config", "--get", "push.default")
    mode = push_default.stdout.lower() if push_default.returncode == 0 and push_default.stdout else "simple"
    if mode in {"matching", "nothing"}:
        return None

    upstream_remote = None
    upstream_branch = None
    if upstream and "/" in upstream:
        upstream_remote, upstream_branch = upstream.split("/", 1)
    if mode == "upstream" and upstream_remote != push_remote:
        return None
    if mode == "simple" and upstream_remote and upstream_remote != push_remote:
        return branch

    push_ref = run_git(repo, "rev-parse", "--symbolic-full-name", "@{push}")
    if push_ref.returncode == 0 and push_ref.stdout:
        prefix = "refs/remotes/"
        if push_ref.stdout.startswith(prefix):
            remote_and_branch = push_ref.stdout.removeprefix(prefix)
            remote_name, separator, target_branch = remote_and_branch.partition("/")
            if separator and remote_name == push_remote and target_branch:
                return target_branch

    if mode == "current":
        return branch
    if mode == "upstream" and upstream and "/" in upstream:
        return upstream_branch
    if mode == "simple":
        if not upstream or "/" not in upstream:
            return branch
        return branch if upstream_branch == branch else None
    return None


def build_push_command(remote: str, branch: str, upstream: str | None) -> str:
    if upstream:
        return "git push"
    return shlex.join(["git", "push", "-u", remote, branch])


def resolve_default_branch(push_url: str | None) -> str | None:
    """Resolve the default branch from the actual GitHub push target."""
    if not push_url:
        return None

    slug = github_repo_slug(push_url)
    gh = shutil.which("gh")
    if not slug or not gh:
        return None

    environment = {
        **os.environ,
        "GH_PROMPT_DISABLED": "1",
        "GIT_TERMINAL_PROMPT": "0",
    }
    try:
        result = subprocess.run(
            [
                gh,
                "api",
                f"repos/{slug}",
                "--hostname",
                "github.com",
                "--jq",
                "{default_branch: .default_branch}",
            ],
            check=False,
            capture_output=True,
            env=environment,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return None

    if result.returncode == 0:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None
        default_branch = payload.get("default_branch")
        if isinstance(default_branch, str) and default_branch and "\n" not in default_branch:
            return default_branch

    return None


def assess_repo(repo_path: str | Path) -> dict[str, Any]:
    repo = Path(repo_path).resolve()
    top_level = run_git(repo, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0:
        return {
            "repo_path": str(repo),
            "is_git_repo": False,
            "github_remote_connected": False,
            "recommended_action": "not_git_repo",
            "safe_to_push": False,
            "reasons": ["Current path is not inside a Git repository."],
            "commands": [],
        }

    repo = Path(top_level.stdout)
    status = summarize_status(run_git_or_raise(repo, "status", "--porcelain=v1", "--branch"))
    branch, detached = parse_branch(status["branch_line"])
    ahead, behind = parse_ahead_behind(status["branch_line"])

    upstream_result = run_git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    upstream = upstream_result.stdout if upstream_result.returncode == 0 else None

    if upstream:
        counts = run_git(repo, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        if counts.returncode == 0 and counts.stdout:
            behind_count, ahead_count = counts.stdout.split()
            behind = int(behind_count)
            ahead = int(ahead_count)

    remotes = load_remote_urls(repo)
    github_remotes = {
        name: urls
        for name, urls in remotes.items()
        if any(is_github_url(url) for url in urls.values())
    }
    push_remote = resolve_push_remote(repo, github_remotes, branch, upstream)
    preferred_remote = push_remote if push_remote in github_remotes else None
    push_urls = load_effective_push_urls(repo, push_remote)
    default_branches = [resolve_default_branch(url) for url in push_urls]
    default_branch = (
        default_branches[0]
        if default_branches and all(branch_name == default_branches[0] for branch_name in default_branches)
        else None
    )
    effective_push_branch = resolve_effective_push_branch(repo, branch, upstream, push_remote)
    has_commits = run_git(repo, "rev-parse", "--verify", "HEAD").returncode == 0
    has_changes = any(status[key] > 0 for key in ("staged", "unstaged", "untracked", "conflicted"))

    reasons: list[str] = []
    commands: list[str] = []
    recommended_action = "noop"
    safe_to_push = False

    if not github_remotes:
        recommended_action = "no_github_remote"
        reasons.append("No GitHub remote is configured for this repository.")
    elif detached or not branch:
        recommended_action = "manual_review"
        reasons.append("Repository is on a detached HEAD or branch name could not be determined.")
    elif status["conflicted"] > 0:
        recommended_action = "resolve_conflicts"
        reasons.append("Working tree contains unresolved merge conflicts.")
    elif behind > 0:
        recommended_action = "sync_first"
        reasons.append(f"Branch is behind upstream by {behind} commit(s).")
        if upstream:
            tracking_remote = upstream.split("/", 1)[0]
            remote_branch = upstream.split("/", 1)[1]
            commands.append(shlex.join(["git", "pull", "--rebase", tracking_remote, remote_branch]))
    elif default_branch is None and (
        has_changes or ahead > 0 or (has_commits and not upstream)
    ):
        recommended_action = "manual_review"
        reasons.append(
            "Could not determine the repository default branch from the actual GitHub push target; "
            "preserve the work and confirm the target branch before publishing."
        )
    elif default_branch and branch == default_branch and has_changes:
        recommended_action = "feature_branch_required"
        reasons.append(
            f"Working tree changes are on the default branch '{default_branch}'; "
            "create a feature branch before committing or pushing."
        )
        commands.append("git switch -c <type>/<short-description>")
    elif default_branch and branch == default_branch and (
        ahead > 0 or (has_commits and not upstream)
    ):
        recommended_action = "manual_review"
        reasons.append(
            f"Default branch '{default_branch}' contains unpublished commit(s); "
            "preserve the work and move it to a feature branch before publishing."
        )
    elif default_branch and effective_push_branch is None and (
        has_changes or ahead > 0 or (has_commits and not upstream)
    ):
        recommended_action = "manual_review"
        reasons.append(
            "Could not determine the effective branch targeted by plain 'git push'; "
            "confirm the push refspec before publishing."
        )
    elif default_branch and effective_push_branch == default_branch and (
        has_changes or ahead > 0 or (has_commits and not upstream)
    ):
        recommended_action = "manual_review"
        reasons.append(
            f"Plain 'git push' targets the default branch '{default_branch}'; "
            "preserve the work and publish through a feature branch and PR."
        )
    elif has_changes:
        recommended_action = "commit_then_push"
        safe_to_push = True
        reasons.append("Working tree has local changes that can be committed before pushing.")
        if preferred_remote and branch:
            commands.extend(["git add -A", 'git commit -m "<message>"', build_push_command(preferred_remote, branch, upstream)])
    elif ahead > 0 or (preferred_remote and has_commits and not upstream):
        recommended_action = "push"
        safe_to_push = True
        if ahead > 0:
            reasons.append(f"Branch is ahead of upstream by {ahead} commit(s).")
        else:
            reasons.append("Branch has no upstream yet and can be published to GitHub.")
        if preferred_remote and branch:
            commands.append(build_push_command(preferred_remote, branch, upstream))
    elif not has_commits:
        recommended_action = "noop"
        reasons.append("Repository has no commits to publish yet.")
    else:
        recommended_action = "noop"
        reasons.append("Repository is clean and has nothing new to push.")

    return {
        "repo_path": str(repo),
        "is_git_repo": True,
        "github_remote_connected": bool(github_remotes),
        "github_remotes": [
            {
                "name": name,
                "fetch_url": urls.get("fetch"),
                "push_url": urls.get("push"),
            }
            for name, urls in sorted(github_remotes.items())
        ],
        "preferred_remote": preferred_remote,
        "push_remote": push_remote,
        "effective_push_branch": effective_push_branch,
        "default_branch": default_branch,
        "branch": branch,
        "detached_head": detached,
        "upstream": upstream,
        "ahead": ahead,
        "behind": behind,
        "has_commits": has_commits,
        "worktree": {
            "staged": status["staged"],
            "unstaged": status["unstaged"],
            "untracked": status["untracked"],
            "conflicted": status["conflicted"],
            "clean": not has_changes,
        },
        "recommended_action": recommended_action,
        "safe_to_push": safe_to_push,
        "reasons": reasons,
        "commands": commands,
    }


def print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))
