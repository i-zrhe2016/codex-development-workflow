#!/usr/bin/env python3
"""Repository contract tests for the managed workflow and test-quality policy."""

from __future__ import annotations

import re
import tomllib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install-all.sh"
README = REPO_ROOT / "README.md"
ROOT_SKILL = REPO_ROOT / "SKILL.md"
AGENTS = REPO_ROOT / "AGENTS.md"
CODEX_CONFIG = REPO_ROOT / ".codex" / "config.toml"
CODEX_AGENTS = REPO_ROOT / ".codex" / "agents"
VERIFY_SKILL = REPO_ROOT / "skills" / "verify-workflow" / "SKILL.md"
TEST_SKILL = REPO_ROOT / "skills" / "test-workflow" / "SKILL.md"
PLAN_TO_TICKET = REPO_ROOT / "skills" / "plan-to-ticket" / "SKILL.md"
SKILL_EVAL = REPO_ROOT / "skills" / "skill-eval" / "SKILL.md"
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
    "skill-eval",
    "plantuml",
    "repo-current-state",
    "repo-documentation",
    "data-document-redaction",
    "github-push-when-ready",
}


class WorkflowContractTests(unittest.TestCase):
    def test_worker_model_table_routes_roles_and_repair_escalation(self) -> None:
        skill = ROOT_SKILL.read_text(encoding="utf-8")
        section = skill.split("## Codex worker model routing", 1)[1].split("\n## ", 1)[0]
        rows = [
            [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            for line in section.splitlines()
            if line.lstrip().startswith("|")
        ]
        routing = {scope: (model, effort) for scope, model, effort in rows[2:]}
        self.assertEqual(
            routing,
            {
                "Ordinary development, docs or synchronization": ("gpt-6-luna", "medium"),
                "API/schema, security or complex logic": ("gpt-6-luna", "high"),
                "Repair implementation after two consecutive failed repair rounds on the same problem": (
                    "gpt-6.1-sol",
                    "high",
                ),
                "Ticket acceptance verification or final Plan/branch/PR acceptance": (
                    "gpt-6.1-sol",
                    "high",
                ),
            },
        )

    def test_codex_defaults_and_named_roles_do_not_override_routing(self) -> None:
        config = tomllib.loads(CODEX_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["agents"]["default_subagent_model"], "gpt-6-luna")
        self.assertEqual(config["agents"]["default_subagent_reasoning_effort"], "medium")
        self.assertNotIn("max_concurrent_threads_per_session", config["agents"])

        repair = tomllib.loads((CODEX_AGENTS / "sol-repair.toml").read_text(encoding="utf-8"))
        self.assertEqual((repair["model"], repair["model_reasoning_effort"]), ("gpt-6.1-sol", "high"))
        self.assertIn("two consecutive failed repair rounds", repair["description"])
        verifier = tomllib.loads((CODEX_AGENTS / "sol-verifier.toml").read_text(encoding="utf-8"))
        self.assertEqual((verifier["model"], verifier["model_reasoning_effort"]), ("gpt-6.1-sol", "high"))
        self.assertEqual(repair["name"], "sol_repair")
        self.assertFalse((CODEX_AGENTS / "luna-escalation.toml").exists())

    def test_direct_dispatch_and_exact_single_ticket_verifier_coalescing(self) -> None:
        root = ROOT_SKILL.read_text(encoding="utf-8").lower()
        develop = (REPO_ROOT / "skills" / "develop-workflow" / "SKILL.md").read_text(encoding="utf-8").lower()
        verify = VERIFY_SKILL.read_text(encoding="utf-8").lower()
        for text in (root, develop, verify):
            normalized = re.sub(r"\s+", " ", text)
            self.assertIn("directly dispatch", normalized)
            self.assertIn("two available slots", normalized)
        self.assertIn("initial implementation failure does not count", root)
        self.assertIn("one-ticket plan", verify)
        for marker in ("full scope", "artifact/version", "configuration", "deployment surface"):
            with self.subTest(marker=marker):
                self.assertIn(marker, verify)
        self.assertIn("after two consecutive failed", root)
        self.assertNotIn("three available slots", root + develop + verify)
        self.assertNotIn("luna/xhigh", root + develop + verify)

    def test_agents_role_hierarchy_points_to_canonical_routing_policy(self) -> None:
        agents = AGENTS.read_text(encoding="utf-8")
        self.assertIn("[`SKILL.md`](SKILL.md#codex-worker-model-routing)", agents)
        self.assertNotIn("one fresh implementation agent, which executes **all**", agents)

    def test_plan_to_ticket_ticket_contract_has_behavioral_acceptance(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        template = re.search(
            r"Each Ticket uses these fields.*?```text\n(.*?)\n```",
            skill,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(template, "Expected the canonical Ticket contract.")
        required_fields = (
            "Ticket Goal:",
            "Ticket Scope:",
            "Ticket Out of scope:",
            "Dependencies:",
            "Function Checklist:",
            "Ticket Acceptance Criteria:",
            "Test Cases:",
            "Relevant Context / Files:",
            "Test Strategy:",
            "Test Level:",
            "Validation Command:",
        )
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, template.group(1))

    def test_requirement_sizing_and_supplement_scenarios(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        sizing = skill.split("## Scope and sizing", 1)[1].split("## Updating scope", 1)[0]
        updates = skill.split("## Updating scope", 1)[1].split("## Persistence and delivery contract", 1)[0]
        sizing = re.sub(r"\s+", " ", sizing).lower()
        updates = re.sub(r"\s+", " ", updates).lower()

        scenarios = {
            "ordinary requirement has one Ticket": (
                sizing,
                r"one ticket for an ordinary requirement",
            ),
            "additional Tickets require distinct behavior boundaries": (
                sizing,
                r"multiple tickets.*?only when they represent distinct behaviors, real dependencies, or acceptance boundaries",
            ),
            "same-requirement supplement updates the existing Ticket": (
                sizing + " " + updates,
                r"supplementary work for the same requirement updates its existing ticket",
            ),
            "new Ticket is conditional on a distinct boundary": (
                sizing + " " + updates,
                r"add a ticket only if the new work creates a distinct behavioral, dependency, or acceptance boundary",
            ),
        }
        for label, (contract, pattern) in scenarios.items():
            with self.subTest(scenario=label):
                self.assertRegex(contract, pattern)

    def test_every_requirement_is_persisted_before_branch_work(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        persistence = skill.split("## Persistence and delivery contract", 1)[1].split("### Naming and idempotency", 1)[0]
        persistence = re.sub(r"\s+", " ", persistence).lower()

        self.assertRegex(
            persistence,
            r"persist one plan issue and its child ticket issue or issues for every user requirement before creating a branch or editing repository files",
        )
        self.assertIn("github issues are authoritative", persistence)
        self.assertIn("do not create local markdown", persistence)

    def test_independent_requirement_uses_new_plan_before_prior_merge(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        sizing = skill.split("## Scope and sizing", 1)[1].split("## Updating scope", 1)[0]
        updates = skill.split("## Updating scope", 1)[1].split("## Persistence and delivery contract", 1)[0]
        contract = re.sub(r"\s+", " ", sizing + " " + updates).lower()

        self.assertRegex(
            contract,
            r"new independent requirements always start new plans, even if another plan is unmerged",
        )
        self.assertRegex(
            contract,
            r"an independent requirement always receives a new plan, including before the previous plan merges",
        )

    def test_publication_requires_valid_plan_and_ticket_metadata(self) -> None:
        publish = (REPO_ROOT / "skills" / "publish-workflow" / "SKILL.md").read_text(encoding="utf-8")
        push = (REPO_ROOT / "skills" / "github-push-when-ready" / "SKILL.md").read_text(encoding="utf-8")
        guide = (REPO_ROOT / "docs" / "skills" / "github-push-when-ready" / "README.md").read_text(encoding="utf-8")
        publish = re.sub(r"\s+", " ", publish).lower()
        push = re.sub(r"\s+", " ", push).lower()
        guide = re.sub(r"\s+", " ", guide).lower()

        self.assertRegex(
            publish,
            r"require the persisted plan and its required ticket issue metadata, and validate that they match the publication scope; missing or invalid metadata blocks commit, push, and pr creation/update",
        )
        self.assertRegex(
            push,
            r"before any commit, push, or pr creation/update, require the persisted plan and its required ticket issue metadata and validate that they match the publication scope\. missing or invalid plan/ticket metadata blocks publication",
        )
        self.assertRegex(
            guide,
            r"require valid plan and ticket issue metadata that matches the publication scope; missing or invalid metadata blocks publication",
        )
        self.assertNotRegex(
            publish + " " + push,
            r"(?:commit|push|pr creation/update) (?:may|can) proceed without (?:the )?plan",
        )
        self.assertNotIn("when it does not, publication proceeds normally", guide)

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

    def test_skill_eval_contract_requires_blind_ab_and_outcome_proof(self) -> None:
        runtime = SKILL_EVAL.read_text(encoding="utf-8").lower()
        normalized = re.sub(r"\s+", " ", runtime)

        for marker in (
            "static",
            "trigger",
            "behavior",
            "outcome",
            "outcome is decisive",
            "positive and negative prompt sets",
            "recall and precision",
            "observable traces and artifacts",
            "agent claims are not evidence",
            "same repository state, tools, permissions, task context",
            "candidate model fixed",
            "baseline runs without the new skill",
            "treatment runs with the skill",
            "do not tell candidates they are being evaluated",
            "judge-only rubric",
            "anonymize and randomize outputs",
            "code changes build, tests run",
            "ui changes are opened and operated",
            "cli changes are executed",
            "documentation changes are judged by the final document",
            "workflow skills are checked through traces, files, artifacts",
            "skill eval",
            "verdict: pass | fail | inconclusive",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, normalized)

    def test_root_workflow_requires_quality_gate(self) -> None:
        root_skill = ROOT_SKILL.read_text(encoding="utf-8")
        self.assertIn("Test Quality Gate", root_skill)
        self.assertIn("retry cannot convert an unexplained flaky failure to PASS", root_skill)
        self.assertIn("Coverage is", root_skill)

    def test_final_acceptance_uses_one_fresh_verifier(self) -> None:
        verify_skill = VERIFY_SKILL.read_text(encoding="utf-8").lower()
        verify_normalized = re.sub(r"\s+", " ", verify_skill)
        self.assertIn("final plan/branch/pr acceptance", verify_normalized)
        self.assertIn("one fresh independent", verify_normalized)
        self.assertIn("one new verifier may satisfy both ticket and final gates", verify_normalized)

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
            "workflow-overview", "components-overview", "plan-ticket",
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
