Status: in_progress
Branch: refactor/markdown-plan-records
Base: main
PR: null
Tickets: [T0078]

<!-- codex-plan-id: markdown-plan-records -->

# Plan: Markdown Plan and Ticket records

## Goal
New requirements use one versioned docs/plans/<plan-id>.md containing Plan,
Tickets and append-only evidence. Existing Issue requirements remain unchanged.

## Scope and validation
Update workflow skills, agent prompts, repository rules, docs, diagrams and
contract tests. Preserve stage gates and authorization. No commit, push, PR,
merge or installed-skill updates. Run repository contract, installer and diagram
checks. One Plan branch, one optional PR and merge.

## Ticket index
- [T0078](#t0078)

### T0078
<!-- codex-ticket-id: T0078 -->
Title: Persist new Plan and Ticket contracts in Markdown
Section: docs/plans/markdown-plan-records.md#t0078
Status: in_progress
Dependencies: []
Write Ownership: workflow sources, documentation, diagrams, contract tests
Shared Resources / Conflicts: shared workflow contracts; writes serialized
Relative Effort: medium
Ticket Goal: Replace new-requirement Issue persistence with versioned Markdown.
Ticket Scope: all workflow entrypoints and associated contract evidence.
Ticket Out of scope: historical migration, installed skills, publication.
Function Checklist:
- [x] New requirements use a complete Plan MD before implementation edits.
- [x] Legacy requirements retain original Issue authority.
- [x] IDs scan historical Issues and visible branch MD; conflicts are repaired.
- [x] Evidence failures do not unlock dependencies; merge determines done.
Requirements: stable anchors, append-only passing/failing evidence, serialized writes.
Non-goals: new scheduler, service, global ledger, automatic publication.
Ticket Acceptance Criteria: consistent runtime instructions and passing regression checks.
Relevant Context / Files: root SKILL.md, skills/, AGENTS.md, docs/, scripts/tests/
Test Strategy: contract regression, installer regression, diagram source/render checks.
Test Level: regression
Test Cases: creation/read-back/retry, anchors, legacy continuation, multi-marker ID
scan, branch conflicts/reference repair, scan failure/exhaustion, verified merge.
Validation Command: python -m unittest discover -s scripts/tests -p 'test_*.py'
Evidence Summary: implementation complete; fresh independent Ticket and identical
whole-Plan acceptance PASS; 51 tests passed. Prior failures preserved below.

## Evidence
- [PLAN] 2026-10-15: approved user plan; clean clone at
  6ac63d3e14300d2487d89d75ff5e08cb2b867bbe. Historical Issue marker scan
  completed (three API pages, 250 records), maximum T0077; visible refs contain no Plan MD.
  Allocated T0078. No installed skills or remote state modified.

- [T0078] Development Complete: workflow contract and scratch installer suite
  passed, 47 tests (47.653s), using WSL Ubuntu-24.04 / Python 3.12.3. Initial
  run failed 24 installer/diagram fixtures because Windows checkout shell files
  had CRLF (`pipefail` with trailing CR); normalized shell working-copy line
  endings without tracked script content changes and reran successfully.
  Changed diagrams and independent acceptance remain pending.

- [T0078] Diagram validation: six changed PlantUML/SVG pairs rendered through
  public Kroki encoded GET using curl.exe; a second fetch matched all six files
  byte-for-byte. Native urllib POST failed HTTP 403 and urllib GET failed TLS
  EOF before the successful curl route; no failed render was saved. Final
  focused workflow contract run: 31 tests PASS (0.212s). No global diagram PASS
  claimed; inherited unrelated diagram drift/routing labels remain documented.

- [T0078] Independent acceptance FAIL on snapshot SHA256
  32497adb3a41670ef58b92ba84904f0e1dc9b946cbfd3a81a18721c4149a4ef5:
  47 tests PASS (10.166s), six rendered pairs independently matched and visually
  inspected, but README/workflow/architecture/root summaries still instructed
  post-merge record mutation or prohibited branch/Plan setup. Fresh repair owner
  assigned for both P2 findings; preserve this failure and reverify with a new
  verifier. Initial acceptance failure is not a failed repair round.

- [T0078] Repair round 1 Development Complete: corrected public planning and
  integration summaries in README, root workflow, architecture and usage. Added
  two regression checks for branch/Plan-only setup and verified-merge completion
  without post-merge Markdown/state writes. Focused workflow suite: 33 PASS;
  git diff --check PASS. No diagrams/runtime contract changes. New independent
  verification required; prior failure remains preserved above.

- [T0078] Repair round 1 independent acceptance FAIL: 49 tests PASS (9.713s),
  but installed integrate-workflow agents/openai.yaml still requested refreshing
  tracked state/docs after merge. Its packaged SHA256 was
  c22d0b11e19f6f0dcdcf9828ef9fa124420c2a343bfe3f0bcfdfa87649b2baec.
  Verified source fingerprint
  1bf6c08f99c08783ebbae70e42cbb81f2fe6569ea0e13ca31981d642ea3be527
  was unchanged. Regression omitted the YAML surface. Preserve this failed
  repair round (count 1); fresh repair round 2 will cover shipped prompts.

- [T0078] Repair round 2 Development Complete: corrected the shipped
  `skills/integrate-workflow/agents/openai.yaml` prompt to validate PR-included
  state/docs and effective merged-PR completion; legacy Issue mutation remains
  legacy-only. Added an installed-prompt regression assertion. Focused prompt
  checks: 2 PASS; git diff --check PASS. Fresh final acceptance required.

- [T0078] Repair round 2 acceptance: prompt defect resolved; 50 tests PASS
  (10.096s), scratch prompt bytes match SHA256
  09e8e652978af3d3e76df71f027f7086fa590c65ed08783983c5692747fdda8e;
  old prompt mutation rejected. Remaining FAIL: allocation says only above the
  maximum, while approved scope explicitly requires maximum + 1.
- [PLAN] Coordinator diagnosis/replan after two unsuccessful full acceptance
  repair cycles: previous fixes were limited to discovered wording and tests
  mirrored those phrases, leaving an approved quantitative invariant implicit.
  Preserve both failures. Replan minimal final precision repair: explicitly
  allocate current combined maximum + 1 (T0001 when empty), including collision
  repairs; add canonical/public contract assertion and exhaustion boundary.
  This does not expand scope, alter numbering format or authorize publication.

- [T0078] Precision repair Development Complete: canonical initial allocation
  and collision repair now require combined maximum + 1, empty scan T0001,
  consecutive new IDs and no wrap after T9999. Usage summary synchronized;
  focused workflow tests 35 PASS; diff check PASS. Fresh verifier required.

- [T0078] Final independent acceptance PASS: 51 tests passed (9.919s) under
  WSL Ubuntu-24.04 / Python 3.12.3; exact max+1 initial/collision-rule mutations
  were each rejected. Fixed 106-file source fingerprint before/after:
  bc44fb05a34b9ebc13defdbe9c1803816ece3825688b9bee57ea685b363781da.
  Test Quality Gate PASS for Ticket and identical whole one-Ticket Plan.
  Packaged prompt bytes unchanged; six diagram render/visual checks retained.
  Diff check PASS. No live GitHub writes or user-skill updates tested/claimed.
  This append-only checkpoint and state verification metadata update occur after
  acceptance; runtime instructions, tests, prompts and diagrams stay unchanged.
  Local verified work stops in_progress, not done, pending publication decision.
