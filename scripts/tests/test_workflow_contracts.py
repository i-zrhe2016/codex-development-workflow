#!/usr/bin/env python3
"""Repository contracts for the zero-Skill architecture."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
README = REPO_ROOT / "README.md"
AGENTS = REPO_ROOT / "AGENTS.md"


class WorkflowContractTests(unittest.TestCase):
    def test_zero_runtime_skills(self) -> None:
        self.assertFalse((REPO_ROOT / "SKILL.md").exists())
        skills = REPO_ROOT / "skills"
        self.assertEqual(list(skills.rglob("SKILL.md")) if skills.exists() else [], [])
        self.assertFalse((REPO_ROOT / "agents" / "openai.yaml").exists())
        self.assertEqual(list(skills.rglob("agents/openai.yaml")) if skills.exists() else [], [])

    def test_agents_owns_non_native_contracts(self) -> None:
        text = AGENTS.read_text(encoding="utf-8")
        for marker in (
            "GitHub Issues are the sole authoritative development-task store",
            "<!-- codex-plan-id:",
            "<!-- codex-ticket-id:",
            "Documentation Impact:",
            "Repo Current State:",
            "scripts/redaction/scan_staged.py",
            "scripts/publication/assess_push_readiness.py",
            "Conventional Commits 1.0.0",
            "scripts/render-diagrams.sh",
        ):
            self.assertIn(marker, text)

    def test_deterministic_tools_are_outside_skills(self) -> None:
        required = (
            "scripts/redaction/scan_staged.py",
            "scripts/publication/assess_push_readiness.py",
            "scripts/publication/push_if_ready.py",
            "scripts/publication/publish_identity.py",
            "scripts/retire-skills.sh",
        )
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_documentation_references_are_outside_skills(self) -> None:
        for name in (
            "doc-file-standard.md",
            "document-types.md",
            "documentation-lifecycle.md",
            "document-templates.md",
        ):
            self.assertTrue((REPO_ROOT / "docs" / "reference" / name).is_file())

    def test_every_plantuml_source_has_same_basename_svg(self) -> None:
        for source in sorted((REPO_ROOT / "docs").rglob("*.puml")):
            rendered = source.with_suffix(".svg")
            with self.subTest(source=source.relative_to(REPO_ROOT)):
                self.assertTrue(rendered.is_file())
                self.assertIn("<svg", rendered.read_text(encoding="utf-8"))

    def test_every_plantuml_source_is_referenced(self) -> None:
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [README, AGENTS, *sorted((REPO_ROOT / "docs").rglob("*.md"))]
        )
        for source in sorted((REPO_ROOT / "docs").rglob("*.puml")):
            with self.subTest(source=source.relative_to(REPO_ROOT)):
                self.assertIn(source.name, markdown)

    def test_drawio_overviews_are_valid_and_referenced(self) -> None:
        root = REPO_ROOT / "docs" / "diagrams" / "drawio"
        sources = sorted(root.glob("*.drawio"))
        markdown = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [README, AGENTS, *sorted((REPO_ROOT / "docs").rglob("*.md"))]
        )
        for source in sources:
            with self.subTest(source=source.name):
                tree = ET.parse(source)
                xml_root = tree.getroot()
                self.assertEqual(xml_root.get("compressed"), "false")
                cells = xml_root.findall(".//mxCell")
                ids = [cell.get("id") for cell in cells]
                self.assertEqual(len(ids), len(set(ids)))
                rendered = source.with_suffix(".svg")
                self.assertTrue(rendered.is_file())
                self.assertIn("<svg", rendered.read_text(encoding="utf-8"))
                self.assertIn(source.name, markdown)


if __name__ == "__main__":
    unittest.main()
