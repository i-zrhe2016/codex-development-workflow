---
name: codex-development-workflow
description: "Route repository work to plan, develop, verify, publish or integrate; orchestrate all stages only for explicitly authorized end-to-end delivery. Preserve Test Quality Gate, staged redaction, Conventional Commits and branch/security/permission/release gates."
---

# Development Workflow

Stage skills own **when** work runs; capability skills own **how**. Read and
follow each invoked skill's `SKILL.md`; report a required skill's absence rather
than inventing a replacement. Feature, Bug, Refactor and Docs are profiles,
changing planning depth and verification breadth without adding stages.

## Routing

| Request | Stage |
|---|---|
| Plan, design, investigate, decompose before changes | `plan-workflow` |
| Implement, fix, refactor, change repository content | `develop-workflow` |
| Verify acceptance, regression, incident, review finding or branch readiness | `verify-workflow` |
| Commit, push, open/update PR, prepare review | `publish-workflow` |
| Merge, clean up, close Plan/Tickets, reconcile state | `integrate-workflow` |
| Explicitly authorized complete delivery | Full orchestration below |

Run only the requested stages, respecting their stopping boundaries. The main
agent owns requirements, architecture, persistence, dependencies, scheduling,
integration, gates, evaluation and final judgment.

## Shared invariants

- Never weaken branch/PR, redaction, security, permission or release gates.
- Published changes use a branch and PR, never direct default-branch delivery.
  One purpose per Conventional Commit 1.0.0; acceptance and relevant integration
  checks pass before publication. Readiness is separate from verified merge.
- Verify branch and worktree before editing; preserve unrelated/uncommitted
  work. Preserve abandoned Ticket work and re-plan; never automatically reset
  user changes or delete unmerged branches.
- No future-Slice features, unrelated refactors, formatting sweeps or dependency
  upgrades. Load only needed context; record results before the next Slice.
- PASS requires `test-workflow`'s risk-aware **Test Quality Gate**: every
  acceptance criterion has executed evidence; applicable dimensions pass or
  carry concrete N/A reasons. Coverage is diagnostic only, and retry cannot convert an unexplained flaky failure to PASS.
- Run the staged redaction gate before every commit; reconcile verified state
  only after merge, branch cleanup and default-branch synchronization.

## Plan and Slice contracts

Use `plan-workflow` and `plan-to-ticket` to settle architecture/scope and
establish Plan -> behavior Tickets -> dependency-ordered Slices, in that order.
Persist when complex, cross-module, dependent, multi-session/resumable, or
explicitly requested; small single-session work stays inline. Planning controls
scope; verification controls evidence, and neither replaces the other.

A persisted Plan owns one Issue, one branch from the updated default branch
(`<type>/<plan-id>-<short-description>`), one PR and one merge. Each Ticket owns
one child Issue and its tests/docs; every Ticket/Slice shares the Plan branch
and base. Prerequisites are validated on that branch, without Ticket merges.
Every required Issue must exist before branch creation; Issue failure blocks
work with no local Markdown/chat-only fallback.

Follow `plan-to-ticket` for identifiers, metadata, persistence and updates.
Before the first edit, record exact `Branch`/`Base` and `Status: in_progress`;
verify them when resuming. PR head/base must match, and opening it records `PR`
and `in_review`. Keep Plan/Tickets open until verified merge, then set `done`
and close. Child Tickets carry no independent branch/PR metadata.

Each independently understandable Slice contains Goal, Scope, Out of scope, Dependencies, Acceptance criteria,
Relevant context/files, Test strategy, Test level, Test cases and Validation
command. Execute dependency-ready Slices using `develop-workflow`; `verify-workflow`
selects minimal/focused/regression/full and invokes `test-workflow` for evidence
and the quality gate.

## Adaptive execution

Follow `AGENTS.md`'s delegation policy where available. Within the current
stage, choose the smallest useful self/delegated wave by dependency readiness,
clear ownership, speed, context isolation, evidence, quality, risk and host
capacity; concurrency is a ceiling. Never pre-assign the entire Plan or hard-code
task classes to agent names; select available built-in/project agents by their
contract and description. Single-agent execution remains valid.

Keep dependent or overlapping files/interfaces/schemas/migrations/shared config
sequential. Parallel workers use isolated worktrees or return patches/findings
for main-agent integration on the Plan branch; never switch a directory shared
by active workers or create Ticket delivery branches. Uncertain write isolation
means read-only delegation or returned patches.

Delegations specify goal, scope/exclusions, files/ownership, dependencies,
acceptance, validation and expected summary. Do not duplicate active delegated
work. Return findings, changes/patches, test results, risks and follow-up work, not raw logs.
Integrate each wave and recompute readiness after material results, failure,
dependency changes or integration. Prefer one delegation level unless explicitly
required. Subagents cannot reorder stages, advance gates, publish, merge or
replace main-agent judgment.

## Full orchestration

Only for explicitly authorized end-to-end delivery. Full deliveries spanning
multiple Tickets, dependencies or sessions persist before branch work:

1. `plan-workflow`: work definition, persistence and single Plan branch.
2. `develop-workflow`: implementation to Development Complete.
3. `verify-workflow`: selected verification and Test Quality Gate.
4. `publish-workflow`: `repo-documentation` impact check -> staged redaction ->
   `github-push-when-ready` commit/push/PR readiness. Update canonical docs/index
   or record no documentation impact; fix blocking findings and revalidate.
5. `integrate-workflow`: merge once -> source-branch deletion -> default-branch
   update -> Plan/Ticket closure -> `repo-current-state` and documentation
   reconciliation when verified state changed. Tracked post-merge updates use
   their own branch/PR gates.
6. Evaluate delivery once; optionally run one bounded follow-up below.

This order and its contracts/gates remain fixed under delegation. Read
`docs/Repo_Current_State.md` at planning start; keep it a compact verified
recovery point (focus, capabilities, current/next Slice, failures, constraints,
architecture), linking active Issues instead of copying backlog/test reports.

External deployment is outside this bundle. When separately authorized, hand
the target release owner the immutable artifact and source commit, environment and
authorization, deployment/health-check/rollback instructions. That owner performs and verifies
rollout/rollback; record the external release result or incident link as evidence.

## Redaction gate contract

Stage intended files, invoke `data-document-redaction`, and follow
[redaction workflow](docs/workflow/redaction.md). Repeat after staged fixes.
Continue only on `pass`, `noop` or recorded no-sensitive-surface skip with scope.
`findings`/`needs_review`/`error` block transition: sanitize reported files only,
re-stage/re-scan to pass; resolve scanner errors first. Report types/paths/lines,
never values, mappings, credentials or full matching context. This protects the next
commit, not repository/history cleanliness; document/PDF/Office/OCR and non-Git
export sanitization are outside scope.

## Capability routing

Invoke only on the applicable trigger, following the owner's procedure:

| Capability | Trigger |
|---|---|
| `plan-to-ticket` | Plan/Ticket/Slice decomposition and persisted Issue contracts |
| `test-workflow` | Selected validation, risk dimensions and bounded evidence |
| `repo-documentation` | Every change's impact check; docs normalization/audit/organization |
| `plantuml` | Architecture/flow materially clearer as a diagram; `.puml` edits/review or required source/render pair |
| `repo-current-state` | Verified state changes after integration/synchronization |
| `data-document-redaction` | Next staged commit; repeat after blocking fixes |
| `github-push-when-ready` | Branch publication, commit, push or PR readiness |

## Post-delivery evaluation

Evaluate once after delivery; this is not a merge gate and must not delay it.
Use completed-work evidence: rework/assumptions/failures, excessive/weak
planning/context/delegation, disproportionate tests/redaction, repeated manual
steps, unclear/duplicate/missing instructions. Report:

```text
Keep: what worked
Improve: one highest-value reusable improvement, or none
Evidence: concrete delivery event
Action: none | follow-up change | report for later
```

Prefer simplifying/merging/removing before adding process or artifacts. Only
concrete, reusable, low-risk improvements within current intent may start
automatically. Report policy/permission/security/release/broad-scope changes
instead. A follow-up starts from updated default branch and repeats the full
Plan -> Branch -> Test -> applicable Redaction -> Commit -> Push -> PR -> Merge
lifecycle; never edit completed/default branches or installed skills as an
evaluation side effect. At most one automatic follow-up per user delivery; its
evaluation cannot start another. Without evidence, finish without invented work
or backlog noise.

## Requested timing

Only when asked, measure monotonic command-boundary durations for Plan/Ticket
setup/branch creation, implementation, validation, redaction, commit/push, PR,
merge/cleanup and requested installation/synchronization. Report total separately
and dominant latency. Timing adds no gate; persist no session timing logs and
expose no credentials/tokens/private endpoints.

## Installation

From a full checkout:

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
# update
bash scripts/install-all.sh --update
```

Copies root and bundled `skills/`, without cloning specialist repositories.
`--target codex` is default; use `--target claude` for Claude Code and repeat
that target on update (`--update` alone updates Codex). Restart the host.
Repository-only `docs/deployment/installation.md` documents destinations/full
procedure; it is not installed with this bundle.
