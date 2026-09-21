#!/usr/bin/env python3
"""Repository contract tests for the managed workflow and test-quality policy."""

from __future__ import annotations

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
        managed: set[str] = set()
        in_skills = False
        for line in installer.splitlines():
            stripped = line.strip()
            if stripped == "SKILLS=(":
                in_skills = True
                continue
            if in_skills and stripped == ")":
                break
            if in_skills and "|" in stripped:
                spec = stripped.strip('"')
                managed.add(spec.split("|", 1)[1])
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
        listed = {
            line.removeprefix("- `").removesuffix("`")
            for line in section.splitlines()
            if line.startswith("- `") and line.endswith("`")
        }
        self.assertEqual(listed, EXPECTED_SKILLS)

    def test_test_workflow_contains_quality_gate_contract(self) -> None:
        runtime = TEST_SKILL.read_text(encoding="utf-8").lower()
        required = (
            "acceptance-to-test matrix",
            "select mandatory test dimensions",
            "boundary and negative tests",
            "property, fuzz, and mutation rules",
            "flaky and isolation policy",
            "test quality gate",
            "coverage percentage is diagnostic evidence only",
            "a retry is diagnostic evidence, never a pass mechanism",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, runtime)

        self.assertNotIn(
            "after it passes, stop by default.",
            runtime,
            "A GREEN test level must not bypass mandatory risk dimensions.",
        )

    def test_test_workflow_docs_match_runtime_quality_model(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in TEST_DOCS).lower()
        for marker in (
            "acceptance-to-test matrix",
            "mandatory",
            "property",
            "mutation",
            "flaky",
            "test quality gate",
            "coverage",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, combined)

    def test_root_workflow_requires_quality_gate(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Test Quality Gate", root_skill)
        self.assertIn("retry cannot convert an unexplained flaky failure to PASS", root_skill)
        self.assertIn("Coverage is", root_skill)


if __name__ == "__main__":
    unittest.main()
