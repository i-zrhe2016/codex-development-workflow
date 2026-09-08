#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from git_push_utils import GitError  # noqa: E402
from publish_identity import (  # noqa: E402
    ensure_git_identity,
    github_push_environment,
    load_publish_identity,
    _ssh_authentication_matches,
    verify_unpublished_commit_identities,
)


class PublishIdentityTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return completed.stdout.strip()

    def configure_identity(self, repo: Path) -> None:
        self.run_git(repo, "config", "user.name", "i-zrhe2016")
        self.run_git(repo, "config", "user.email", "zrhe2016@gmail.com")
        self.run_git(repo, "config", "codex.identity.name", "i-zrhe2016")
        self.run_git(repo, "config", "codex.identity.email", "zrhe2016@gmail.com")
        self.run_git(repo, "config", "codex.github.account", "i-zrhe2016")

    def test_correct_identity_passes_and_root_policy_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="publish-identity-test-") as temp:
            repo = Path(temp)
            self.run_git(repo, "init", "-q", "-b", "main")
            self.configure_identity(repo)
            identity = load_publish_identity(repo)
            ensure_git_identity(repo, identity)
            self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): verify identity")
            verify_unpublished_commit_identities(
                repo,
                identity,
                upstream=None,
                remote=None,
            )

            self.run_git(repo, "config", "codex.identity.name", "root")
            with self.assertRaises(GitError):
                load_publish_identity(repo)

    def test_unpublished_mismatched_identity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="publish-identity-test-") as temp:
            repo = Path(temp)
            self.run_git(repo, "init", "-q", "-b", "main")
            self.configure_identity(repo)
            identity = load_publish_identity(repo)
            self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): baseline")
            bad_env = os.environ.copy()
            bad_env.update(
                {
                    "GIT_AUTHOR_NAME": "root",
                    "GIT_AUTHOR_EMAIL": "root@localhost",
                    "GIT_COMMITTER_NAME": "root",
                    "GIT_COMMITTER_EMAIL": "root@localhost",
                }
            )
            self.run_git(
                repo,
                "commit",
                "--allow-empty",
                "-m",
                "docs(test): wrong identity",
                env=bad_env,
            )
            with self.assertRaises(GitError):
                verify_unpublished_commit_identities(
                    repo,
                    identity,
                    upstream=None,
                    remote=None,
                )

    def test_https_push_uses_verified_gh_account_credentials(self) -> None:
        with tempfile.TemporaryDirectory(prefix="publish-identity-test-") as temp:
            root = Path(temp)
            repo = root / "repo"
            fake_bin = root / "bin"
            repo.mkdir()
            fake_bin.mkdir()
            self.run_git(repo, "init", "-q", "-b", "main")
            self.configure_identity(repo)
            self.run_git(
                repo,
                "remote",
                "add",
                "origin",
                "https://github.com/i-zrhe2016/codex-development-workflow.git",
            )
            fake_gh = fake_bin / "gh"
            fake_gh.write_text(
                "#!/bin/sh\n"
                "case \"$1\" in\n"
                "  api) printf '%s\\n' 'i-zrhe2016' ;;\n"
                "  auth) printf '%s\\n' 'test-credential' ;;\n"
                "  *) exit 1 ;;\n"
                "esac\n",
                encoding="utf-8",
            )
            fake_gh.chmod(0o700)
            identity = load_publish_identity(repo)
            old_path = os.environ.get("PATH", "")
            os.environ["PATH"] = f"{fake_bin}{os.pathsep}{old_path}"
            try:
                with github_push_environment(repo, "origin", identity) as push_env:
                    credential_result = subprocess.run(
                        ["git", "-C", str(repo), "credential", "fill"],
                        input="protocol=https\nhost=github.com\n\n",
                        check=True,
                        capture_output=True,
                        text=True,
                        env={**os.environ, **push_env},
                    )
                    credential_lines = dict(
                        line.split("=", 1)
                        for line in credential_result.stdout.splitlines()
                        if "=" in line
                    )
                    self.assertEqual(credential_lines.get("username"), "i-zrhe2016")
                    self.assertEqual(credential_lines.get("password"), "test-credential")
                    askpass_path = Path(push_env["GIT_ASKPASS"])
                    self.assertTrue(askpass_path.is_file())
                self.assertFalse(askpass_path.exists())
                self.run_git(
                    repo,
                    "remote",
                    "set-url",
                    "origin",
                    "https://stale-user:stale-credential@github.com/i-zrhe2016/codex-development-workflow.git",
                )
                with self.assertRaises(GitError):
                    with github_push_environment(repo, "origin", identity):
                        pass
            finally:
                os.environ["PATH"] = old_path

    def test_ssh_success_message_matches_only_configured_account(self) -> None:
        message = "Hi i-zrhe2016! You've successfully authenticated, but GitHub does not provide shell access."
        self.assertTrue(_ssh_authentication_matches(message, "i-zrhe2016"))
        self.assertFalse(_ssh_authentication_matches(message, "another-account"))


if __name__ == "__main__":
    unittest.main()
