# Workflow Usage Guide

> Type: Guide
> Status: Active
> Scope: Running the development workflow: stage routing, Plan/Ticket handoff, delegation, verification, publication, and completion order

Use `codex-development-workflow` as the entry point for repository work. It
routes a request to the stage workflow that owns it and carries the invariants
shared by every stage.

## Stage workflows

```text
Requirement
  -> plan-workflow        understand, design, decompose, persistence decision
  -> develop-workflow     implement to Development Complete
  -> verify-workflow      verification scope, level, and conclusion
  -> publish-workflow     documentation impact, redaction, commit, push, PR ready
  -> integrate-workflow   merge once, cleanup, close Issues, state and docs
```

Run one stage when that is all the request needs:

| Request | Stage |
|---|---|
| Plan, design, investigate, or decompose before code changes | `plan-workflow` |
| Implement, fix, refactor, or change repository content | `develop-workflow` |
| Verify acceptance criteria, a regression, or a branch | `verify-workflow` |
| Commit, push, or prepare a pull request | `publish-workflow` |
| Merge, clean up, or reconcile after delivery | `integrate-workflow` |

The full orchestration runs every stage as one explicitly authorized
end-to-end delivery:

```text
Create Plan branch
  -> Implement all Plan Tickets
  -> Test Quality Gate
  -> Documentation impact check
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> Merge the PR once
  -> Delete branch
  -> Update main
  -> Close Plan + Tickets
  -> Update State / Docs
  -> If separately authorized: external release handoff (outside this workflow)
  -> Evaluate workflow
  -> Reusable improvement? -> one bounded follow-up change or finish
```

Feature, Bug, Refactor, and Docs are profiles of these stages, not additional
workflows. They change verification breadth and whether a plan is persisted.
Planning depth and verification level may vary, but published work always uses
the branch and PR path: Docs, Code, Tests, Config, Refactor, Bugfix, Feature,
Dependency, and CI/CD changes may not direct-push around the PR gate.

## External deployment handoff

Deployment is outside this repository's workflow and does not invoke a bundled
deployment Skill. When separately authorized, the Plan owner hands the target
project's release owner the immutable artifact and source commit, target
environment and authorization, and documented deployment, health-check, and
rollback instructions. The external release owner performs and verifies the
rollout or rollback; record the external release result or incident link as
completion evidence with the delivery.

## Ticket-to-Slice hierarchy

A delivery batch that is complex, must survive a session boundary, or is
explicitly requested as a persisted plan gets one Plan Issue and at least one
Ticket Issue. When the batch includes multiple functionalities or has
dependencies, use this order:

1. Explicitly list the batch's planned functionalities and create its Plan Issue.
2. Split its functionalities into independently reviewable behavior Tickets.
3. Define each Ticket's scope, dependencies, acceptance boundary, and Issue.
4. Split each Ticket into dependency-ordered, independently verifiable
   Slices.

All Tickets and Slices for one Plan share the Plan's implementation branch.
Ticket dependencies determine execution order within the Plan; Slice
dependencies determine the execution order within a Ticket. A single-behavior
requirement is one Ticket containing one Slice, and a persisted plan still uses
one branch and one PR. The [Plan scope contract](../../skills/plan-to-ticket/SKILL.md#scope-and-sizing)
owns batch boundaries.

For every Slice, define:

```text
Goal, Scope, Out of scope, Dependencies, Acceptance criteria,
Relevant context/files, Test strategy, Test level, Test cases,
Validation command
```

The Ticket's fresh implementation worker executes dependency-ready Slices in
order. If an assumption is wrong, return to planning rather than expanding the
patch; the main agent owns that decision.

## Persistent plan and ticket handoff

Persist a plan when the work is complex, must survive a session boundary, or
the user explicitly asks for a persisted plan. Small, single-session work keeps
its plan inline.

For a persisted plan, GitHub Issues are the durable source of truth. Create or
update one Plan Issue and every required child Ticket Issue before the Plan
branch starts. The Plan Issue retains:

- `Status`: `planned`, `in_progress`, `blocked`, `in_review`, or `done`;
- `Branch`, `Base`, `PR`, and child Ticket index metadata;
- the batch goal, explicit functionality scope, milestones, completion rule,
  and delivery contract.

Each child Ticket Issue retains its Plan link, `Status`, `Dependencies`, goal,
scope, acceptance criteria, Slice plan, and validation contract. It does not
own `Branch`, `Base`, `PR`, or a separate merge.

The Plan Issue contains the overall batch plan and links to every Ticket
Issue. Chat output contains convenience links only.
`docs/Repo_Current_State.md` may link to the active Issue but must not become a
duplicate plan or backlog.

Search for stable plan/ticket markers before creating Issues so retries reuse
existing records. For a persisted plan, if the GitHub connector, repository
target, authentication, or required write fails, mark the operation blocked and
stop; do not fall back to local Markdown or an unpersisted chat response.

Update the Plan as work progresses: `in_progress` when its branch starts,
`blocked` for a blocking dependency or environment problem, `in_review` when
the PR is opened, and `done`/closed only after that PR is verified merged.
Update child Ticket status and acceptance evidence during execution; set all
child Tickets to `done` and close them with the Plan after the one merge.

## Branch and PR discipline

Published work goes through a branch and a pull request. A persisted Plan owns
exactly one branch, one PR, and one merge.

Use `<type>/<plan-id>-<short-description>` and create the branch from the
updated default branch. Ticket dependencies are completed and validated on this
branch; they do not require prerequisite Ticket merges. Keep the Plan's
implementation, tests, and related documentation on this branch; all Tickets
and internal Slices share it.

Verify the current branch and working tree before editing and preserve
unrelated or uncommitted work. Parallel workers use isolated worktrees or
return patches/findings for integration on the branch; never create a second
delivery branch for a Ticket. Before publishing, complete the Plan's acceptance
and relevant integration/regression checks for every Ticket and the batch. A
planned batch may share one commit and PR; follow the
[publication rules](../../skills/github-push-when-ready/SKILL.md#readiness-and-boundaries)
for staging, batch commit bodies and complete PR evidence. After creating or
updating the PR, merge it once the existing verification and publication gates
are satisfied. The Plan
Issue and implementation branch are a one-to-one pair; record and verify the
Plan's `Branch`/`Base` values, and require the PR head/base to match them.

## Adaptive agent orchestration

```text
ready Ticket -> fresh implementer: all dependency-ordered Slices + local checks
             -> separate fresh verifier: all functionality scenarios
             -> coordinator integrates evidence and decides gates
```

Follow the canonical [scheduling policy](../../AGENTS.md#multi-agent-delegation)
for worker roles, replacement, failure repair and safe waves, and
[Context Management](../../AGENTS.md#context-management) for thin coordinator
context, scoped handoffs, durable Issue checkpoints and recovery.
Codex dispatch uses `fork_turns="none"`; another host must provide equivalent
fresh agents with independent context or report BLOCKED. Workers execute their
role without spawning agents. The installable root/develop/verify/test Skills
carry the minimum runtime rules even in repositories without AGENTS.md.

## Verification

`verify-workflow` decides when verification runs, chooses one bounded level,
invokes `test-workflow`, and returns a conclusion. Use test-first development
for behavior changes, bug fixes, regressions, API behavior, core business
logic, data processing, and high-risk code when a meaningful failing test can
be produced. For docs, configuration, dependency updates, styling, typo fixes,
simple refactors, and exploratory work, use direct focused validation without
forcing RED/GREEN.

| Level | Use |
|---|---|
| `minimal` | Tiny changes, docs, configuration, styling, simple scripts. |
| `focused` | Default; checks directly tied to Slice acceptance criteria. |
| `regression` | Bug fixes, cross-module changes, demonstrated regression risk. |
| `full` | High-risk, release gates, or explicit requirements. |

Run the smallest set that provides sufficient evidence. The level controls
breadth, not PASS: stop only when the Test Quality Gate closes. Report the
level, the acceptance-to-test matrix, the quality-gate dimensions, commands,
results, evidence, N/A reasons, and any escalation reason.

### Local package validation

From this repository's checkout, run the existing package checks:

```bash
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
git diff --check
```

These checks cover managed bundle/source contracts, Test Quality Gate references
and Draw.io source structure and pairing. The
[installer regression checks](../deployment/installation.md#installer-regression-checks)
also exercise installation and update contents for both targets. They provide
local package evidence; independent Ticket verification still maps acceptance
to executed evidence before its coordinator decides the gate. Claude runtime
execution and a real GitHub publication/merge flow require their own evidence.

For PlantUML source/render changes, use the
[PlantUML rendering procedure](../../skills/plantuml/SKILL.md#integration-and-rendering).

## Post-delivery workflow evaluation

Run one lightweight retrospective after delivery and after any requested
deployment result is known. It evaluates the workflow rather than re-reviewing
the code, so it is not a merge gate.

Look only for evidence from the completed work:

- avoidable rework, failed assumptions, or repeated delivery failures;
- planning, context loading, or delegation that was too heavy or too weak;
- tests or redaction that were disproportionate to risk;
- repeated manual work that should be automated;
- unclear, duplicated, or missing workflow instructions.

Record a compact result:

```text
Keep: what worked and should remain
Improve: one highest-value reusable improvement, or none
Evidence: concrete event from this delivery
Action: none | follow-up change | report for later
```

Apply self-improvement only when the lesson is reusable and evidence-backed.
Prefer simplifying or removing redundant steps before adding new process. Never
weaken branch/PR, redaction, security, permission, or release
gates for convenience.

A low-risk improvement that stays within the existing workflow intent may start
automatically as one separate follow-up repository change. It must begin from
the updated default branch and repeat the normal branch, validation, redaction,
PR and merge lifecycle. Policy, permission, security,
release behavior, and broad project-scope changes are reported instead of
self-applied.

Only one automatic follow-up improvement may be created per delivered user
request. Its own evaluation cannot recursively create another automatic
improvement. If there is no meaningful evidence-backed improvement, finish
without inventing work or backlog entries.

## Output classification and redaction

Stage the intended change, then invoke `data-document-redaction` and follow
[redaction.md](redaction.md) before creating the commit. Repeat the scan after
any subsequent fix that changes staged content, before the next commit.

The scan returns `pass`, `findings`, `needs_review`, `noop`, or `error`. Only
`pass` and `noop` continue; record the inspected scope and skip only when the
staged change carries no sensitive surface. `findings`, `needs_review`, and
`error` stop the boundary transition until the reported gap is resolved.

The gate covers the staged commit set only. Document, PDF, Office, OCR,
repository-wide, and non-Git export sanitization are out of scope and need
project-specific tooling and review.

## Completion order

`plan-workflow -> develop-workflow -> verify-workflow -> publish-workflow -> integrate-workflow -> Evaluate workflow -> optional one bounded follow-up improvement`

`publish-workflow` stops at PR ready and never merges. `integrate-workflow`
merges once, deletes the branch, updates the default branch, closes the Plan and
its Tickets, refreshes `docs/Repo_Current_State.md`, and reconciles the
documentation index. State and documentation updates that change tracked
content after the merge go through their own change with the same gates.

For managed specialist sources and installation locations, see
[`../../references/skill-map.md`](../../references/skill-map.md).
