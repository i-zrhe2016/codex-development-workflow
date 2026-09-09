#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import sys


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from git_push_utils import assess_repo  # noqa: E402


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

    def test_default_branch_changes_require_feature_branch(self) -> None:
        repo = self.make_repo()
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = assess_repo(repo)

        self.assertEqual(report["default_branch"], "main")
        self.assertEqual(report["recommended_action"], "feature_branch_required")
        self.assertFalse(report["safe_to_push"])

    def test_feature_branch_changes_can_reach_commit_then_push(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "switch", "-q", "-c", "docs/change")
        (repo / "change.md").write_text("pending change\n", encoding="utf-8")

        report = assess_repo(repo)

        self.assertEqual(report["default_branch"], "main")
        self.assertEqual(report["recommended_action"], "commit_then_push")
        self.assertTrue(report["safe_to_push"])

    def test_unpublished_default_branch_commit_requires_manual_review(self) -> None:
        repo = self.make_repo()
        self.run_git(repo, "commit", "--allow-empty", "-m", "docs(test): unpublished")

        report = assess_repo(repo)

        self.assertEqual(report["recommended_action"], "manual_review")
        self.assertFalse(report["safe_to_push"])


if __name__ == "__main__":
    unittest.main()
