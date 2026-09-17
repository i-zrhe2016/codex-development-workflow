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
    def run_main(self, root, arguments, prior=None, stream_result=0,
                 ancestor=True, branch="branch"):
        directory = root / "ocr-review"
        directory.mkdir(exist_ok=True)
        if prior is not None:
            review.save(directory / "state.json", prior)
        def fake_git(*args):
            if args[0] == "status":
                return ""
            if args[:2] == ("branch", "--show-current"):
                return branch
            if "--absolute-git-dir" in args:
                return str(root)
            return "head" if args[-1] == "HEAD" else "base"
        def fake_try_git(*args):
            # Keep the helper hermetic: equal local/remote refs skip the
            # stale-base guard without touching the ambient repository.
            return "base"
        with patch.object(review, "git", side_effect=fake_git), patch.object(
                review, "try_git", side_effect=fake_try_git), patch.object(
                review.subprocess, "run", return_value=subprocess.CompletedProcess(
                    [], 0 if ancestor else 1)) as merge_base, patch.object(
                review, "stream", return_value=stream_result) as runner, patch.object(
                review.sys, "argv", ["run_review", "--base", "main", *arguments]):
            result = review.main()
        return result, runner, json.loads((directory / "state.json").read_text()), merge_base

    def test_completed_execution_is_pending_and_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, runner, state, _ = self.run_main(root, [])
            self.assertEqual(code, 0)
            self.assertEqual(state["assessment"], "pending")
            self.assertEqual(state["status"], "completed")
            code, runner, _, _ = self.run_main(root, [])
            runner.assert_not_called()
            _, _, state, _ = self.run_main(root, ["--record", "pass", "--note", "Verified conclusion"])
            self.assertEqual(state["assessment"], "pass")
            _, runner, state, _ = self.run_main(root, ["--force-full"])
            runner.assert_called_once()
            self.assertEqual(state["scope"], "base")
            self.assertEqual(state["coverage"], "full")
            self.assertEqual(state["assessment"], "pending")

    def test_failed_execution_cannot_be_recorded_as_pass(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code, _, state, _ = self.run_main(root, [], stream_result=1)
            self.assertEqual(code, 1)
            self.assertEqual(state["status"], "incomplete")
            with self.assertRaises(SystemExit):
                self.run_main(root, ["--record", "pass", "--note", "invalid"])

    def test_orphaned_child_prevents_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old", base="base", head="head", status="running", child_pid=1)
            with patch.object(review.os, "kill"):
                code, runner, _, _ = self.run_main(Path(temporary), [], prior)
            self.assertEqual(code, 2)
            runner.assert_not_called()

    def test_first_and_unassessed_reviews_are_full(self):
        self.assertEqual(review.choose_scope("base", "head", None, True,
                                            "branch"), "base")
        self.assertEqual(review.choose_scope("base", "head", {
            "base": "base", "head": "old", "assessment": "pending"},
            True, "branch"), "base")

    def test_incremental_covers_previous_assessed_head(self):
        prior = dict(base="base", head="old", status="completed",
                     assessment="blocking", branch="branch")
        with patch.object(review.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)):
            self.assertEqual(review.choose_scope("base", "head", prior, True,
                                                "branch"), "old")
            self.assertEqual(review.choose_scope("base", "head", prior, False,
                                                "branch"), "base")
            self.assertEqual(review.choose_scope("new-base", "head", prior, True,
                                                "branch"), "new-base")

    def test_assessed_review_defaults_to_incremental_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old-run", base="base", head="old",
                         status="completed", assessment="pass", branch="branch")
            code, runner, state, merge_base = self.run_main(
                Path(temporary), [], prior=prior)
            self.assertEqual(code, 0)
            self.assertEqual(state["scope"], "old")
            self.assertEqual(state["coverage"], "incremental")
            self.assertEqual(state["previous_run"], "old-run")
            self.assertEqual(state["branch"], "branch")
            self.assertEqual(runner.call_args.args[0],
                             ["ocr", "review", "--from", "old", "--to", "head"])
            merge_base.assert_called_once()

    def test_unassessed_or_incomplete_review_defaults_to_full_scope(self):
        for status, assessment in (("completed", "pending"),
                                   ("incomplete", "blocking")):
            with self.subTest(status=status, assessment=assessment), \
                    tempfile.TemporaryDirectory() as temporary:
                prior = dict(run_id="old-run", base="base", head="old",
                             status=status, assessment=assessment, branch="branch")
                _, runner, state, merge_base = self.run_main(
                    Path(temporary), [], prior=prior)
                self.assertEqual(state["scope"], "base")
                self.assertEqual(state["coverage"], "full")
                self.assertIsNone(state["previous_run"])
                self.assertEqual(runner.call_args.args[0],
                                 ["ocr", "review", "--from", "base", "--to", "head"])
                merge_base.assert_not_called()

    def test_force_full_overrides_assessed_incremental_default(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old-run", base="base", head="old",
                         status="completed", assessment="blocking", branch="branch")
            _, runner, state, merge_base = self.run_main(
                Path(temporary), ["--force-full"], prior=prior)
            self.assertEqual(state["scope"], "base")
            self.assertEqual(state["coverage"], "full")
            self.assertIsNone(state["previous_run"])
            self.assertEqual(runner.call_args.args[0],
                             ["ocr", "review", "--from", "base", "--to", "head"])
            merge_base.assert_not_called()

    def test_other_branch_or_legacy_state_defaults_to_full_scope(self):
        for prior_branch in ("other-branch", None):
            with self.subTest(prior_branch=prior_branch), \
                    tempfile.TemporaryDirectory() as temporary:
                prior = dict(run_id="old-run", base="base", head="old",
                             status="completed", assessment="pass")
                if prior_branch is not None:
                    prior["branch"] = prior_branch
                _, runner, state, merge_base = self.run_main(
                    Path(temporary), [], prior=prior, branch="current-branch")
                self.assertEqual(state["scope"], "base")
                self.assertEqual(state["coverage"], "full")
                self.assertIsNone(state["previous_run"])
                self.assertEqual(runner.call_args.args[0],
                                 ["ocr", "review", "--from", "base", "--to", "head"])
                merge_base.assert_not_called()

    def test_completed_execution_from_other_branch_is_not_reused(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old-run", base="base", head="head",
                         status="completed", assessment="pass",
                         branch="other-branch")
            _, runner, state, _ = self.run_main(
                Path(temporary), [], prior=prior, branch="current-branch")
            runner.assert_called_once()
            self.assertEqual(state["scope"], "base")
            self.assertEqual(state["coverage"], "full")
            self.assertIsNone(state["previous_run"])

    def test_rewritten_history_requires_full_review(self):
        with patch.object(review.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)):
            self.assertEqual(review.choose_scope("base", "head", {
                "base": "base", "head": "old", "status": "completed",
                "assessment": "pass", "branch": "branch"}, True,
                "branch"), "base")

    def test_stale_local_base_reports_both_refs(self):
        def fake_try_git(*args):
            ref = args[-1]
            if ref == "refs/heads/main^{commit}":
                return "a" * 40
            if ref == "origin/main^{commit}":
                return "b" * 40
            return None
        with patch.object(review, "try_git", side_effect=fake_try_git):
            message = review.stale_base_error("main", "a" * 40)
        self.assertIsNotNone(message)
        self.assertIn("origin/main", message)

    def test_matching_and_non_local_bases_are_accepted(self):
        def fake_try_git(*args):
            ref = args[-1]
            if ref.startswith("refs/heads/"):
                return "a" * 40
            if ref.startswith("origin/"):
                return "a" * 40
            return None
        with patch.object(review, "try_git", side_effect=fake_try_git):
            self.assertIsNone(review.stale_base_error("main", "a" * 40))
            self.assertIsNone(review.stale_base_error("origin/main", "a" * 40))
            self.assertIsNone(review.stale_base_error("deadbeef", "a" * 40))

    def test_configured_upstream_remote_takes_precedence_over_origin(self):
        def fake_try_git(*args):
            if args[0] == "for-each-ref":
                return "refs/remotes/upstream/main"
            ref = args[-1]
            if ref == "refs/heads/main^{commit}":
                return "a" * 40
            if ref == "refs/remotes/upstream/main^{commit}":
                return "b" * 40
            if ref == "origin/main^{commit}":
                return "a" * 40
            return None
        with patch.object(review, "try_git", side_effect=fake_try_git):
            message = review.stale_base_error("main", "a" * 40)
        self.assertIsNotNone(message)
        self.assertIn("upstream/main", message)
        self.assertNotIn("origin/main", message)

    def test_upstream_match_is_accepted_even_when_origin_differs(self):
        def fake_try_git(*args):
            if args[0] == "for-each-ref":
                return "refs/remotes/upstream/main"
            ref = args[-1]
            if ref == "refs/heads/main^{commit}":
                return "a" * 40
            if ref == "refs/remotes/upstream/main^{commit}":
                return "a" * 40
            if ref == "origin/main^{commit}":
                return "b" * 40
            return None
        with patch.object(review, "try_git", side_effect=fake_try_git):
            self.assertIsNone(review.stale_base_error("main", "a" * 40))

    def test_resolved_base_that_is_not_the_branch_tip_is_accepted(self):
        # A same-named tag may win ref resolution, so only guard when the
        # resolved base really is the local branch tip.
        def fake_try_git(*args):
            ref = args[-1]
            if ref == "refs/heads/main^{commit}":
                return "a" * 40
            if ref == "origin/main^{commit}":
                return "b" * 40
            return None
        with patch.object(review, "try_git", side_effect=fake_try_git):
            self.assertIsNone(review.stale_base_error("main", "b" * 40))

    def test_record_is_not_blocked_by_a_stale_base(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prior = dict(run_id="old", base="base", head="head",
                         status="completed", assessment="pending", branch="branch")

            def fake_git(*args):
                if args[0] == "status":
                    return ""
                if args[:2] == ("branch", "--show-current"):
                    return "branch"
                if "--absolute-git-dir" in args:
                    return str(root)
                return "head" if args[-1] == "HEAD" else "base"

            def fake_try_git(*args):
                if args[0] == "for-each-ref":
                    return None
                ref = args[-1]
                if ref == "refs/heads/main^{commit}":
                    return "base"
                if ref == "origin/main^{commit}":
                    return "b" * 40
                return None

            directory = root / "ocr-review"
            directory.mkdir(exist_ok=True)
            review.save(directory / "state.json", prior)
            with patch.object(review, "git", side_effect=fake_git), \
                    patch.object(review, "try_git", side_effect=fake_try_git), \
                    patch.object(review, "stream") as runner, \
                    patch.object(review.sys, "argv",
                                 ["run_review", "--base", "main",
                                  "--record", "pass", "--note", "ok"]):
                self.assertEqual(review.main(), 0)
            runner.assert_not_called()
            self.assertEqual(json.loads((directory / "state.json").read_text())["assessment"], "pass")

    def test_record_requires_current_branch_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            prior = dict(run_id="old", base="base", head="head",
                         status="completed", assessment="pending", branch="other")
            with self.assertRaises(SystemExit):
                self.run_main(Path(temporary),
                              ["--record", "pass", "--note", "ok"],
                              prior=prior, branch="current")

    def test_stale_local_base_blocks_before_review_starts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "ocr-review"
            directory.mkdir(exist_ok=True)

            def fake_git(*args):
                if args[0] == "status":
                    return ""
                if "--absolute-git-dir" in args:
                    return str(root)
                return "head" if args[-1] == "HEAD" else "a" * 40

            def fake_try_git(*args):
                ref = args[-1]
                if ref == "refs/heads/main^{commit}":
                    return "a" * 40
                if ref == "origin/main^{commit}":
                    return "b" * 40
                return None

            with patch.object(review, "git", side_effect=fake_git), patch.object(
                    review, "try_git", side_effect=fake_try_git), patch.object(
                    review, "stream") as runner, patch.object(
                    review.sys, "argv", ["run_review", "--base", "main"]):
                with self.assertRaises(SystemExit):
                    review.main()
            runner.assert_not_called()
            self.assertFalse((directory / "state.json").exists())

    def test_output_is_saved_and_failure_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            code = review.stream(["sh", "-c", "printf review-evidence; exit 7"],
                                 root / "review.log", {}, root / "state.json")
            self.assertEqual(code, 7)
            self.assertEqual((root / "review.log").read_text(), "review-evidence")


if __name__ == "__main__":
    unittest.main()
