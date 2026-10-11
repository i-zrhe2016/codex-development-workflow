#!/usr/bin/env python3
"""Regression tests for the documentation-skill installer."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install-all.sh"
EXPECTED_SKILLS = ("data-document-redaction", "plantuml", "repo-current-state", "repo-documentation")
RETIRED = ("context-efficiency", "pr-review", "ponytail", "ponytail-review", "ponytail-audit",
           "ponytail-debt", "ponytail-gain", "ponytail-help", "auto-deploy",
           "codex-development-workflow", "plan-workflow", "develop-workflow", "verify-workflow",
           "publish-workflow", "integrate-workflow", "plan-to-ticket", "test-workflow",
           "skill-eval", "github-push-when-ready")
MARKER = ".codex-development-workflow-managed"


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="install-doc-skills-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_installer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", str(INSTALLER), *args], cwd=REPO_ROOT,
                              capture_output=True, text=True, env=dict(os.environ))

    def names(self, root: Path) -> list[str]:
        return sorted(path.parent.name for path in root.glob("*/SKILL.md"))

    def test_fresh_install_has_only_four_standalone_skills(self) -> None:
        for target in ("codex", "claude"):
            dest = self.tmp / target
            result = self.run_installer("--target", target, "--dest", str(dest))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(self.names(dest), list(EXPECTED_SKILLS))
            for name in EXPECTED_SKILLS:
                bundle = dest / name
                self.assertTrue((bundle / "SKILL.md").is_file())
                if target == "codex":
                    self.assertTrue((bundle / "agents/openai.yaml").is_file())
                else:
                    self.assertFalse((bundle / "agents/openai.yaml").exists())
                source = REPO_ROOT / "skills" / name
                self.assertEqual((bundle / "SKILL.md").read_bytes(), (source / "SKILL.md").read_bytes())

    def test_update_replaces_owned_skills_and_removes_only_owned_retired_bundles(self) -> None:
        dest = self.tmp / "dest"
        first = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stderr)
        for name in EXPECTED_SKILLS:
            (dest / name / "SKILL.md").write_text("stale\n", encoding="utf-8")
        owned = dest / "plan-workflow"
        owned.mkdir()
        (owned / MARKER).write_text(f"codex-development-workflow:plan-workflow\n", encoding="utf-8")
        unowned = dest / "develop-workflow"
        unowned.mkdir()
        (unowned / "SKILL.md").write_text("local\n", encoding="utf-8")
        unrelated = dest / "my-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_text("local\n", encoding="utf-8")

        result = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("remove: plan-workflow (retired)", result.stdout)
        self.assertIn("preserve: develop-workflow (ownership unverified)", result.stdout)
        for name in EXPECTED_SKILLS:
            self.assertEqual((dest / name / "SKILL.md").read_bytes(),
                             (REPO_ROOT / "skills" / name / "SKILL.md").read_bytes())
        self.assertFalse(owned.exists())
        self.assertEqual((unowned / "SKILL.md").read_text(encoding="utf-8"), "local\n")
        self.assertEqual((unrelated / "SKILL.md").read_text(encoding="utf-8"), "local\n")

    def test_adopt_legacy_backs_up_unmarked_retired_bundle(self) -> None:
        dest = self.tmp / "dest"
        legacy = dest / "plan-workflow"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("legacy\n", encoding="utf-8")
        result = self.run_installer("--target", "claude", "--dest", str(dest), "--update", "--adopt-legacy")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Migrated:  1", result.stdout)
        backups = list(dest.glob(".codex-development-workflow-legacy.*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "plan-workflow/SKILL.md").read_text(encoding="utf-8"), "legacy\n")
        self.assertFalse((dest / "plan-workflow").exists())

    def test_skip_and_cli_errors(self) -> None:
        dest = self.tmp / "dest"
        first = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stderr)
        second = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Skipped:   4", second.stdout)
        self.assertEqual(self.run_installer("--target", "bogus").returncode, 2)
        self.assertEqual(self.run_installer("--adopt-legacy").returncode, 2)


if __name__ == "__main__":
    unittest.main()
