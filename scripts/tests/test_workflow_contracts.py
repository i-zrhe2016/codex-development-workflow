#!/usr/bin/env python3
"""Repository scope, package, link, and diagram integrity checks."""
from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
EXPECTED = {"repo-documentation", "repo-current-state", "plantuml", "data-document-redaction"}
RETIRED = {"context-efficiency", "pr-review", "ponytail", "ponytail-review", "ponytail-audit",
           "ponytail-debt", "ponytail-gain", "ponytail-help", "auto-deploy",
           "codex-development-workflow", "plan-workflow", "develop-workflow", "verify-workflow",
           "publish-workflow", "integrate-workflow", "plan-to-ticket", "test-workflow",
           "skill-eval", "github-push-when-ready"}


class RepositoryIntegrityTests(unittest.TestCase):
    def test_only_documentation_skills_are_bundled(self) -> None:
        bundles = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(bundles, EXPECTED)
        installer = (ROOT / "scripts/install-all.sh").read_text(encoding="utf-8-sig")
        readme = README.read_text(encoding="utf-8-sig")
        for name in EXPECTED:
            self.assertIn(f"skills/{name}|{name}", installer)
            self.assertIn(f"`{name}`", readme)
        self.assertFalse((ROOT / "SKILL.md").exists())
        self.assertFalse(RETIRED & bundles)

    def test_retired_cleanup_is_explicit_and_ownership_checked(self) -> None:
        installer = (ROOT / "scripts/install-all.sh").read_text(encoding="utf-8-sig")
        self.assertIn('if [ "$UPDATE" -eq 1 ]; then', installer)
        self.assertIn('destination_is_managed "$dest" "$name"', installer)
        self.assertIn('backup_legacy_destination "$dest" "$name"', installer)
        for name in RETIRED:
            self.assertIn(f'"{name}"', installer)

    def test_retained_skills_do_not_require_retired_workflow_skills(self) -> None:
        retired_refs = ("plan-workflow", "develop-workflow", "verify-workflow", "publish-workflow",
                        "integrate-workflow", "plan-to-ticket", "test-workflow", "skill-eval",
                        "github-push-when-ready", "codex-development-workflow")
        for path in sorted((ROOT / "skills").rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".yaml", ".py"}:
                continue
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for name in retired_refs:
                with self.subTest(path=path.relative_to(ROOT), reference=name):
                    self.assertNotIn(name, text)

    def test_all_markdown_links_resolve_and_docs_are_reachable(self) -> None:
        visited: set[Path] = set()
        pending = [README]
        while pending:
            doc = pending.pop().resolve()
            if doc in visited:
                continue
            visited.add(doc)
            for target in self.local_links(doc):
                self.assertTrue(target.exists(), f"Broken link in {doc.relative_to(ROOT)}: {target}")
                if target.is_dir():
                    target = target / "README.md"
                if target.is_file() and target.suffix == ".md":
                    pending.append(target)
        docs = {p.resolve() for p in (ROOT / "docs").rglob("*.md")}
        self.assertEqual(docs - visited, set())

    def test_retained_plantuml_pairs_are_linked_and_valid_svg(self) -> None:
        sources = sorted((ROOT / "docs").rglob("*.puml"))
        self.assertTrue(sources)
        links = {link.resolve() for doc in [README, *(ROOT / "docs").rglob("*.md")]
                 for link in self.local_links(doc)}
        for source in sources:
            svg = source.with_suffix(".svg")
            self.assertTrue(svg.is_file())
            self.assertEqual(ET.parse(svg).getroot().tag, "{http://www.w3.org/2000/svg}svg")
            self.assertIn(source.resolve(), links)
            self.assertIn(svg.resolve(), links)
            content = source.read_text(encoding="utf-8-sig")
            self.assertIn("@startuml", content)
            self.assertIn("@enduml", content)

    @staticmethod
    def local_links(document: Path) -> set[Path]:
        text = document.read_text(encoding="utf-8-sig")
        text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)
        result = set()
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            parsed = urlsplit(link.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            result.add((document.parent / unquote(parsed.path)).resolve())
        return result


if __name__ == "__main__":
    unittest.main()
