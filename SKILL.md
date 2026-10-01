---
name: codex-development-workflow
description: "Thin repository policy for Codex and Claude Code. Native model capabilities handle planning, implementation, verification, delegation, Git/GitHub operations, and diagram authoring. Load a repository Skill only for durable repository-specific contracts, deterministic tooling, or hard publication gates."
---

# Repository Policy

Codex is the control plane. Do not reproduce native model behavior inside Skills.

## Active repository capabilities

- `github-issue-persistence` — persist repository task hierarchy and lifecycle metadata in GitHub Issues.
- `repo-documentation` — enforce canonical documentation ownership and repository document conventions.
- `repo-current-state` — maintain the compact `docs/Repo_Current_State.md` snapshot contract.
- `data-document-redaction` — run the deterministic staged sensitive-data gate.
- `github-publish` — enforce repository-specific publication identity, commit, branch, and PR guards.

Everything else stays native to Codex, including requirement understanding, planning and decomposition, architecture, coding, refactoring, testing strategy and execution, delegation, integration, ordinary Git/GitHub use, and diagram design.

## Task authority

GitHub Issues are the sole authoritative development-task store for this repository policy.

Before implementation, the task must have an authoritative Issue. Chat, PR bodies, local Markdown, and model memory may summarize or link to it but must not become a parallel backlog.

Use `github-issue-persistence` only when repository-specific Issue hierarchy, stable IDs, or lifecycle metadata must be created or reconciled. Do not load it merely to plan.

## Required Issue records

For every development task, keep these records current in the authoritative Issue:

- current status and branch / PR references when applicable;
- verification evidence, or a concrete reason verification was unnecessary;
- `Documentation Impact: updated | no-change` plus documents or reason;
- `Repo Current State: updated | no-change` plus document or reason.

These are policy records, not reasons to create extra workflow Skills.

## Publication guardrails

Before publication:

- required verification evidence must be sufficient;
- applicable staged redaction must pass;
- documentation impact must be recorded;
- repository branch, identity, commit, and PR policy must pass.

Never weaken security, permissions, verification, redaction, branch, or release controls for convenience.

## Completion

Finish when the requested outcome is satisfied, required Issue records are current, and applicable repository-specific gates pass. Do not manufacture stages, artifacts, or Skill calls for capabilities Codex already provides.
