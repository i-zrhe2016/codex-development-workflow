#!/usr/bin/env python3

"""Resolve and enforce the per-repository identity used for publication."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Mapping
from urllib.parse import urlparse

from git_push_utils import GitError, load_remote_urls, run_git, run_git_or_raise


IDENTITY_NAME_CONFIG = "codex.identity.name"
IDENTITY_EMAIL_CONFIG = "codex.identity.email"
GITHUB_ACCOUNT_CONFIG = "codex.github.account"
GITHUB_HOST = "github.com"
GIT_IDENTITY_PATTERN = re.compile(r"^(?P<name>.*) <(?P<email>[^>]+)>")


@dataclass(frozen=True)
class PublishIdentity:
    name: str
    email: str
    github_account: str


def _local_config(repo: Path, key: str) -> str | None:
    result = run_git(repo, "config", "--local", "--get", key)
    if result.returncode != 0 or not result.stdout:
        return None
    return result.stdout


def load_publish_identity(repo: Path) -> PublishIdentity:
    values = {
        IDENTITY_NAME_CONFIG: _local_config(repo, IDENTITY_NAME_CONFIG),
        IDENTITY_EMAIL_CONFIG: _local_config(repo, IDENTITY_EMAIL_CONFIG),
        GITHUB_ACCOUNT_CONFIG: _local_config(repo, GITHUB_ACCOUNT_CONFIG),
    }
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise GitError(
            "publication identity is not configured for this repository; "
            "set local codex.identity.name, codex.identity.email, and "
            "codex.github.account before publishing"
        )

    name = values[IDENTITY_NAME_CONFIG] or ""
    email = values[IDENTITY_EMAIL_CONFIG] or ""
    github_account = values[GITHUB_ACCOUNT_CONFIG] or ""
    if _is_root_identity(name, email, github_account):
        raise GitError("publication identity must not use root or a root GitHub account")
    return PublishIdentity(name=name, email=email, github_account=github_account)


def _is_root_identity(name: str, email: str, github_account: str) -> bool:
    root_values = {name.strip().lower(), email.strip().lower(), github_account.strip().lower()}
    return (
        "root" in root_values
        or "root@localhost" in root_values
        or github_account.strip().lower().startswith("root@")
    )


def _parse_git_identity(value: str) -> tuple[str, str] | None:
    match = GIT_IDENTITY_PATTERN.match(value.strip())
    if not match:
        return None
    return match.group("name"), match.group("email")


def ensure_git_identity(repo: Path, identity: PublishIdentity) -> None:
    """Make local Git config and effective author/committer identity agree."""
    run_git_or_raise(repo, "config", "--local", "user.name", identity.name)
    run_git_or_raise(repo, "config", "--local", "user.email", identity.email)

    for variable in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        value = run_git_or_raise(repo, "var", variable)
        parsed = _parse_git_identity(value)
        if parsed != (identity.name, identity.email):
            raise GitError(
                f"{variable} does not match the configured publication identity; "
                "refusing to create or publish a commit"
            )


def _default_remote_ref(repo: Path, remote: str | None) -> str | None:
    if not remote:
        return None
    symbolic = run_git(
        repo,
        "symbolic-ref",
        "--quiet",
        "--short",
        f"refs/remotes/{remote}/HEAD",
    )
    if symbolic.returncode == 0 and symbolic.stdout:
        return symbolic.stdout
    for branch in ("main", "master"):
        candidate = f"{remote}/{branch}"
        if run_git(repo, "rev-parse", "--verify", candidate).returncode == 0:
            return candidate
    return None


def verify_unpublished_commit_identities(
    repo: Path,
    identity: PublishIdentity,
    *,
    upstream: str | None,
    remote: str | None,
) -> None:
    """Reject unpublished commits with an unexpected author or committer."""
    base = upstream or _default_remote_ref(repo, remote)
    revision = f"{base}..HEAD" if base else "-1"
    result = run_git(
        repo,
        "log",
        "--format=%H%x00%an%x00%ae%x00%cn%x00%ce",
        revision,
    )
    if result.returncode != 0:
        raise GitError("could not inspect unpublished commit identities")

    for line in result.stdout.splitlines():
        fields = line.split("\x00")
        if len(fields) != 5:
            raise GitError("could not parse an unpublished commit identity")
        _commit, author_name, author_email, committer_name, committer_email = fields
        if (author_name, author_email) != (identity.name, identity.email):
            raise GitError("an unpublished commit has an unexpected author identity")
        if (committer_name, committer_email) != (identity.name, identity.email):
            raise GitError("an unpublished commit has an unexpected committer identity")


def _run_gh(*args: str) -> subprocess.CompletedProcess[str]:
    gh = shutil.which("gh")
    if gh is None:
        raise GitError("GitHub CLI (gh) is required to verify publication identity")
    return subprocess.run(
        [gh, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def verify_github_account(identity: PublishIdentity) -> str:
    """Return the active GitHub token only after verifying its account."""
    account = _run_gh("api", "user", "--hostname", GITHUB_HOST, "--jq", ".login")
    login = account.stdout.strip()
    if account.returncode != 0 or not login:
        raise GitError("GitHub CLI authentication could not be verified")
    if login != identity.github_account:
        raise GitError("GitHub CLI is authenticated as a different account")

    credential = _run_gh("auth", "token", "--hostname", GITHUB_HOST)
    if credential.returncode != 0 or not credential.stdout.strip():
        raise GitError("GitHub CLI token could not be obtained for the configured account")
    return credential.stdout.strip()


def _remote_push_url(repo: Path, remote: str) -> str:
    urls = load_remote_urls(repo).get(remote, {})
    push_url = urls.get("push") or urls.get("fetch")
    if not push_url:
        raise GitError("the selected GitHub remote has no push URL")
    return push_url


def _https_push_environment(identity: PublishIdentity, credential: str) -> dict[str, str]:
    # Clear configured credential helpers and supply the verified gh token through
    # an askpass process, so an unrelated root or stale HTTPS credential cannot be used.
    return {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "credential.helper",
        "GIT_CONFIG_VALUE_0": "",
        "CODEX_GITHUB_USERNAME": identity.github_account,
        "CODEX_GITHUB_TOKEN": credential,
    }


def _ssh_authentication_matches(output: str, account: str) -> bool:
    return bool(re.search(rf"\bHi {re.escape(account)}!", output))


@contextmanager
def github_push_environment(
    repo: Path,
    remote: str,
    identity: PublishIdentity,
) -> Iterator[Mapping[str, str]]:
    """Yield an environment that binds Git publication to the verified account."""
    credential = verify_github_account(identity)
    push_url = _remote_push_url(repo, remote)
    parsed = urlparse(push_url)
    if parsed.username or parsed.password:
        raise GitError("the GitHub remote URL must not contain embedded credentials")

    if parsed.scheme in {"http", "https"} and parsed.hostname == GITHUB_HOST:
        with tempfile.TemporaryDirectory(prefix="codex-github-askpass-") as temp_dir:
            askpass = Path(temp_dir) / "askpass.sh"
            askpass.write_text(
                "#!/bin/sh\n"
                "case \"$1\" in\n"
                "  *[Uu]sername*) printf '%s' \"$CODEX_GITHUB_USERNAME\" ;;\n"
                "  *) printf '%s' \"$CODEX_GITHUB_TOKEN\" ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            askpass.chmod(0o700)
            environment = _https_push_environment(identity, credential)
            environment["GIT_ASKPASS"] = str(askpass)
            yield environment
        return

    if push_url.startswith("git@github.com:") or push_url.startswith("ssh://git@github.com/"):
        ssh = shutil.which("ssh")
        if ssh is None:
            raise GitError("ssh is required to verify the GitHub SSH publication account")
        check = subprocess.run(
            [ssh, "-T", "-o", "BatchMode=yes", "git@github.com"],
            check=False,
            capture_output=True,
            text=True,
        )
        if not _ssh_authentication_matches(
            check.stdout + check.stderr,
            identity.github_account,
        ):
            raise GitError("GitHub SSH authentication could not be verified for the configured account")
        yield {"GIT_SSH_COMMAND": f"{ssh} -o BatchMode=yes"}
        return

    raise GitError("the selected remote is not a supported GitHub HTTPS or SSH URL")
