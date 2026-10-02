# AGENTS.md

This repository uses **zero runtime Skills**. Codex owns normal reasoning and execution directly.

Do not create, install, discover, or invoke repository Skills. There must be no root `SKILL.md` and no `skills/**/SKILL.md`.

## Native Codex responsibilities

Use Codex natively for requirement understanding, planning and decomposition, architecture, implementation, refactoring, investigation, verification and testing, delegation, coordination, integration, ordinary Git/GitHub operations, and diagram authoring.

The rules below exist only because they are repository-specific contracts or deterministic gates that Codex does not inherently know.

## GitHub Issues are the task authority

GitHub Issues are the sole authoritative development-task store.

- Every development task must have an authoritative Issue before implementation.
- Chat, PR bodies, local Markdown, TODO files, and model memory are non-authoritative views.
- If the Issue cannot be created or updated, implementation is blocked.
- A simple task may remain one Issue.
- When durable hierarchy is useful, persist one Plan Issue plus the smallest useful set of child Ticket Issues. Codex decides the decomposition natively.

### Durable Issue schema

Use exact stable markers when a persisted hierarchy is needed:

```text
<!-- codex-plan-id: <stable-kebab-slug> -->
<!-- codex-ticket-id: T0016 -->
```

Ticket IDs are repository-scoped: `T` plus four zero-padded digits. Allocate a value greater than every existing valid ticket marker and never reuse an ID.

A Plan title is:

```text
[PLAN] <short title>
```

A Plan body starts with:

```yaml
Status: planned
Branch: <type>/<plan-id>-<short-description>
Base: <base-branch>
PR: null
Tickets: [T0001]
```

A Ticket title is:

```text
[T0001] <short behavior title>
```

A Ticket body starts with:

```yaml
Plan: <canonical Plan Issue URL>
Status: planned
Dependencies: []
```

Allowed status values are `planned`, `in_progress`, `blocked`, `in_review`, and `done`.

A persisted Plan owns one implementation branch, one PR, and one merge. Child Tickets do not get independent delivery branches.

Before creating a Plan or Ticket, search open and closed Issues for the exact stable marker. Reuse one exact match; if multiple records match, stop rather than guessing.

Keep Plan Branch/Base/PR/Ticket index and child dependencies/status synchronized with repository reality. Mark records `done` only after the Plan PR is merged.

## Required task records

Every development Issue must keep these records current:

- task status and branch / PR references when applicable;
- verification evidence or a concrete reason verification was unnecessary;
- `Documentation Impact: updated | no-change` plus documents or reason;
- `Repo Current State: updated | no-change` plus document or reason.

These records are mandatory even though no Skill exists for them.

## Documentation contract

One fact -> one canonical document -> other documents link to it.

- Root `README.md` is the repository documentation router.
- Detailed documentation lives under `docs/`.
- Current verified truth belongs in `docs/Repo_Current_State.md`.
- Planned work belongs in GitHub Issues.
- Historical change information belongs in Git.
- Update an existing canonical owner instead of creating a parallel document.
- Every maintained document must be reachable from the documentation router.
- When documentation changes, keep source diagrams and required renders synchronized.
- Never hand-edit a rendered SVG to hide a source problem.
- Public rendering services must not receive sensitive or unreleased architecture.

Repository document standards live in:

- `docs/reference/doc-file-standard.md`
- `docs/reference/document-types.md`
- `docs/reference/documentation-lifecycle.md`
- `docs/reference/document-templates.md`

For every development task, record:

- `Documentation Impact: updated — <documents>`, or
- `Documentation Impact: no-change — <concrete reason>`.

## Repo Current State contract

`docs/Repo_Current_State.md` is a compact recovery snapshot of verified repository truth, not a changelog, backlog, plan, test archive, or reasoning trace.

Keep these sections:

- `Last verified`
- `Current Focus`
- `Implemented`
- `In Progress`
- `Known Issues / Failing Checks`
- `Constraints`
- `Architecture Snapshot`
- `Next`

Only write claims supported by current repository evidence such as tracked files, configuration, Git/GitHub state, or authoritative Issues. Omit or qualify unverified claims.

For every development task, record:

- `Repo Current State: updated — docs/Repo_Current_State.md`, or
- `Repo Current State: no-change — <concrete reason>`.

Update the snapshot only when repository truth materially changed.

## Staged sensitive-data gate

When staged content may contain credentials, tokens, private/internal addresses, personal identifiers, or other sensitive values, run:

```bash
python3 scripts/redaction/scan_staged.py
```

Interpret results:

- `pass` / `noop`: gate is clear.
- `findings`: block publication, sanitize, re-stage, and re-run.
- `needs_review`: block publication until the uninspectable surface is resolved.
- `error`: block publication until the scanner can run successfully.

Never print matched secret values; report only finding type, path, and line number.

If a real secret was already committed or pushed, revoke or rotate it first, then handle history separately.

## Publication policy

Codex performs Git/GitHub operations natively, but repository publication must satisfy these guards:

- publish from a non-default branch;
- required verification and applicable redaction must already pass;
- selected changes must belong to the intended task;
- commit subjects follow Conventional Commits 1.0.0;
- repository-local author/committer identity and configured GitHub account match policy;
- GitHub repository description is non-empty;
- unresolved conflicts and unsafe behind-upstream states block publication;
- every published coherent change has a pull request;
- force-push requires explicit user authorization.

Deterministic publication tools live under `scripts/publication/`.

Readiness:

```bash
python3 scripts/publication/assess_push_readiness.py --json
```

Guarded commit/push when appropriate:

```bash
python3 scripts/publication/push_if_ready.py \
  --message "type(scope): description" \
  --pathspec path/to/file \
  --execute
```

Optional managed hooks:

```bash
python3 scripts/publication/install_post_commit_hook.py --repo .
```

A successful commit or push is not equivalent to PR readiness. Stop at `PR ready` unless merge is separately authorized.

## Diagram repository rules

Diagram reasoning and authoring are native Codex work.

For PlantUML already used by repository documentation:

```bash
bash scripts/render-diagrams.sh render
bash scripts/render-diagrams.sh --check
```

Keep `.puml` and same-basename `.svg` synchronized where the documentation standard requires it.

## Hard guardrails

Never weaken security, permissions, verification, redaction, branch, publication, or release controls to complete a task.

Never commit credentials, tokens, private keys, `.env`, or other secrets.

## Completion

Finish when the user's requested outcome is satisfied, the authoritative Issue is current, required records are present, and applicable deterministic gates pass. Do not manufacture workflow stages, Skills, or artifacts for capabilities Codex already provides.
