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

    def openai_metadata(self, root: Path) -> list[Path]:
        return sorted(root.rglob("openai.yaml"))

    def test_claude_target_omits_codex_metadata_from_every_bundle(self) -> None:
        """agents/openai.yaml is Codex-only; the Claude archive must not ship it.

        This covers both archive branches: the root package copies an explicit
        file list that includes `agents/`, and each specialist bundle copies `.`
        wholesale.
        """
        dest = self.tmp / "dest"
        result = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.openai_metadata(dest), [])

        # The root package still ships its other managed paths.
        root_bundle = dest / "codex-development-workflow"
        self.assertTrue((root_bundle / "SKILL.md").is_file())
        self.assertTrue((root_bundle / "agents").is_dir())
        self.assertTrue((root_bundle / "docs" / "workflow" / "redaction.md").is_file())
        self.assertTrue((root_bundle / "references" / "skill-map.md").is_file())

    def test_codex_target_installs_codex_metadata_for_every_bundle(self) -> None:
        codex_home = self.tmp / "codex-home"
        home = self.tmp / "home"
        home.mkdir()
        result = self.run_installer(home=home, codex_home=codex_home)
        self.assertEqual(result.returncode, 0, result.stderr)
        found = self.openai_metadata(codex_home / "skills")
        self.assertEqual(len(found), len(EXPECTED_SKILLS))
        self.assertEqual(
            sorted(p.parent.parent.name for p in found),
            sorted(EXPECTED_SKILLS),
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
        self.assertIn(f"Installed: {len(EXPECTED_SKILLS)}", first.stdout)

        second = self.run_installer("--target", "claude", "--dest", str(dest))
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(f"Skipped:   {len(EXPECTED_SKILLS)}", second.stdout)

        third = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(third.returncode, 0, third.stderr)
        self.assertIn(f"Installed: {len(EXPECTED_SKILLS)}", third.stdout)

    def test_update_leaves_unrelated_destination_untouched(self) -> None:
        dest = self.tmp / "dest"
        unrelated = dest / "local-custom-skill"
        unrelated.mkdir(parents=True)
        (unrelated / "SKILL.md").write_text("local work\n", encoding="utf-8")

        result = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("local-custom-skill", result.stdout)
        self.assertEqual((unrelated / "SKILL.md").read_text(encoding="utf-8"), "local work\n")

    def test_update_preserves_unverified_managed_destination(self) -> None:
        dest = self.tmp / "dest"
        unverified = dest / "test-workflow"
        unverified.mkdir(parents=True)
        (unverified / "SKILL.md").write_text("local work\n", encoding="utf-8")

        result = self.run_installer("--target", "claude", "--dest", str(dest), "--update")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preserve: test-workflow (ownership unverified)", result.stdout)
        self.assertEqual((unverified / "SKILL.md").read_text(encoding="utf-8"), "local work\n")


if __name__ == "__main__":
    unittest.main()
