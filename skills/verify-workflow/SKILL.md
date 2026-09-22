---
name: verify-workflow
description: "Decide WHEN to verify. Select the verification scope and level for a change, invoke the test-workflow capability, and return its conclusion. Use when the request is to verify, validate, check acceptance criteria, or confirm a branch before publication. It does not modify code and does not restate the quality gate."
---

# Verify Workflow

Thin stage workflow for the **trigger -> verification scope -> conclusion**
transition. It decides *when* verification runs and *how much* of it the change
warrants; the verification procedure and its quality gate belong to the
`test-workflow` capability.

## Triggers

Invoke this stage when:

- a Slice or Ticket has reached Development Complete and its acceptance must be
  proven before publication;
- the user asks to verify, validate, or confirm a branch, a change, or an
  acceptance criterion;
- a regression, an incident, or a review finding needs confirmation;
- a pull request is about to be declared ready.

Do not invoke it for exploratory inspection during implementation; that local
feedback belongs to `develop-workflow`.

## Responsibility

- Decide whether verification is warranted, and record the reason when it is
  skipped.
- Establish what is being verified: a Slice, a Ticket, a branch, a Plan, or a
  single acceptance criterion.
- Choose one bounded level — `minimal`, `focused`, `regression`, or `full` —
  from the change's behavior and risk, not from habit.
- Invoke `test-workflow` and let it own the requirement-to-acceptance-to-test
  matrix, the mandatory test dimensions, the RED/GREEN loop, the flaky and
  isolation policy, and the Test Quality Gate.
- For a Ticket, branch, or Plan conclusion, verify that every originating
  Requirement ID is covered by acceptance criteria and executed evidence; a
  green test suite with an uncovered Requirement is not sufficient for PASS.
- When verification contains independent bounded checks, the main agent may
  schedule them adaptively under `AGENTS.md`. Parallel evidence gathering is
  allowed only when the checks do not interfere with one another; the main
  agent still synthesizes the evidence and owns the final conclusion.
- Return the conclusion with its evidence. Escalate the level only when the
  evidence, the acceptance criteria, or an explicit requirement justify it.

## Result

Return exactly one conclusion:

- `PASS` — every originating Requirement ID is covered by executed evidence,
  and the selected level and every applicable mandatory dimension passed;
- `FAIL` — a check failed, reported with the failing check and its evidence;
- `BLOCKED` — verification could not run, reported with the reason.

Return the result and stop.

## Not responsible for

- modifying code, tests, configuration, or documentation so a check passes —
  return `FAIL` to `develop-workflow` instead;
- duplicating, restating, or relaxing the quality gate;
- letting a subagent advance the workflow, publish, merge, or replace the main
  agent's PASS / FAIL / BLOCKED judgment;
- committing, pushing, opening a pull request, or merging;
- closing Issues or updating repository state.
