---
name: verify-workflow
description: "Select and run delivery verification for a Slice, Ticket, branch, Plan, or acceptance criterion. Use when asked to verify/validate a change or before publication. Choose a bounded verification level, invoke test-workflow, return PASS/FAIL/BLOCKED, and do not modify code."
---

# Verify Workflow

Decide the verification scope and level, then delegate the procedure to `test-workflow`.

1. Identify what is being verified and why.
2. Choose `minimal`, `focused`, `regression`, or `full` from behavior/risk.
3. Invoke `test-workflow`; it owns the acceptance matrix, risk dimensions, advanced test paths, flaky policy, and Test Quality Gate.
4. Return exactly one conclusion with evidence:
   - `PASS`: selected level and all applicable mandatory dimensions passed.
   - `FAIL`: required evidence failed.
   - `BLOCKED`: verification could not run.
5. Stop.

Independent non-interfering checks may be scheduled under `AGENTS.md`, but the main agent owns the final conclusion.

Do not patch code/tests/docs to force a pass, duplicate/relax the quality gate, publish, merge, close Issues, or update repository state from this stage.
