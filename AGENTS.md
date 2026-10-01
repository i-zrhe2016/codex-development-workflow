# AGENTS.md

Repository-wide engineering principles and hard guardrails. Detailed procedures live in capability Skills.

## Principles

Priority: Correctness -> Simplicity -> Architecture Clarity -> Maintainability -> Extensibility

- Prefer the simplest necessary and maintainable solution.
- Understand affected architecture before non-trivial changes.
- Reuse existing capabilities and conventions before adding abstractions.
- Fix root causes instead of hiding them with process or code complexity.
- Keep scope bounded to the user's goal.

## Capability model

There is no mandatory stage workflow.

The model decides whether a capability is useful, when to invoke it, which capability is the most specific match, and how to compose multiple capabilities when their independent triggers apply. A capability may be skipped when it is unnecessary, redundant, or its outcome is already satisfied by stronger evidence.

Use native model reasoning for ordinary planning, implementation, investigation, integration, and coordination. Do not invoke a capability merely because it exists.

## GitHub Issues task authority

GitHub Issues are the sole authoritative source for repository development tasks.

- Before implementation begins, every development task must exist as an Issue in the target repository.
- Chat plans, PR bodies, local Markdown, TODO files, and model memory may summarize or link to a task, but they must not become a parallel backlog or task authority.
- Small work may use one Issue directly. Complex or dependency-heavy work may use plan-to-ticket to create a Plan Issue and child Ticket Issues.
- Branch, PR, acceptance evidence, blockers, and completion status must be reflected back to the authoritative Issue.
- If GitHub Issues are unavailable or unwritable, implementation is blocked; do not silently fall back to another task store.

Available capabilities:
- plan-to-ticket: persisted Plan / Ticket / Slice contracts.
- test-quality: risk-aware verification and the Test Quality Gate.
- repo-documentation: documentation ownership, impact, and lifecycle.
- repo-current-state: verified repository-state snapshot.
- data-document-redaction: staged sensitive-data scan.
- github-publish: guarded Conventional Commit, push, and pull-request publication.
- plantuml: maintainable engineering diagrams.

## Non-skippable records

Capability invocation is optional; record obligations are not.

For every development task, keep these records current in the authoritative GitHub Issue:
- task status and delivery references (branch / PR when applicable);
- verification evidence or the explicit reason structured verification was not required;
- Documentation Impact: documents updated, or `no-change` with a concrete reason;
- Repo Current State: snapshot updated, or `no-change` with a concrete reason.

The model may satisfy these obligations directly or through a capability Skill, but it may not omit them.

## Hard guardrails

Before publishing repository changes:
- required verification must have sufficient evidence;
- applicable sensitive-data checks must pass;
- documentation impact must be considered;
- the target repository's branch and PR policy must be respected.

Never weaken security, permission, branch, verification, or release controls merely to complete a task.
Never commit credentials, tokens, private keys, .env, or other secrets.

## Planning and persistence

Every development task already has an authoritative GitHub Issue. Use plan-to-ticket only when that Issue needs durable Plan / Ticket / Slice decomposition because the work is complex, dependency-heavy, resumable, or explicitly requested.

A persisted Plan owns one implementation branch, one pull request, and one merge. Tickets and Slices are decomposition boundaries, not independent delivery branches.

## Verification

The model decides when verification is warranted from changed behavior, acceptance criteria, and risk. When structured evidence is needed, use test-quality.

A green focused test is not automatically PASS. Applicable risk dimensions must pass or have a concrete N/A reason. Retry does not convert an unexplained flaky failure into PASS. Coverage is diagnostic evidence, not a quality target.

## Publication

When committing, pushing, or opening a pull request, use github-publish. Before the commit, invoke data-document-redaction when staged content has a sensitive surface. Run repo-documentation when the change may affect documented behavior, architecture, interfaces, configuration, operations, or diagrams.

## Delegation

The model may execute work directly or delegate bounded independent work. Prefer the smallest useful execution topology. Keep dependent or overlapping writes sequential. The main agent owns integration and final judgment.

## Documentation

Keep README.md as the project introduction and documentation index. Put detailed documentation under docs/. Maintain one canonical owner per fact and link instead of duplicating.
