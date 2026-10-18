Status: in_progress
Branch: docs/single-model-escalation
Base: main
PR: null
Tickets: [single-model-escalation-01]

<!-- codex-plan-id: single-model-escalation -->

# Plan: Single-model defaults and user-selected escalation

## Goal
Use one model across workflow stages by default. After two consecutive failed
same-problem repair rounds, preserve evidence and wait for the user to select
an escalation model before continuing that problem. Start with the main agent
alone, including verification; delegation requires explicit user authorization.
Use high reasoning for planning, low for all other single-agent work, and
low development/repair plus high independent verification in delegated mode.

## Scope and validation
Update canonical routing, project instructions, develop/verify/test guidance,
repair role instructions, relevant documentation and workflow contract tests.
Default model remains gpt-6.1-sol. In delegated mode, development/repair uses low
and independent verification high; default execution keeps the main runtime.
Set the repository's main-agent default effort to low. Planning explicitly
requests high; report unsupported runtime switching rather than claiming it.
Default to single-agent execution; keep fresh independent workers only in
explicitly authorized delegated mode. Preserve evidence-based stage gates and
publication boundaries. Include direct-entrypoint prompts and delegation docs.
No new model dependency or automatic fallback. User now authorizes updating
local Codex Skills and AGENTS.md, plus commit, push, PR creation and merge of
this complete requirement. Preserve backups before updating local files.

## Ticket index
- [single-model-escalation-01](#single-model-escalation-01)

### single-model-escalation-01
<!-- codex-ticket-id: single-model-escalation-01 -->
Title: Make single-model execution and user-selected escalation explicit
Status: in_progress
Dependencies: []
Write Ownership: routing instructions, repair role, relevant docs and contract tests
Shared Resources / Conflicts: shared workflow contracts; serialized writes
Ticket Goal: Preserve a uniform default model and require explicit model selection at escalation.
Ticket Scope: all current routing entrypoints and contradictory escalation instructions.
Ticket Out of scope: automatic model choice, unrelated local configuration changes.
Ticket Acceptance Criteria:
- All stages default to Sol; effort varies by role, not task complexity.
- Initial implementation failure is excluded from repair count; two consecutive
  failed same-problem repair rounds trigger a durable checkpoint and user question.
- Pause affected problem pending an explicit user-selected model; do not silently
  retry Sol beyond the threshold or select another model/provider automatically.
- User-selected dispatch retains explicit model/effort, compatible role settings,
  independent verification in delegated mode, failure evidence and count;
  unavailable settings are reported.
- No user-selected model is hardcoded; main runtime is not silently reconfigured.
- The main agent performs initial implementation, checks, acceptance and local
  repair without subagents. Stage transitions or an initial failure do not
  activate delegation. After two failed repair rounds, wait for user model
  selection and explicit delegation authorization before spawning workers.
- Worker-only isolation/independent-verifier rules apply only in delegated mode;
  missing subagent support does not block default single-agent execution.
- Planning uses high in either execution mode. Other single-agent work, including
  self-verification, uses low. Delegated development/repair uses low and delegated
  independent verification high. No medium routing is introduced.
- Configured defaults and stage instructions agree; unavailable required effort
  is reported accurately, without silently accepting another level.
Relevant Context / Files: SKILL.md routing; AGENTS.md; skills/develop-workflow,
  verify-workflow and test-workflow; .codex/agents/sol-repair.toml;
  scripts/tests/test_workflow_contracts.py; relevant routing documentation.
Test Strategy: source-contract scenarios plus complete repository regression suite.
Test Level: regression
Validation Command: python3 -m unittest discover -s scripts/tests -p 'test_*.py'; git diff --check
Evidence Summary: Final effort matrix self-verified; 54 tests and CI checks PASS.
Local installation, publication and merge now authorized for this scope.
Refresh local installation evidence and final publication readiness before merge.
No subagents dispatched; historical failure evidence remains preserved.

## Evidence
- [single-model-escalation-01] User clarified that all stages use one model;
  selected two consecutive failed repair rounds as escalation threshold and
  explicitly chose to specify the escalation model when that threshold is met.
  Implementation and local verification authorized; publication not authorized.
- [single-model-escalation-01] Initial main worktree clean. Branch creation was
  denied by sandbox ref permissions; approved retry created the declared branch.
  No implementation edits preceded this Plan record.
- [single-model-escalation-01] Development Complete: updated canonical and stage
  routing, project guidance, Sol repair role, documentation and contract tests.
  Corrected an existing ticket-loop diagram that prescribed Luna and automatic
  Sol/high escalation; rendered its paired SVG. Unrelated diagrams unchanged.
  Worker reports all 52 tests PASS (31.371s), git diff --check PASS, shell syntax
  checks for both CI scripts PASS and Python test compilation PASS. No validation
  or rendering failures. Requested implementation worker: gpt-6.1-sol / low;
  underlying inference identity was not independently exposed. No publication.
- [single-model-escalation-01] Initial independent Ticket and final Plan acceptance
  FAIL on snapshot 584bc3fe0c1bd3ac709d6ac99bdd8abe2e5c323348a6e19409b0b9c84f576d3d:
  docs/Repo_Current_State.md still described ticket-loop source as unchanged and
  using older Luna routing. Other acceptance scenarios passed. All 52 tests PASS
  (36.701s), whitespace/shell syntax/compilation PASS. SVG XML and embedded source
  consistency PASS; remote rerender returned HTTP 403, so no independent live
  byte-for-byte rerender comparison claimed. Snapshot unchanged by verification.
  Requested verifier gpt-6.1-sol / high; underlying runtime identity not exposed.
  Initial failure is not a repair round; same-problem failed repair count: 0.
- [single-model-escalation-01] Repair round 1 implemented by fresh Sol/low worker:
  corrected only the stale current-state diagram paragraph, preserving unrelated
  limitations and the HTTP 403 independent-rerender limitation. Focused source
  comparison and git diff --check PASS. No new failure; fresh acceptance pending.
  Requested worker gpt-6.1-sol / low; underlying runtime identity not exposed.
- [single-model-escalation-01] Fresh independent Ticket and exact-scope whole-Plan
  acceptance PASS on unchanged snapshot
  a7068e488ee540c31d14dc9a46d456fe7f7ebb2b69f36e1f0b63638a6d5358ff.
  All 52 tests PASS (24.852s); git diff --check, both CI shell syntax checks and
  Python compilation PASS. Full semantic review confirms requested routing and
  corrected recovery documentation. SVG XML, rendered labels and decoded source
  consistency PASS. The verifier's initial comparison helper included PlantUML
  wrappers incorrectly; corrected comparison resolved that explained helper
  failure without repository edits. Remote byte comparison remains unverified
  after documented HTTP 403. Repair round 1 passes, failed same-problem repair
  count remains 0. Requested verifier gpt-6.1-sol / high; underlying inference
  identity not exposed. Main agent accepts the Test Quality Gate for this
  instruction-only change: static contract tests plus independent semantic and
  source/artifact review; live model availability is not claimed. Local stage
  complete; no commit, push, PR, merge or installed-bundle update performed.

- [single-model-escalation-01] Supplementary clarification: initial execution must
  use no subagents. Update this same requirement before implementation; preserve
  earlier evidence above. Main agent now owns implementation and self-verification
  directly under the user's explicit instruction. Retain the two-round threshold;
  model choice alone does not authorize multiple agents. No publication authorized.
- [single-model-escalation-01] Supplementary implementation and self-verification:
  main agent changed default mode in AGENTS.md/root and all direct stage entrypoints,
  scoped worker isolation/independent acceptance to authorized delegation, and
  updated develop/verify prompts and relevant documentation. No subagents created.
  Initial focused contract run failed because its new assertion required the
  exact wording "delegation authorization" while the verify prompt equivalently
  said "explicitly authorized delegated mode"; corrected that over-specific test
  assertion. Focused rerun: 37 tests PASS. Full suite: 53 tests PASS (9.939s).
  Both CI shell syntax checks, Python compilation and git diff --check PASS.
  Prior independent PASS is not attributed to this supplementary scope.
  This is main-agent self-verification, with executed source-contract tests and
  semantic review; it establishes no live model availability or merge completion.
  No commit, push, PR, merge or installed-bundle update performed.
- [single-model-escalation-01] Final user-approved effort clarification persisted
  before implementation: planning high; other single-agent work low, including
  self-verification; delegated development/repair low and independent verification
  high. Earlier medium proposals are superseded. Main-agent default config will
  change high to low; no subagents, installation or publication authorized.
  Preserve existing branch, Ticket, historical evidence and two-round escalation.
- [single-model-escalation-01] Final effort-matrix implementation and local
  acceptance PASS: main-agent default config is gpt-6.1-sol / low; planning
  explicitly requires high in either mode; other single-agent work, including
  self-verification, low; delegated development/repair low and independent
  verification high. Existing repair/verifier role settings remain compatible.
  Updated AGENTS.md, root and all direct workflow entrypoints, planning/develop/
  verify prompts, relevant documentation and source-contract tests. Unsupported
  effort settings must be reported; no live setting change inferred from files.
  Focused 38 tests PASS, full 54 tests PASS (17.289s), CI shell syntax checks,
  Python compilation and git diff --check PASS. No new failures. Main agent
  performed implementation, semantic review and self-verification directly,
  without subagents or a claim of independent verification for this final scope.
  Earlier rendering limitation remains unchanged. No publication or installation.
- [single-model-escalation-01] Publication/local-update authorization: user
  requested PR creation and merge, then explicitly confirmed synchronizing local
  Skills and AGENTS.md while continuing PR/merge. Scope includes this complete
  requirement only. Local AGENTS.md contains two exact copies of the repository
  baseline; back up before replacing with one current canonical copy. Use the
  existing ownership-aware Codex installer and preserve recoverable Skill backups.
  No global runtime config or other host installation is included.
- [single-model-escalation-01] Local synchronization PASS: backed up the prior
  global AGENTS.md and all 14 managed Skill directories outside the repository,
  ran bash scripts/install-all.sh --target codex --update, and compared each
  installed SKILL.md and agents/openai.yaml byte-for-byte with source. All 14
  ownership markers match. Global AGENTS.md now exactly matches the repository
  version as one document, replacing two identical old copies. No unrelated
  global runtime configuration changed. Restart is required for Skill discovery.
  origin/main still matches branch base a95e705; no existing Plan PR or remote
  branch found. Publication remains authorized for this requirement.
- [single-model-escalation-01] Publication readiness revalidation PASS: all 54
  tests PASS (15.595s), shell syntax, Python compilation and whitespace checks
  PASS. Independent Kroki GET rerender of ticket-loop.puml exactly matches the
  tracked SVG (SHA256 6a4193565294fcd5db14e193f889b050c00ac180545bca8dee87709b0c99ace1),
  resolving the earlier POST HTTP 403 comparison limitation without changing
  that failure evidence. Initial historical-scan command used an unsupported
  gh --slurp flag; reran supported gh api --paginate and decoded its output.
  All 252 historical Issue/PR records and 8 Plan copies across 4 visible refs
  checked: no current Plan/Ticket ID collision. origin/main matches branch base.
  Complete current-scope Ticket and Plan acceptance revalidated by the main
  agent under the authorized single-agent policy; no independent-agent claim.
- [single-model-escalation-01] Pre-commit scope/redaction gate PASS: exactly 27
  declared requirement files staged, including intentionally versioned AGENTS.md.
  No forbidden secret files, private keys or high-confidence credential patterns
  found. Plan/branch/base and single-Ticket scope match the authorized delivery.
- [single-model-escalation-01] Initial commit attempt stopped before creating
  a commit because this checkout has no Git author identity. Use the authenticated
  GitHub account's public noreply identity for this commit only via per-command
  Git settings; do not change global configuration. No staged changes lost.
