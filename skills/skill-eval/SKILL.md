---
name: skill-eval
description: "Evaluate whether a Codex skill improves real task outcomes using blind A/B comparisons, trigger/behavior/outcome evidence, and an outcome-first verdict. Use for skill effectiveness studies, not ordinary feature verification."
---

# Skill Eval

Validate skills as playbooks, not by asking an agent whether it followed them.
Use the lightest design that can answer the decision question, but preserve the
blind A/B controls whenever the claim is that a skill improves task results.

This is a Skill Playbook. Do not create runner scripts, datasets or schemas just
to use it unless the user separately requests automation.

## Evaluation layers

Use four layers. Static, Trigger and Behavior diagnose the skill; Outcome is
decisive for the verdict.

- **Static:** inspect `SKILL.md`, optional resources and `agents/openai.yaml`
  for clear trigger, scope, non-goals, safety boundaries, progressive
  disclosure, installability and contradictions. Static review can block obvious
  defects but cannot prove effectiveness.
- **Trigger:** test whether the skill is selected for the right requests and
  ignored for the wrong ones. Use positive and negative prompt sets, record each
  prompt as hit/miss/false-positive/false-negative, and summarize recall and
  precision style results.
- **Behavior:** inspect observable traces and artifacts from the task execution:
  loaded resources, commands, diffs, files, screenshots, logs and decisions.
  Agent claims are not evidence unless the underlying trace or artifact proves
  the behavior.
- **Outcome:** judge the final task result against the real acceptance criteria.
  If the outcome evidence is missing, materially worse, or not attributable to
  the skill treatment, the evaluation cannot PASS regardless of Static, Trigger
  or Behavior results.

## Blind A/B protocol

Use blind A/B evaluation for outcome claims.

1. Freeze one real task and acceptance criteria before running candidates.
2. Start baseline and treatment from the same repository state, tools,
   permissions, task context and time budget.
3. Keep the candidate model fixed when testing the skill. The baseline runs
   without the new skill; the treatment runs with the skill available under the
   same ordinary user request.
4. Do not tell candidates they are being evaluated, compared, or in an A/B
   study. Give only the normal task prompt and authorized context.
5. Prepare the judge-only rubric before reviewing outputs. Do not show it to
   candidates.
6. Anonymize and randomize outputs before judging. The judge sees labels such as
   A/B, not baseline/treatment identity, and evaluates only final outputs,
   traces and artifacts needed by the rubric.
7. Reveal identities only after scoring. Attribute differences to the skill only
   when the setup kept all other material factors equal.

If exact parity is impossible, state the deviation and use `INCONCLUSIVE` unless
the deviation cannot reasonably affect the claim being judged.

## Outcome evidence

Outcome proof depends on the task surface. Prefer direct operation of the final
artifact over indirect descriptions.

- Code changes build, tests run, and the changed behavior executes.
- UI changes are opened and operated through the user-visible surface.
- CLI changes are executed with representative commands and failure cases.
- Documentation changes are judged by the final document, not by the author's
  summary of it.
- Workflow skills are checked through traces, files, artifacts and decision
  records that show the workflow actually happened.

Record cost alongside quality: marginal tokens, time, tool calls, retries,
manual review burden and any extra setup. A skill that improves quality only by
adding disproportionate cost should not receive an unqualified PASS.

## Verdicts

- `PASS`: the treatment produces a materially better or reliably safer outcome
  than baseline, with acceptable cost and no blocking Static, Trigger or
  Behavior defect.
- `FAIL`: the treatment is worse, unsafe, materially ineffective, too costly for
  the gain, or lacks required real-artifact proof.
- `INCONCLUSIVE`: blindness, parity, sample size, trace availability or outcome
  evidence is insufficient to decide.

## Report

Use this report shape and keep raw transcripts out unless requested:

```text
SKILL EVAL
skill: <skill name and version/source>
Static: <pass/fail/inconclusive and key evidence>
Trigger: <positive/negative prompt results; recall/precision style summary>
Behavior: <observable trace/artifact evidence; no unsupported claims>
Outcome: <real artifact proof and blind A/B comparison>
Cost: <tokens/time/tool calls/retries/manual review; material differences>
Verdict: PASS | FAIL | INCONCLUSIVE
```

Report unresolved risks, parity deviations and whether the verdict is based on
one task or a broader sample.
