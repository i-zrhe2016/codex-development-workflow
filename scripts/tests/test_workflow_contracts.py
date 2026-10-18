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
                "Ordinary development, docs or synchronization": ("gpt-6.1-sol", "low"),
                "API/schema, security or complex logic": ("gpt-6.1-sol", "low"),
                "Repair implementation from the first repair round": (
                    "gpt-6.1-sol",
                    "low",
                ),
                "Ticket acceptance verification or final Plan/branch/PR acceptance": (
                    "gpt-6.1-sol",
                    "high",
                ),
            },
        )

    def test_single_model_defaults_and_user_selected_escalation_contract(self) -> None:
        section = ROOT_SKILL.read_text(encoding="utf-8").split(
            "## Codex worker model routing", 1
        )[1].split("\n## ", 1)[0]
        normalized = re.sub(r"\s+", " ", section).lower()
        scenarios = {
            "uniform_defaults": ("one model across all stages", "effort varies by role"),
            "repair_count": ("initial implementation failure does not count", "two consecutive failed same-problem repair rounds", "count across replacement"),
            "missing_selection": ("durable plan/ticket checkpoint", "pauses the affected problem", "asks the user to choose an escalation model", "user has not selected a model, do not dispatch another same-problem repair or a new model"),
            "selected_model": ("dispatch that model only for the stated problem and role", "`low` for implementation/repair", "`high` for independent verification", "model selection does not reset history"),
            "unsupported_selection": ("user-selected model or required effort is unavailable", "unsupported setting", "stop that dispatch without fallback"),
            "conflicting_role": ("compatible named role or no named role", "never apply a sol-only role's conflicting override"),
            "unchanged_defaults": ("unrelated work retains its defaults", "do not hardcode an escalation model", "change the main runtime"),
        }
        for scenario, markers in scenarios.items():
            with self.subTest(scenario=scenario):
                for marker in markers:
                    self.assertIn(marker, normalized)
        self.assertNotIn("ensure they match the table", normalized)
        for path in (AGENTS, REPO_ROOT / "skills/develop-workflow/SKILL.md", VERIFY_SKILL, TEST_SKILL):
            with self.subTest(entrypoint=path):
                text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8")).lower()
                self.assertIn("choose an escalation model", text)
                self.assertIn("until selection", text)
                self.assertIn("no named role", text)
                self.assertIn("without fallback", text)

    def test_codex_defaults_and_named_roles_do_not_override_routing(self) -> None:
        config = tomllib.loads(CODEX_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual((config["model"], config["model_reasoning_effort"]), ("gpt-6.1-sol", "low"))
        self.assertEqual(config["agents"]["default_subagent_model"], "gpt-6.1-sol")
        self.assertEqual(config["agents"]["default_subagent_reasoning_effort"], "low")
        self.assertNotIn("max_concurrent_threads_per_session", config["agents"])

        repair = tomllib.loads((CODEX_AGENTS / "sol-repair.toml").read_text(encoding="utf-8"))
        self.assertEqual((repair["model"], repair["model_reasoning_effort"]), ("gpt-6.1-sol", "low"))
        self.assertIn("from the first repair round", repair["description"])
        self.assertIn("After two consecutive failed\nrepair rounds", repair["developer_instructions"])
        verifier = tomllib.loads((CODEX_AGENTS / "sol-verifier.toml").read_text(encoding="utf-8"))
        self.assertEqual((verifier["model"], verifier["model_reasoning_effort"]), ("gpt-6.1-sol", "high"))
        self.assertEqual(repair["name"], "sol_repair")
        self.assertFalse((CODEX_AGENTS / "luna-escalation.toml").exists())

    def test_effort_matrix_and_planning_exception(self) -> None:
        root = ROOT_SKILL.read_text(encoding="utf-8")
        mode = root.split("## Default single-agent execution\n", 1)[1].split("\n## ", 1)[0]
        rows = [
            [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            for line in mode.splitlines() if line.lstrip().startswith("|")
        ]
        self.assertEqual(dict(rows[2:]), {
            "Planning in either execution mode": "high",
            "Other single-agent work, including self-verification": "low",
            "Delegated development and repair": "low",
            "Delegated independent verification": "high",
        })
        normalized = re.sub(r"\s+", " ", mode).lower()
        self.assertIn("planning takes precedence over the single-agent default", normalized)
        self.assertIn("if it cannot be applied, report the actual limitation", normalized)
        self.assertIn("configuration changes do not alter a running turn", normalized)

        for name in (
            "plan-workflow", "develop-workflow", "verify-workflow",
            "publish-workflow", "integrate-workflow", "plan-to-ticket", "test-workflow",
        ):
            with self.subTest(entrypoint=name):
                source = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                execution = re.sub(r"\s+", " ", source.split("## Execution mode\n", 1)[1].split("\n## ", 1)[0]).lower()
                self.assertIn("default reasoning effort is `low`, including self-verification", execution)
                self.assertIn("planning uses `high` in either mode", execution)
                self.assertIn("delegated development/repair uses `low`", execution)
                self.assertIn("independent verification `high`", execution)
                self.assertIn("report unsupported effort settings", execution)
                self.assertNotIn("`medium`", execution)

        plan_prompt = (REPO_ROOT / "skills/plan-workflow/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("high reasoning effort", plan_prompt)
        develop_prompt = (REPO_ROOT / "skills/develop-workflow/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("development and repair workers use low reasoning effort", develop_prompt)
        verify_prompt = (REPO_ROOT / "skills/verify-workflow/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("default single-agent execution with low reasoning effort", verify_prompt)
        self.assertIn("independent verifiers with high reasoning effort", verify_prompt)

    def test_single_agent_default_and_authorized_delegation_contract(self) -> None:
        root = ROOT_SKILL.read_text(encoding="utf-8")
        default_mode = root.split("## Default single-agent execution\n", 1)[1].split("\n## ", 1)[0]
        normalized = re.sub(r"\s+", " ", default_mode).lower()
        for condition in (
            "main agent alone",
            "do not spawn subagents",
            "local repairs, ticket acceptance or final plan acceptance",
            "self-verification evidence",
            "never label that evidence independent",
            "stage transitions and an initial failure do not activate delegation",
            "two consecutive failed same-problem repair rounds",
            "model selection alone does not authorize subagents",
            "missing subagent support does not block",
            "worker-only rules below apply only in explicitly authorized delegated mode",
            "same acceptance criteria and quality gate in either mode",
        ):
            with self.subTest(condition=condition):
                self.assertIn(condition, normalized)

        # Each directly installed entrypoint must work without the repository's
        # AGENTS.md and must not silently activate its worker-only instructions.
        for name in (
            "plan-workflow", "develop-workflow", "verify-workflow",
            "publish-workflow", "integrate-workflow", "plan-to-ticket", "test-workflow",
        ):
            with self.subTest(entrypoint=name):
                source = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                mode = re.sub(r"\s+", " ", source.split("## Execution mode\n", 1)[1].split("\n## ", 1)[0]).lower()
                self.assertIn("default single-agent execution", mode)
                self.assertIn("do not spawn subagents", mode)
                self.assertIn("only in explicitly authorized delegated mode", mode)
                self.assertIn("model selection alone does not authorize subagents", mode)
                self.assertIn("missing subagent support does not block", mode)

        for name in ("develop-workflow", "verify-workflow"):
            with self.subTest(prompt=name):
                prompt = (REPO_ROOT / "skills" / name / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertIn("default single-agent execution", prompt)
                self.assertIn("without spawning subagents", prompt)
                self.assertRegex(prompt, r"explicit delegation authorization|explicitly authorized delegated mode")

        agents = re.sub(r"\s+", " ", AGENTS.read_text(encoding="utf-8")).lower()
        self.assertIn("start with the main agent alone", agents)
        self.assertIn("never require a subagent during default execution", agents)
        self.assertIn("model selection alone does not authorize subagents", agents)

    def test_delegated_dispatch_and_exact_single_ticket_verifier_coalescing(self) -> None:
        root = ROOT_SKILL.read_text(encoding="utf-8").lower()
        develop = (REPO_ROOT / "skills" / "develop-workflow" / "SKILL.md").read_text(encoding="utf-8").lower()
        verify = VERIFY_SKILL.read_text(encoding="utf-8").lower()
        for text in (root, develop, verify):
            normalized = re.sub(r"\s+", " ", text)
            self.assertIn("directly dispatch", normalized)
            self.assertIn("one free slot", normalized)
            self.assertIn("active main agent", normalized)
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
            "Write Ownership:",
            "Shared Resources / Conflicts:",
            "Relative Effort:",
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

    def test_new_requirement_contract_precedes_implementation_not_branch(self) -> None:
        skill = re.sub(r"\s+", " ", PLAN_TO_TICKET.read_text(encoding="utf-8")).lower()
        for invariant in ("docs/plans/<plan-id>.md", "before any other implementation edits",
                          "a branch may be created first", "read back every contract",
                          "no new plan/ticket issues", "no github comment write is required"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, skill)
        sequence = skill.split("### persistence sequence and failures", 1)[1].split("### publication conflict recheck", 1)[0]
        self.assertLess(sequence.index("save the complete plan"), sequence.index("read back markers"))
        self.assertIn("before any other implementation edits", sequence)
        self.assertIn("failed required read/write or read-back blocks", sequence)
        self.assertIn("on retry read the authoritative file first", sequence)
        self.assertIn("preserves other tickets, metadata and evidence", sequence)

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
            r"an independent requirement always receives a new plan and its own branch, including before the previous plan merges",
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
            r"require the persisted plan and its required ticket section metadata, and validate that they match the publication scope; missing or invalid metadata blocks commit, push, and pr creation/update",
        )
        self.assertRegex(
            push,
            r"before any commit, push, or pr creation/update, require the persisted plan and its required ticket section metadata and validate that they match the publication scope\. missing or invalid plan/ticket metadata blocks publication",
        )
        self.assertRegex(
            guide,
            r"require valid plan and ticket section metadata that matches the publication scope; missing or invalid metadata blocks publication",
        )
        self.assertNotRegex(
            publish + " " + push,
            r"(?:commit|push|pr creation/update) (?:may|can) proceed without (?:the )?plan",
        )
        self.assertNotIn("when it does not, publication proceeds normally", guide)

    def test_markdown_contract_and_stable_ticket_example(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        normalized = re.sub(r"\s+", " ", skill).lower()
        for invariant in ("same file", "### t0001", "#t0001", "behavior titles",
                          "ticket-id-tagged", "evidence summary:", "read back",
                          "serializes all writes", "preserves other tickets",
                          "append-only evidence in `## evidence`", "preserve prior passing and failing"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, normalized)
        template = re.search(r"Each Ticket uses these fields.*?```text\n(.*?)\n```", skill, re.S).group(1)
        self.assertIn("### T0001\n<!-- codex-ticket-id: T0001 -->", template)
        self.assertIn("docs/plans/<plan-id>.md#t0001", template)
        usage = WORKFLOW_USAGE.read_text(encoding="utf-8")
        example = re.search(r"### Markdown Plan example.*?```markdown\n(.*?)\n```", usage, re.S).group(1)
        self.assertEqual(example.splitlines()[:5], ["Status: planned", "Branch: docs/example-plan-contract", "Base: main", "PR: null", "Tickets: [T0001]"])
        self.assertEqual(re.findall(r"<!-- codex-ticket-id: (T\d{4}) -->", example), ["T0001"])
        self.assertIn("Ticket index: [T0001](#t0001)", example)
        self.assertIn("### T0001\n", example)

    def test_legacy_extensions_keep_original_issue_authority(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        legacy = re.sub(r"\s+", " ", skill.split("### Legacy continuation", 1)[1].split("### Effective completion", 1)[0]).lower()
        for invariant in ("including scope extensions", "single-issue sections stay there",
                          "original issues", "preserve ids, branch/base, pr and history",
                          "do not migrate", "or dual write", "required issue read/write failures block",
                          "close their issues", "completed merged plan is never reopened"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, legacy)
        for name in ("SKILL.md", "skills/develop-workflow/SKILL.md", "skills/verify-workflow/SKILL.md", "skills/publish-workflow/SKILL.md", "skills/github-push-when-ready/SKILL.md", "skills/integrate-workflow/SKILL.md"):
            with self.subTest(entrypoint=name):
                entrypoint = (REPO_ROOT / name).read_text(encoding="utf-8")
                self.assertIn("#legacy-continuation", entrypoint)
                self.assertNotIn("extension triggers canonical migration", entrypoint)

    def test_global_allocation_covers_history_branches_and_failures(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        ids = re.sub(r"\s+", " ", skill.split("### Naming and idempotency", 1)[1].split("### Authoritative Markdown record", 1)[0]).lower()
        for invariant in ("every page", "open and closed", "all", "multiple markers",
                          "working tree", "all visible local and remote branches", "including unmerged",
                          "refresh remote refs", "deduplicate copies", "never reuse", "incomplete scan blocks",
                          "pagination failure", "t9999", "serializes allocation", "ambiguous matches"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, ids)
        publication = re.sub(r"\s+", " ", skill.split("### Publication conflict recheck", 1)[1].split("### Legacy continuation", 1)[0]).lower()
        for invariant in ("before any commit, push or pr creation/update", "refresh visible remote refs",
                          "conflicting id blocks publication", "only new tickets in the current unmerged plan",
                          "never renumber historical issues, merged records or another plan",
                          "heading, marker, tickets index, dependencies", "evidence tags/summaries",
                          "commit/pr descriptions", "read back and rerun", "failure history"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, publication)
        for name in ("publish-workflow", "github-push-when-ready"):
            self.assertIn("#publication-conflict-recheck", (REPO_ROOT / "skills" / name / "SKILL.md").read_text())

    def test_ticket_allocation_requires_exact_successor_and_boundary_rules(self) -> None:
        skill = re.sub(r"\s+", " ", PLAN_TO_TICKET.read_text(encoding="utf-8")).lower()
        initial = skill.split("### naming and idempotency", 1)[1].split("### authoritative markdown record", 1)[0]
        repair = skill.split("### publication conflict recheck", 1)[1].split("### legacy continuation", 1)[0]
        self.assertIn("allocate exactly the combined maximum + 1", initial)
        self.assertIn("empty scan or maximum zero as zero, yielding `t0001`", initial)
        self.assertIn("allocate consecutively, updating the maximum after each id", initial)
        self.assertIn("at `t9999`, stop and report id exhaustion; never invent another format", initial)
        self.assertIn("allocating exactly the new combined maximum + 1", repair)
        self.assertIn("consecutively updating the maximum after each id", repair)
        self.assertIn("same empty/zero and `t9999` exhaustion rules above", repair)

    def test_merged_pr_completion_requires_identity_scope_and_no_postmerge_write(self) -> None:
        skill = PLAN_TO_TICKET.read_text(encoding="utf-8")
        completion = re.sub(r"\s+", " ", skill.split("### Effective completion from verified merge", 1)[1].split("### Branch, status", 1)[0]).lower()
        for invariant in ("effective plan and ticket status is `done`", "`in_review` or `pr: null`",
                          "do not create a post-merge status-only commit or pr", "discover the repository pr",
                          "exact recorded head branch and base", "merged state", "every current ticket",
                          "merged commit and full scope", "closed/unmerged prs", "ambiguous/missing pr",
                          "without requiring a markdown write"):
            with self.subTest(invariant=invariant):
                self.assertIn(invariant, completion)
        integrate = (REPO_ROOT / "skills/integrate-workflow/SKILL.md").read_text()
        self.assertIn("#effective-completion-from-verified-merge", integrate)

    def test_public_integration_summaries_preserve_derived_completion(self) -> None:
        overview = REPO_ROOT / "docs/architecture/overview.md"
        for path in (README, ROOT_SKILL, WORKFLOW_USAGE, overview):
            with self.subTest(document=path.relative_to(REPO_ROOT)):
                text = re.sub(r"\s+", " ", path.read_text(encoding="utf-8")).lower()
                for invariant in ("effective markdown plan/tickets", "exact verified merged pr",
                                  "full accepted scope", "without post-merge markdown/state edits",
                                  "only legacy issues are updated and closed"):
                    self.assertIn(invariant, text)
                self.assertNotRegex(text, r"mark(?:s|ing)? ticket sections done|plan markdown record closure")
        usage = re.sub(r"\s+", " ", WORKFLOW_USAGE.read_text(encoding="utf-8")).lower()
        integration = usage.split("`integrate-workflow` requires merge authorization", 1)[1]
        self.assertNotIn("refreshes `docs/repo_current_state.md`", integration)
        self.assertIn("validates the state and documentation index included in the pr", integration)

    def test_integrate_agent_prompt_preserves_premerge_state_and_derived_completion(self) -> None:
        prompt = (REPO_ROOT / "skills" / "integrate-workflow" / "agents" / "openai.yaml").read_text(encoding="utf-8").lower()
        self.assertIn("validate required repository state and documentation updates are included in the pr", prompt)
        self.assertIn("exact merged pr", prompt)
        self.assertIn("only legacy issues", prompt)
        self.assertNotIn("refresh repository state", prompt)
        self.assertNotRegex(prompt, r"mark(?:s|ing)? (?:plan|ticket) sections done")

    def test_public_planning_summaries_allow_only_initial_plan_edit(self) -> None:
        readme = README.read_text(encoding="utf-8")
        planning_row = next(line for line in readme.splitlines() if line.startswith("| `plan-workflow` |"))
        overview = (REPO_ROOT / "docs/architecture/overview.md").read_text(encoding="utf-8")
        planning = overview.split("`plan-to-ticket` may", 1)[1].split("### Fixed topology", 1)[0]
        for summary in (planning_row, planning):
            with self.subTest(summary=summary):
                text = re.sub(r"\s+", " ", summary).lower()
                for invariant in ("create or resume the plan branch", "save and read back only the complete canonical plan markdown",
                                  "before other implementation edits", "legacy issues retain original authority"):
                    self.assertIn(invariant, text)
                self.assertNotIn("no repository edits", text)
                self.assertNotIn("before the plan branch is created", text)

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

    def test_readme_skill_tables_match_installer(self) -> None:
        readme = README.read_text(encoding="utf-8")
        expected_workflows = {
            "codex-development-workflow", "plan-workflow", "develop-workflow",
            "verify-workflow", "publish-workflow", "integrate-workflow",
        }
        listed = []
        for heading, expected in (
            ("Workflows", expected_workflows),
            ("Specialist Skills", EXPECTED_SKILLS - expected_workflows),
        ):
            section = readme.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]
            rows = [line for line in section.splitlines() if line.startswith("| `")]
            names = [re.match(r"\| `([^`]+)` \|", row).group(1) for row in rows]
            self.assertEqual(set(names), expected)
            self.assertEqual(len(names), len(expected))
            listed.extend(names)
            for name, row in zip(names, rows):
                source = ROOT_SKILL if name == "codex-development-workflow" else (
                    REPO_ROOT / "skills" / name / "SKILL.md"
                )
                frontmatter_name = re.search(
                    r"^name: (.+)$", source.read_text(encoding="utf-8"), re.MULTILINE
                ).group(1).strip()
                self.assertEqual(name, frontmatter_name)
                self.assertIn(f"`${frontmatter_name} ", row)
        self.assertEqual(set(listed), EXPECTED_SKILLS)
        self.assertEqual(len(listed), len(EXPECTED_SKILLS))
        self.assertNotIn("## Installed skills", readme)
        self.assertNotIn("## Skill documentation", readme)

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
