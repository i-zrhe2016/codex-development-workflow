#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RETIRE = REPO_ROOT / "scripts" / "retire-skills.sh"


class ZeroSkillTests(unittest.TestCase):
    def test_repository_has_no_runtime_skill_entrypoints(self) -> None:
        self.assertFalse((REPO_ROOT / "SKILL.md").exists())
        skills = REPO_ROOT / "skills"
        self.assertEqual(list(skills.rglob("SKILL.md")) if skills.exists() else [], [])
        self.assertFalse((REPO_ROOT / "agents" / "openai.yaml").exists())
        self.assertEqual(list(skills.rglob("agents/openai.yaml")) if skills.exists() else [], [])

    def test_agents_is_runtime_policy_surface(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        for marker in (
            "zero runtime Skills",
            "GitHub Issues are the sole authoritative development-task store",
            "Documentation Impact:",
            "Repo Current State:",
            "scripts/redaction/scan_staged.py",
            "scripts/publication/assess_push_readiness.py",
        ):
            self.assertIn(marker, agents)

    def test_retire_removes_only_managed_skill(self) -> None:
        with tempfile.TemporaryDirectory(prefix="retire-skills-") as temp:
            dest = Path(temp)
            managed = dest / "github-publish"
            managed.mkdir()
            (managed / ".codex-development-workflow-managed").write_text(
                "codex-development-workflow:github-publish\n", encoding="utf-8"
            )
            unmanaged = dest / "repo-current-state"
            unmanaged.mkdir()
            (unmanaged / "SKILL.md").write_text("local\n", encoding="utf-8")
            unrelated = dest / "local-skill"
            unrelated.mkdir()
            (unrelated / "SKILL.md").write_text("local\n", encoding="utf-8")

            result = subprocess.run(
                ["bash", str(RETIRE), "--dest", str(dest)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(managed.exists())
            self.assertTrue(unmanaged.exists())
            self.assertTrue(unrelated.exists())
            self.assertIn("remove: github-publish", result.stdout)
            self.assertIn("preserve: repo-current-state (ownership unverified)", result.stdout)


if __name__ == "__main__":
    unittest.main()
