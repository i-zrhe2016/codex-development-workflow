#!/usr/bin/env python3
"""Regression tests for scripts/install-all.sh target selection.

These exercise the CLI surface added for dual-host support: the default Codex
destination, the Claude destination, explicit --dest precedence, invalid or
missing --target values, and the update/skip behavior against a scratch root.

The installer never touches a real skills directory here; every case passes an
explicit --dest under a temporary directory.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install-all.sh"

EXPECTED_SKILLS = (
    "codex-development-workflow",
    "context-efficiency",
    "plan-to-ticket",
    "test-workflow",
    "repo-current-state",
    "repo-documentation",
    "data-document-redaction",
    "github-push-when-ready",
    "pr-review",
)


class InstallerTargetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="install-all-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def run_installer(self, *args: str, home: Path | None = None,
                      codex_home: Path | None = None) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        if home is not None:
            env["HOME"] = str(home)
        if codex_home is not None:
            env["CODEX_HOME"] = str(codex_home)
        else:
            env.pop("CODEX_HOME", None)
        return subprocess.run(
            ["bash", str(INSTALLER), *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=REPO_ROOT,
        )

    def installed_names(self, root: Path) -> list[str]:
        return sorted(
            p.parent.name
            for p in root.glob("*/SKILL.md")
        )

    def test_default_target_installs_into_codex_home(self) -> None:
        codex_home = self.tmp / "codex-home"
        home = self.tmp / "home"
        home.mkdir()
        result = self.run_installer(home=home, codex_home=codex_home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(codex_home / "skills"), result.stdout)
        self.assertIn("Restart Codex", result.stdout)
        self.assertEqual(self.installed_names(codex_home / "skills"), sorted(EXPECTED_SKILLS))

    def test_claude_target_installs_into_claude_skills(self) -> None:
        home = self.tmp / "home"
        home.mkdir()
        result = self.run_installer("--target", "claude", home=home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(home / ".claude" / "skills"), result.stdout)
        self.assertIn("Restart Claude Code", result.stdout)
        self.assertEqual(self.installed_names(home / ".claude" / "skills"), sorted(EXPECTED_SKILLS))

    def test_explicit_dest_overrides_target(self) -> None:
        home = self.tmp / "home"
        home.mkdir()
        explicit = self.tmp / "explicit"
        result = self.run_installer("--target", "claude", "--dest", str(explicit), home=home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(explicit), result.stdout)
        self.assertEqual(self.installed_names(explicit), sorted(EXPECTED_SKILLS))
        self.assertFalse((home / ".claude" / "skills").exists())

    def test_unknown_target_exits_without_creating_destination(self) -> None:
        home = self.tmp / "home"
        home.mkdir()
        result = self.run_installer("--target", "bogus", home=home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown target", result.stderr)
        self.assertFalse((home / ".claude" / "skills").exists())

    def test_missing_target_value_exits_with_error(self) -> None:
        result = self.run_installer("--target")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--target requires a name", result.stderr)

    def test_rerun_skips_then_update_replaces(self) -> None:
        dest = self.tmp / "dest"
        first = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("Installed: 9", first.stdout)

        second = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Skipped:   9", second.stdout)

        third = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(third.returncode, 0, third.stderr)
        self.assertIn("Installed: 9", third.stdout)

    def test_update_preserves_unmanaged_destination(self) -> None:
        dest = self.tmp / "dest"
        unmanaged = dest / "pr-review"
        unmanaged.mkdir(parents=True)
        (unmanaged / "SKILL.md").write_text("local work\n", encoding="utf-8")

        result = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ownership unverified", result.stdout)
        self.assertEqual((unmanaged / "SKILL.md").read_text(encoding="utf-8"), "local work\n")


if __name__ == "__main__":
    unittest.main()
