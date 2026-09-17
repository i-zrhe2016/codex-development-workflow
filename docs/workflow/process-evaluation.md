# Workflow Process Evaluation

Use this file to evaluate whether the development workflow is becoming heavier
than the value it provides. It is a process-retrospective reference, not a
second workflow specification and not a session log.

## Goal

After a real workflow run, determine whether any stage, handoff, check, or
record was redundant, disproportionately expensive, unclear, or missing. Keep
mandatory safety and delivery gates intact while reducing unnecessary work.

The preferred improvement order is:

```text
Remove duplication -> simplify -> merge steps -> automate -> add new process
```

Do not add a new stage, agent, skill, document, or persistent record when a
smaller change solves the same problem.

## Evaluation rules

1. Evaluate observed evidence from an actual run, not hypothetical preferences.
2. Separate required gates from their implementation. A gate may be necessary
   while its repeated execution, documentation, or context loading is not.
3. Prefer one reusable improvement over a list of speculative improvements.
4. Do not weaken branch/PR, review, security, redaction, permission, or release
   controls merely to reduce friction.
5. Do not update this file after every successful run. Persist a finding only
   when it is reusable, repeated, or high-impact.
6. A self-improvement change follows the normal branch/PR/review lifecycle.
   Never modify the completed branch or default branch as a retrospective side
   effect.
7. A self-improvement run must not recursively create another automatic
   self-improvement run.

## What to inspect

| Area | Question | Typical redundancy signal |
|---|---|---|
| Planning | Was Slice planning and Ticket sizing proportional to the change? | A tiny Ticket required extra Tickets, repeated planning, or unnecessary re-decomposition |
| Context | Was the same repository context loaded repeatedly? | Re-reading large files because no compact recovery state existed |
| Delegation | Did another agent reduce work or add coordination? | Main agent repeated delegated exploration or integration cost exceeded benefit |
| Implementation | Was work expanded beyond acceptance criteria? | Unrelated refactor or future-slice work appeared |
| Testing | Was verification proportional to risk? | Full/regression suites ran without evidence requiring escalation |
| Redaction | Was scanning repeated without a changed sensitive surface? | Identical safe scope was reclassified unnecessarily |
| Git / PR | Did branch and PR handling create avoidable cycles? | Multiple publication cycles for changes that could have been batched |
| Review | Did review repeat already-assessed evidence? | Full review reran after a bounded non-impacting fix |
| State / Docs | Is the same fact maintained in several places? | Workflow order or status copied across SKILL, README, usage, architecture, state |
| Deployment | Did deployment checks match the requested target? | Release work ran when deployment was not in scope |
| Human interaction | Did the workflow stop for unnecessary confirmation? | Agent asked permission for an already-authorized next gate |
| Automation | Was a deterministic manual step repeated? | Same command sequence or metadata update repeated across runs |

## Runtime evidence to capture

Use counts and concrete events when possible. Exact timing or token metrics are
optional because they may not be reliably available.

```text
Run / PR:
Change type:
Planning level: single-Ticket slice | multi-Ticket
Verification level: minimal | focused | regression | full
Review rounds:
Repeated stages:
Avoidable rework:
Repeated context reads:
Manual repeated steps:
User interruptions / confirmations caused by workflow:
Observed bottleneck:
```

Do not preserve raw logs here. Link to the PR or Issue when durable evidence is
needed.

## Decision rubric

Classify each candidate improvement:

| Decision | Apply when |
|---|---|
| `keep` | The step produced distinct evidence or protected a required gate |
| `simplify` | The step is useful but its instructions, inputs, or outputs are too heavy |
| `merge` | Two stages consume the same inputs and produce substantially the same decision |
| `automate` | A deterministic manual action repeats and has a safe, testable contract |
| `remove` | The step adds no distinct evidence, decision, state, or protection |
| `observe` | Evidence exists but one run is insufficient to justify a workflow change |

A single high-impact failure can justify immediate improvement. For low-impact
friction, prefer evidence from at least two runs before changing the workflow.

## Evaluation output

Keep each retrospective short:

```text
Keep: <what worked>
Redundancy: <none or the clearest duplicate/overhead>
Improve: <one highest-value reusable improvement or none>
Evidence: <specific event from the completed run>
Decision: keep | simplify | merge | automate | remove | observe
Action: none | follow-up change | report for later
```

If `Action` is `follow-up change`, that change must use the same normal
Requirement -> Plan -> Branch -> Test -> PR -> Review -> Merge lifecycle.

## Current structural baseline

These are repository-structure observations, not claims from runtime metrics.
Use future real runs to confirm or reject them.

| Candidate | Current assessment | Improvement direction |
|---|---|---|
| Macro workflow repeated across `SKILL.md`, `README.md`, usage, and architecture docs | Likely documentation redundancy and drift risk | Keep `SKILL.md` as control plane; make other docs explain details or link to one canonical flow instead of copying it |
| Branch/PR rules appear in core path, branch section, review section, and completion gates | Some repetition is useful for local context, but the same rule is stated many times | Keep one authoritative rule and shorten repeated sections to references |
| Post-delivery evaluation can itself create a documentation-only PR every run | High risk of process noise and recursive self-improvement | Evaluate every run in memory; persist only reusable findings or an approved follow-up improvement |
| `pr-review` after every PR update | Necessary single merge gate; full-range repetition after bounded fixes is wasteful | Keep one mandatory gate; let its runner default to incremental coverage after an assessed review and require explicit full escalation for high-impact or uncertain changes |
| State / Docs updates plus separate evaluation records | Potential duplicate persistence | Keep `Repo_Current_State.md` for recovery state and this file for process quality; do not duplicate ticket/backlog/status history |
| Ticket/Slice/delegation machinery | Every requirement has a Ticket; delegation remains optional | Keep the Ticket mandatory and scale only its shape: one Ticket with one Slice for small work, extra Tickets or delegation only when complexity provides evidence |

## Improvement backlog discipline

Do not turn this document into a backlog. When an improvement is actionable,
record it as the normal Issue/Ticket before implementation; a small improvement
is one Ticket with a single Slice and PR. Remove or rewrite resolved baseline
findings so this file stays a compact description of current process quality
rather than a historical archive.
