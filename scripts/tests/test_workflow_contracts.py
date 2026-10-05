#!/usr/bin/env python3
"""Repository contract tests for the managed workflow and test-quality policy."""

from __future__ import annotations

import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install-all.sh"
README = REPO_ROOT / "README.md"
ROOT_SKILL = REPO_ROOT / "SKILL.md"
VERIFY_SKILL = REPO_ROOT / "skills" / "verify-workflow" / "SKILL.md"
TEST_SKILL = REPO_ROOT / "skills" / "test-workflow" / "SKILL.md"
WORKFLOW_USAGE = REPO_ROOT / "docs" / "workflow" / "usage.md"
TEST_DOCS = (
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "README.md",
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "architecture.md",
    REPO_ROOT / "docs" / "skills" / "test-workflow" / "usage.md",
)

EXPECTED_SKILLS = {
    "codex-development-workflow",
    "plan-workflow",
    "develop-workflow",
    "verify-workflow",
    "publish-workflow",
    "integrate-workflow",
    "plan-to-ticket",
    "test-workflow",
    "plantuml",
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

    def test_verify_workflow_requires_same_surface_runtime_proof(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").lower()
            for path in (ROOT_SKILL, README, VERIFY_SKILL, WORKFLOW_USAGE)
        )
        normalized = re.sub(r"\s+", " ", combined)
        for marker in (
            "same-surface verification",
            "runtime identity/doctor",
            "launch -> doctor -> drive -> evidence -> cleanup",
            "reproducible evidence",
            "verification profile freshness",
            "intended artifact",
            "instance or surface cannot be proven",
            "docs/verification/",
            "not a new workflow skill",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_test_workflow_requires_authz_and_falsifiable_assertions(self) -> None:
        runtime = TEST_SKILL.read_text(encoding="utf-8").lower()
        combined_docs = "\n".join(path.read_text(encoding="utf-8").lower() for path in TEST_DOCS)

        for label, text in (("runtime", runtime), ("docs", combined_docs)):
            with self.subTest(document=label):
                for marker in (
                    "authn/authz",
                    "authentication",
                    "authorization",
                    "session lifecycle",
                    "cookie-token",
                    "tenant/object ownership",
                    "fail-closed",
                    "protected side-effect absence",
                    "falsifiable",
                    "mock-called",
                    "value-exists",
                    "no-exception",
                    "status-only",
                ):
                    self.assertIn(marker, text)

    def test_root_workflow_requires_quality_gate(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Test Quality Gate", root_skill)
        self.assertIn("retry cannot convert an unexplained flaky failure to PASS", root_skill)
        self.assertIn("Coverage is", root_skill)

    def test_final_acceptance_uses_one_fresh_verifier(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8").lower()
        verify_skill = VERIFY_SKILL.read_text(encoding="utf-8").lower()
        for text in (root_skill, verify_skill):
            normalized = re.sub(r"\s+", " ", text)
            with self.subTest():
                self.assertIn("ordinary per-ticket", normalized)
                self.assertIn("one verifier", normalized)
                self.assertIn("final plan/branch/pr acceptance", normalized)
                self.assertIn("one fresh independent verifier", normalized)
                self.assertIn("verifier", normalized)
                self.assertIn("it must pass", normalized)

    def test_final_acceptance_rejects_old_three_verifier_policy(self) -> None:
        scanned_suffixes = {".md", ".puml", ".py", ".svg", ".yaml", ".yml"}
        ignored_paths = {Path(__file__).resolve()}
        ignored_parts = {".git", ".pytest_cache", "__pycache__"}
        rejected_patterns = (
            r"three[- ]fresh(?:[- ]independent)?[- ]verifiers?",
            r"three[- ]independent[- ]verifiers?",
            r"three[- ]verifier",
            r"3[- ]fresh",
            r"3[- ]verifiers?",
            r"all[- ]three[- ]must",
            r"all[- ]3[- ](?:must|pass)",
        )

        for path in sorted(REPO_ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in scanned_suffixes:
                continue
            if path.resolve() in ignored_paths or ignored_parts.intersection(path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            normalized = re.sub(r"\s+", " ", text)
            for pattern in rejected_patterns:
                with self.subTest(path=path.relative_to(REPO_ROOT), pattern=pattern):
                    self.assertIsNone(re.search(pattern, normalized))

    def test_every_plantuml_source_has_same_basename_svg(self) -> None:
        sources = sorted((REPO_ROOT / "docs").rglob("*.puml"))
        self.assertTrue(sources, "Expected repository documentation diagrams.")
        for source in sources:
            with self.subTest(source=source.relative_to(REPO_ROOT)):
                rendered = source.with_suffix(".svg")
                self.assertTrue(rendered.is_file(), f"Missing render for {source}")
                self.assertEqual(ET.parse(rendered).getroot().tag, "{http://www.w3.org/2000/svg}svg")

    def test_plantuml_sources_follow_repository_contract(self) -> None:
        for source in sorted((REPO_ROOT / "docs").rglob("*.puml")):
            text = source.read_text(encoding="utf-8")
            with self.subTest(source=source.relative_to(REPO_ROOT)):
                self.assertIn("@startuml", text)
                self.assertIn("@enduml", text)
                self.assertIn("!theme plain", text)
                if source.name != "installer-decision-flow.puml":
                    self.assertNotIn("context-efficiency", text)
                self.assertNotIn("PR review loop", text)

    def test_every_plantuml_source_is_referenced_by_documentation(self) -> None:
        references = {
            target
            for document in [README, *sorted((REPO_ROOT / "docs").rglob("*.md"))]
            for target in self.local_link_targets(document)
        }
        for source in sorted((REPO_ROOT / "docs").rglob("*.puml")):
            with self.subTest(source=source.relative_to(REPO_ROOT)):
                self.assertIn(source.resolve(), references)
                self.assertIn(source.with_suffix(".svg").resolve(), references)

    @staticmethod
    def local_link_targets(document: Path) -> set[Path]:
        targets = set()
        markdown = document.read_text(encoding="utf-8")
        # Fenced examples are source text, not rendered documentation links.
        markdown = re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", markdown)
        for link in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", markdown):
            parsed = urlsplit(link.strip("<>"))
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            targets.add((document.parent / unquote(parsed.path)).resolve())
        return targets

    def test_every_diagram_svg_has_canonical_plantuml_source(self) -> None:
        renders = sorted(REPO_ROOT.rglob("*.svg"))
        self.assertTrue(renders, "Expected repository diagram renders.")
        for rendered in renders:
            with self.subTest(render=rendered.relative_to(REPO_ROOT)):
                self.assertTrue(rendered.with_suffix(".puml").is_file(), f"Missing source for {rendered}")

    def test_diagrams_have_no_legacy_sources_or_raster_copies(self) -> None:
        self.assertEqual(list(REPO_ROOT.rglob("*.drawio")), [])
        for directory in (REPO_ROOT / "docs").rglob("diagrams"):
            for image in directory.rglob("*"):
                with self.subTest(path=image.relative_to(REPO_ROOT)):
                    self.assertNotIn(image.suffix.lower(), {".png", ".jpg", ".jpeg", ".gif", ".webp"})

    def test_all_shared_overviews_are_present(self) -> None:
        expected = {
            "workflow-overview", "components-overview", "plan-ticket-slice",
            "test-quality-gate", "docs-publication-flow", "installer-overview",
        }
        sources = (REPO_ROOT / "docs" / "diagrams").glob("*.puml")
        self.assertEqual({source.stem for source in sources}, expected)

    def test_documentation_links_exist_and_all_docs_are_reachable(self) -> None:
        visited = set()
        pending = [README]
        while pending:
            document = pending.pop().resolve()
            if document in visited:
                continue
            visited.add(document)
            for target in self.local_link_targets(document):
                with self.subTest(document=document.relative_to(REPO_ROOT), target=target):
                    self.assertTrue(target.exists(), f"Broken link in {document}: {target}")
                if target.is_dir():
                    target = target / "README.md"
                if target.is_file() and target.suffix == ".md" and target not in visited:
                    pending.append(target)
        docs = {document.resolve() for document in (REPO_ROOT / "docs").rglob("*.md")}
        self.assertEqual(docs - visited, set(), "Documents must be reachable from root README.")


if __name__ == "__main__":
    unittest.main()
