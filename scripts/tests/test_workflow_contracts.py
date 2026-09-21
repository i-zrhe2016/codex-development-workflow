#!/usr/bin/env python3
"""Repository contract tests for the managed workflow and test-quality policy."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install-all.sh"
README = REPO_ROOT / "README.md"
ROOT_SKILL = REPO_ROOT / "SKILL.md"
TEST_SKILL = REPO_ROOT / "skills" / "test-workflow" / "SKILL.md"
TEST_DOCS = (
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "README.md",
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "architecture.md",
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "usage.md",
)

EXPECTED_SKILLS = {
    "codex-development-workflow",
    "context-efficiency",
    "plan-to-ticket",
    "test-workflow",
    "repo-current-state",
    "repo-documentation",
    "data-document-redaction",
    "github-push-when-ready",
}


class WorkflowContractTests(unittest.TestCase):
    def test_installer_managed_skills_match_repository_sources(self) -> None:
        installer = INSTALLER.read_text(encoding="utf-8")
        managed = set(re.findall(r'^\s*"[^|]+\|([^"]+)"\s*$', installer, re.MULTILINE))
        self.assertEqual(managed, EXPECTED_SKILLS)

        sources = {"codex-development-workflow"}
        sources.update(
            p.name
            for p in (REPO_ROOT / "skills").iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file()
        )
        self.assertEqual(sources, EXPECTED_SKILLS)

    def test_every_managed_skill_has_required_codex_metadata(self) -> None:
        roots = [REPO_ROOT]
        roots.extend(
            REPO_ROOT / "skills" / name
            for name in sorted(EXPECTED_SKILLS - {"codex-development-workflow"})
        )
        for root in roots:
            with self.subTest(skill=root.name):
                self.assertTrue((root / "SKILL.md").is_file())
                self.assertTrue((root / "agents" / "openai.yaml").is_file())

    def test_readme_installed_skill_list_matches_installer(self) -> None:
        readme = README.read_text(encoding="utf-8")
        section = readme.split("## Installed skills", 1)[1].split("## Skill documentation", 1)[0]
        listed = set(re.findall(r"^- `([^`]+)`$", section, re.MULTILINE))
        self.assertEqual(listed, EXPECTED_SKILLS)

    def test_test_workflow_contains_quality_gate_contract(self) -> None:
        runtime = TEST_SKILL.read_text(encoding="utf-8")
        required = (
            "Acceptance-to-test matrix",
            "Select mandatory test dimensions",
            "Boundary and negative tests",
            "Property, fuzz, and mutation rules",
            "Flaky and isolation policy",
            "Test Quality Gate",
            "Coverage percentage is diagnostic evidence only",
            "A retry is diagnostic evidence, never a PASS mechanism",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), runtime.lower())

        self.assertNotIn(
            "After it passes, stop by default.",
            runtime,
            "A GREEN test level must not bypass mandatory risk dimensions.",
        )

    def test_test_workflow_docs_match_runtime_quality_model(self) -> None:
        combined = "\\n".join(path.read_text(encoding="utf-8") for path in TEST_DOCS)
        for marker in (
            "Acceptance-to-Test Matrix",
            "mandatory",
            "Property",
            "Mutation",
            "flaky",
            "Test Quality Gate",
            "Coverage",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), combined.lower())

    def test_root_workflow_requires_quality_gate(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Test Quality Gate", root_skill)
        self.assertIn("retry cannot convert an unexplained flaky failure to PASS", root_skill)
        self.assertIn("Coverage is", root_skill)


if __name__ == "__main__":
    unittest.main()
, installer, re.MULTILINE))
        self.assertEqual(managed, EXPECTED_SKILLS)

        sources = {"codex-development-workflow"}
        sources.update(
            p.name
            for p in (REPO_ROOT / "skills").iterdir()
            if p.is_dir() and (p / "SKILL.md").is_file()
        )
        self.assertEqual(sources, EXPECTED_SKILLS)

    def test_every_managed_skill_has_required_codex_metadata(self) -> None:
        roots = [REPO_ROOT]
        roots.extend(
            REPO_ROOT / "skills" / name
            for name in sorted(EXPECTED_SKILLS - {"codex-development-workflow"})
        )
        for root in roots:
            with self.subTest(skill=root.name):
                self.assertTrue((root / "SKILL.md").is_file())
                self.assertTrue((root / "agents" / "openai.yaml").is_file())

    def test_readme_installed_skill_list_matches_installer(self) -> None:
        readme = README.read_text(encoding="utf-8")
        section = readme.split("## Installed skills", 1)[1].split("## Skill documentation", 1)[0]
        listed = set(re.findall(r"^- `([^`]+)`$", section, re.MULTILINE))
        self.assertEqual(listed, EXPECTED_SKILLS)

    def test_test_workflow_contains_quality_gate_contract(self) -> None:
        runtime = TEST_SKILL.read_text(encoding="utf-8")
        required = (
            "Acceptance-to-test matrix",
            "Select mandatory test dimensions",
            "Boundary and negative tests",
            "Property, fuzz, and mutation rules",
            "Flaky and isolation policy",
            "Test Quality Gate",
            "Coverage percentage is diagnostic evidence only",
            "A retry is diagnostic evidence, never a PASS mechanism",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, runtime)

        self.assertNotIn(
            "After it passes, stop by default.",
            runtime,
            "A GREEN test level must not bypass mandatory risk dimensions.",
        )

    def test_test_workflow_docs_match_runtime_quality_model(self) -> None:
        combined = "\\n".join(path.read_text(encoding="utf-8") for path in TEST_DOCS)
        for marker in (
            "Acceptance-to-Test Matrix",
            "mandatory",
            "Property",
            "Mutation",
            "flaky",
            "Test Quality Gate",
            "Coverage",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker.lower(), combined.lower())

    def test_root_workflow_requires_quality_gate(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Test Quality Gate", root_skill)
        self.assertIn("retry cannot convert an unexplained flaky failure to PASS", root_skill)
        self.assertIn("Coverage is", root_skill)


if __name__ == "__main__":
    unittest.main()
