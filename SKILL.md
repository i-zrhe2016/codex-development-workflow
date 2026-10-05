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

Run only the requested stages and publication actions, respecting their stopping
boundaries. Local verified functionality is a normal stopping point; awaiting
the user's publication decision is not BLOCKED. The user chooses commit, push,
PR creation/update and merge timing and scope. Existing authorization persists
for its stated batch; added feature scope alone never extends it. The main
agent owns requirements, architecture, persistence, dependencies, scheduling,
integration, gates, evaluation and final judgment.

When the user states that they control the overall flow, preserve that control:
prompt them with the main workflow, prerequisites, risks and available next
actions, but do not choose scope, stage transitions, publication actions,
timing or trade-offs on their behalf. Execute only decisions the user has made
explicitly; otherwise stop at the current authorized boundary and ask for the
next decision.

## Shared invariants

- Never weaken branch/PR, redaction, security, permission or release gates.
- Commits and pushes use a non-default branch; final delivery uses a PR merge.
  Never commit/push directly to default or force a PR after commit-only/push-only
  work. Implementation/verification alone never triggers publication.
  Use Conventional Commits 1.0.0 for one functionality or a clearly planned
  multi-function batch per commit/PR. Every Ticket's acceptance and the batch's
  relevant integration/regression checks pass before publication; any failure
  blocks the batch. Readiness is separate from verified merge.
- Verify branch and worktree before editing; preserve unrelated/uncommitted
  work. Preserve abandoned Ticket work and re-plan; never automatically reset
  user changes or delete unmerged branches.
- No future-Slice features, unrelated refactors, formatting sweeps or dependency
  upgrades. Load only needed context; record results before the next Slice.
- PASS requires `test-workflow`'s risk-aware **Test Quality Gate**: every
  acceptance criterion has executed evidence; applicable dimensions pass or
  carry concrete N/A reasons, including separate AuthN/AuthZ proof and
  falsifiable assertion strength when relevant. Coverage is diagnostic only,
  and retry cannot convert an unexplained flaky failure to PASS.
- Verification must prove Same-Surface Verification: intended artifact, runtime
  instance and user-facing surface match scope; runtime identity/doctor succeeds;
  the verifier follows Launch -> Doctor -> Drive -> Evidence -> Cleanup. If the
  artifact, instance or surface cannot be proven, report BLOCKED.
  Repository-specific verification profiles or feature maps belong under
  `docs/verification/`, not in a new workflow Skill.
- Run the staged redaction gate before every commit. When verified repository
  state materially changes, update `docs/Repo_Current_State.md` on the same
  Plan branch before commit/PR creation so the PR carries the state change with
  the work; integration validates the merged state rather than creating a
  separate state-only PR.

## Plan and Slice contracts

Use `plan-workflow` and `plan-to-ticket` to settle architecture/scope and
establish Plan -> behavior Tickets -> dependency-ordered Slices, in that order.
Persist when complex, cross-module, dependent, multi-session/resumable, or
explicitly requested; small single-session work stays inline. Planning controls
scope; verification controls evidence, and neither replaces the other.

A Plan is a delivery batch with explicitly listed scope; it may include one or
multiple independent functionalities, each bounded by behavior Tickets. Follow
`plan-to-ticket` for scope and `github-push-when-ready` for batch staging and
message/PR requirements.

Before merge, append new user-requested functionality to the same Plan as a
new Ticket using `plan-to-ticket`'s scope-update contract; after merge use a new
Plan. Preserve IDs, branch/base, existing PR and accepted evidence. Update
goal/scope/index/dependencies/validation before edits. An open PR retains its
URL but expanded scope returns the Plan to `in_progress`, invalidates impacted
acceptance/batch readiness and requires revalidation, including final
Plan/branch/PR acceptance, before an authorized update. An existing PR is not
ready for the expanded scope.

A persisted Plan owns one Issue, one branch from the updated default branch
(`<type>/<plan-id>-<short-description>`) and, if the user elects delivery, one PR
and one merge. Each Ticket owns
one child Issue and its tests/docs; every Ticket/Slice shares the Plan branch
and base. Prerequisites are validated on that branch, without Ticket merges.
Every initially required Issue must exist before branch creation; appended
Tickets and scope updates must persist before their edits. Issue failure blocks
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

## Ticket workers and adaptive execution

The main agent coordinates design, dependencies, integration and gates; it does
not implement Tickets or replace their independent verifiers. For every Ticket,
including docs/config/test and inline one-Slice work, dispatch one fresh
implementation agent for all dependency-ordered Slices, then a separate fresh verification
agent for all functionality scenarios. Ordinary per-Ticket verification uses
one verifier. Never reuse workers across Tickets or split a Ticket's
Slices/scenarios across agents. Same-Ticket follow-up is allowed.
Already-dispatched implementation/verification workers run only their assigned
role, never spawn agents or run coordinator orchestration.

Final Plan/branch/PR acceptance verification is separate. Before deciding
publication, PR update or merge readiness, dispatch three fresh independent
verifier agents.
Each verifies the whole current Plan branch/PR scope. All three must PASS; any
FAIL or BLOCKED blocks readiness and preserves evidence. Do not reuse Ticket
implementers, Ticket verifiers or prior final verifiers for this gate.

For Codex, every `spawn_agent` uses `fork_turns="none"`. Other hosts must provide
equivalent fresh agents with independent context; otherwise report BLOCKED,
without main-agent fallback. Manually hand off role, current Ticket goal/scope/
non-goals, Slice dependencies/acceptance, relevant files/ownership, Plan branch/
base and verified prerequisites, validation commands and expected summary.
Never include the parent conversation or unrelated history. These minimum
rules apply even without `AGENTS.md`; it owns the full repository policy when
present and is not installed with the bundle.

Verifiers are read-only except caches/temporary evidence. Failures return to
implementation; after fixes dispatch a new verifier for the affected function,
preserving failed evidence and the flaky-test gate. Interrupted/failed workers
are replaced by fresh agents from verified checkpoints. The main agent owns
the final Test Quality Gate and stage decisions.

Schedule ready Tickets within host capacity; do not pre-assign the Plan. Keep
dependent or overlapping writes/interfaces/schemas/migrations/config and shared
test state sequential. Independent context does not isolate files: use safe
ownership and isolated worktrees or returned patches on the shared Plan branch,
never Ticket branches or directory switching under active workers. Integrate
each wave, recompute readiness from results, and do not duplicate worker work.
Agent selection and useful concurrency remain adaptive under `AGENTS.md`.

## Full orchestration

Only for explicitly authorized end-to-end delivery of the stated batch, including
publication and merge. Readiness alone grants neither action. Stop at any narrower
authorized boundary, including local verification, commit-only or push-only;
added scope returns to planning and does not inherit publication authority from
the earlier batch. Full deliveries spanning
multiple Tickets, dependencies or sessions persist before branch work:

1. `plan-workflow`: work definition, persistence and single Plan branch.
2. `develop-workflow`: implementation to Development Complete.
3. `verify-workflow`: selected verification and Test Quality Gate, including
   three-verifier final Plan/branch/PR acceptance when delivery readiness is
   being decided.
4. `publish-workflow`: `repo-documentation` impact check -> update
   `docs/Repo_Current_State.md` when represented state changed -> staged
   redaction -> `github-push-when-ready` commit/push/PR readiness. Update
   canonical docs/index or record no documentation impact; fix blocking
   findings and revalidate.
5. `integrate-workflow`: merge once -> source-branch deletion -> default-branch
   update -> validate merged state/docs included in the PR -> Plan/Ticket
   closure. Missing required state/docs changes return to publication on the
   Plan branch instead of creating a post-merge state-only PR.
6. Evaluate delivery once; report any bounded follow-up below for a user decision.

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

Prefer simplifying/merging/removing before adding process or artifacts. Report
concrete, reusable improvements for the user to choose; evaluation
authorizes no implementation or publication. A user-requested follow-up after
merge starts a new Plan from the updated default branch and follows only its
authorized stages/actions, preserving all applicable gates. Never edit
completed/default branches or installed skills as an evaluation side effect.
Evaluate at most one follow-up per user delivery without recursively starting
another. Without evidence, finish without invented work or backlog noise.

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
