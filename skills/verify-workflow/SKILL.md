---
name: verify-workflow
description: "Verify acceptance, regressions, incidents, review findings or branch/PR readiness. Select scope and level, invoke test-workflow and return PASS/FAIL/BLOCKED; never modify code or duplicate its quality gate."
---

# Verify Workflow

Owns **trigger -> verification scope -> conclusion**; `test-workflow` owns
procedure and Test Quality Gate.

Invoke for Development Complete acceptance before publication, explicit
verification, regression/incident/review confirmation, or PR readiness. Exploratory
implementation feedback belongs to `develop-workflow`.

1. Establish whether verification is warranted (record any skip reason), and
   scope: Slice, Ticket, branch, Plan or single criterion.
2. Choose `minimal`, `focused`, `regression` or `full` from behavior/risk.
3. Invoke `test-workflow` for acceptance-to-test matrix, mandatory dimensions,
   RED/GREEN, flaky/isolation policy and quality gate. Do not restate/relax it.
4. Under `AGENTS.md`, independent checks may gather evidence concurrently only
   without interference; the main agent synthesizes and judges it. Escalate
   breadth only for evidence, acceptance or explicit requirements.

Return exactly one conclusion with evidence, then stop:

- `PASS`: selected level and all applicable mandatory dimensions passed.
- `FAIL`: identify failing check/evidence; return fixes to `develop-workflow`.
- `BLOCKED`: checks could not run; explain why.

No code/test/config/docs edits to pass checks, commit/push/PR/merge, Issue closure
or state updates. Subagents cannot advance stages or replace main-agent judgment.
