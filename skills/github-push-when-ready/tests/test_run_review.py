import importlib.util
from pathlib import Path
import subprocess
import tempfile
import json
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "run_review", Path(__file__).parents[1] / "scripts" / "run_review.py")
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def run_main(self, root, arguments, prior=None, stream_result=0):
        directory = root / "codex-review"
        directory.mkdir(exist_ok=True)
        if prior is not None:
            review.save(directory / "state.json", prior)
        def fake_git(*args):
            if args[0] == "status":
                return ""
            if "--absolute-git-dir" in args:
                return str(root)
            return "head" if args[-1] == "HEAD" else "base"
        with patch.object(review, "git", side_effect=fake_git), patch.object(
                review, "stream", return_value=stream_result) as runner, patch.object(
                review.sys, "argv", ["run_review", "--base", "main", *arguments]):
            result = review.main()
        return result, runner, json.loads((directory / "state.json").read_text())

    def test_completed_execution_is_pending_and_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, runner, state = self.run_main(root, [])
            self.assertEqual(code, 0)
            self.assertEqual(state["assessment"], "pending")
            self.assertEqual(state["status"], "completed")
            code, runner, _ = self.run_main(root, [])
            runner.assert_not_called()
            _, _, state = self.run_main(root, ["--record", "pass", "--note", "Verified conclusion"])
            self.assertEqual(state["assessment"], "pass")
            _, runner, state = self.run_main(root, ["--force-full"])
            runner.assert_called_once()
            self.assertEqual(state["scope"], "base")
            self.assertEqual(state["assessment"], "pending")

    def test_failed_execution_cannot_be_recorded_as_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, _, state = self.run_main(root, [], stream_result=1)
            self.assertEqual(code, 1)
            self.assertEqual(state["status"], "incomplete")
            with self.assertRaises(SystemExit):
                self.run_main(root, ["--record", "pass", "--note", "invalid"])

    def test_orphaned_child_prevents_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old", base="base", head="head", status="running", child_pid=1)
            with patch.object(review.os, "kill"):
                code, runner, _ = self.run_main(Path(temporary), [], prior)
            self.assertEqual(code, 2)
            runner.assert_not_called()

    def test_first_and_unassessed_reviews_are_full(self):
        self.assertEqual(review.choose_scope("base", "head", None, True), "base")
        self.assertEqual(review.choose_scope("base", "head", {
            "base": "base", "head": "old", "assessment": "pending"}, True), "base")

    def test_incremental_covers_previous_assessed_head(self):
        prior = dict(base="base", head="old", assessment="blocking")
        with patch.object(review.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
            self.assertEqual(review.choose_scope("base", "head", prior, True), "old")
            self.assertEqual(review.choose_scope("base", "head", prior, False), "base")
            self.assertEqual(review.choose_scope("new-base", "head", prior, True), "new-base")

    def test_rewritten_history_requires_full_review(self):
        with patch.object(review.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            self.assertEqual(review.choose_scope("base", "head", {
                "base": "base", "head": "old", "assessment": "pass"}, True), "base")

    def test_output_is_saved_and_failure_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code = review.stream(["sh", "-c", "printf review-evidence; exit 7"],
                                 root / "review.log", {}, root / "state.json")
            self.assertEqual(code, 7)
            self.assertEqual((root / "review.log").read_text(), "review-evidence")


if __name__ == "__main__":
    unittest.main()
