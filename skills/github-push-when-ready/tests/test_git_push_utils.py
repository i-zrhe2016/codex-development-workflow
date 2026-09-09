#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import sys
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from git_push_utils import assess_repo, resolve_default_branch  # noqa: E402


class PushReadinessTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory(prefix="push-readiness-test-")
        self.addCleanup(temp.cleanup)
        repo = Path(temp.name)
        self.run_git(repo, "init", "-q", "-b", "main")
        self.run_git(repo, "config", "user.name", "i-zrhe2016")
        self.run_git(repo, "config", "user.email", "test")
        self.run_git(
            repo,
            "remote",
            "add",
            "origin",
            "https://github.com/i-zrhe2016/codex-development-workflow.git",
        )
        self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): baseline")
        return repo

    def assess_with_default_branch(self, repo: Path, default_branch: str | None) -> dict[str, object]:
        with patch("git_push_utils.resolve_default_branch", return_value=default_branch):
            return assess_repo(repo)

    def test_default_branch_is_read_from_push_target_api(self) -> None:
        with patch("git_push_utils.shutil.which", return_value="/usr/bin/gh"), patch(
            "git_push_utils.subprocess.run"
        ) as run:
            run.return_value = subprocess.CompletedProcess(
                ["gh"], 0, '{"default_branch":"release/main"}\n', ""
            )

            result = resolve_default_branch(
                "https://github.com/example/project.git",
            )

        self.assertEqual(result, "release/main")
        command = run.call_args.args[0]
        self.assertEqual(
            command,
            [
                "/usr/bin/gh",
                "api",
                "repos/example/project",
                "--hostname",
                "github.com",
                "--jq",
                "{default_branch: .default_branch}",
            ],
        )
        self.assertEqual(run.call_args.kwargs["timeout"], 10)
        self.assertEqual(run.call_args.kwargs["env"]["GH_PROMPT_DISABLED"], "1")

    def test_default_branch_probe_timeout_fails_closed(self) -> None:
        with patch("git_push_utils.shutil.which", return_value="/usr/bin/gh"), patch(
            "git_push_utils.subprocess.run",
            side_effect=subprocess.TimeoutExpired(["gh"], timeout=10),
        ):
            result = resolve_default_branch(
                "https://github.com/example/project.git"
            )

        self.assertIsNone(result)

    def test_null_default_branch_output_is_unknown(self) -> None:
        with patch("git_push_utils.shutil.which", return_value="/usr/bin/gh"), patch(
            "git_push_utils.subprocess.run"
        ) as run:
            run.return_value = subprocess.CompletedProcess(
                ["gh"], 0, '{"default_branch":null}\n', ""
            )

            result = resolve_default_branch("https://github.com/example/project.git")

        self.assertIsNone(result)

    def test_branch_tracking_default_upstream_requires_manual_review(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.run_git(repo, "switch", "-q", "-c", "work")
        self.run_git(repo, "branch", "--set-upstream-to=origin/main", "work")
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = self.assess_with_default_branch(repo, "main")

        self.assertEqual(report["recommended_action"], "manual_review")
        self.assertFalse(report["safe_to_push"])

    def test_malformed_github_url_fails_closed(self) -> None:
        self.assertIsNone(resolve_default_branch("https://[github.com/example/project"))

    def test_default_branch_changes_require_feature_branch(self) -> None:
        repo = self.make_repo()
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = self.assess_with_default_branch(repo, "main")

        self.assertEqual(report["default_branch"], "main")
        self.assertEqual(report["recommended_action"], "feature_branch_required")
        self.assertFalse(report["safe_to_push"])

    def test_slash_containing_default_branch_is_preserved(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "switch", "-q", "-c", "release/main")
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = self.assess_with_default_branch(repo, "release/main")

        self.assertEqual(report["default_branch"], "release/main")
        self.assertEqual(report["recommended_action"], "feature_branch_required")
        self.assertFalse(report["safe_to_push"])

    def test_feature_branch_changes_can_reach_commit_then_push(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "switch", "-q", "-c", "docs/change")
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = self.assess_with_default_branch(repo, "main")

        self.assertEqual(report["default_branch"], "main")
        self.assertEqual(report["recommended_action"], "commit_then_push")
        self.assertTrue(report["safe_to_push"])

    def test_unpublished_default_branch_commit_requires_manual_review(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): unpublished")

        report = self.assess_with_default_branch(repo, "main")

        self.assertEqual(report["recommended_action"], "manual_review")
        self.assertFalse(report["safe_to_push"])

    def test_unknown_default_branch_changes_require_manual_review(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "switch", "-q", "-c", "develop")
        self.run_git(repo, "branch", "-D", "main")
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = self.assess_with_default_branch(repo, None)

        self.assertIsNone(report["default_branch"])
        self.assertEqual(report["recommended_action"], "manual_review")
        self.assertFalse(report["safe_to_push"])

    def test_unknown_default_branch_commit_requires_manual_review(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "switch", "-q", "-c", "trunk")
        self.run_git(repo, "branch", "-D", "main")
        self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): unpublished")

        report = self.assess_with_default_branch(repo, None)

        self.assertIsNone(report["default_branch"])
        self.assertEqual(report["recommended_action"], "manual_review")
        self.assertFalse(report["safe_to_push"])


if __name__ == "__main__":
    unittest.main()
