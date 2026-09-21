# Codex Development Workflow

An adaptive, main-agent-led development workflow for Codex and Claude Code with
optional bounded delegation, post-delivery process evaluation, bounded
self-improvement, and all required specialist skills managed in this repository.

```text
Requirement
  -> Understand repo
  -> Plan
  -> Record Plan + Tickets + Slices
  -> Create Plan branch
  -> Implement all Plan Tickets
  -> Test
  -> Documentation impact check
  -> Redaction scan if applicable
  -> Commit
  -> Push branch
  -> Create / Update PR
  -> Merge the Plan PR once
  -> Delete branch
  -> Update main
  -> Close Plan + Tickets
  -> Update State / Docs
  -> If separately authorized: external release handoff (outside this workflow)
  -> Evaluate workflow
  -> Reusable improvement? -> one bounded follow-up change or finish
```

An external deployment handoff is outside this repository's workflow and does
not invoke a bundled deployment Skill. When separately authorized, the Plan
owner hands the target project's release owner the immutable artifact and
source commit, target environment and authorization, and the documented
deployment, health-check, and rollback instructions. The external release
owner performs and verifies the rollout or rollback. Completion evidence is
the external release result or incident link recorded with the delivery.

The macro workflow controls architecture and scope. Every requirement is
recorded as exactly one GitHub Issue Plan with one or more child Ticket Issues
before branch work starts, so a single-behavior requirement is one Plan with one
Ticket and one implicit Slice while larger requirements add Tickets and Slices
under that Plan. The Plan owns the one branch, PR, and merge. All Tickets and
Slices share that branch; Ticket dependencies remain separate from Slice
dependencies, and the PR head and base must match the Plan metadata.
Test level may vary with risk, but delivery does not: Docs, Code, Tests,
Config, Refactor, Bugfix, Feature, Dependency, and CI/CD changes all require a
branch, commit, push, PR, and merge.

After delivery, the main agent performs one lightweight workflow evaluation.
It looks for reusable evidence such as avoidable rework, weak assumptions,
unnecessary context loading, disproportionate validation, repeated manual work,
or unclear workflow instructions. It records one highest-value improvement at
most. A safe, low-risk improvement may start automatically as one separate
follow-up change through the same branch/PR lifecycle; broad policy,
security, permission, release, or scope changes are reported instead of
self-applied. The follow-up cannot recursively create another automatic
self-improvement change.

Verification is bounded by an explicit level (`minimal`, `focused`,
`regression`, or `full`), but PASS is controlled by a risk-aware Test
Quality Gate. The default is focused validation; each acceptance criterion maps
to executed evidence, and applicable boundary, negative, integration,
regression, property/fuzz, mutation, browser, or isolation dimensions must pass
or be explicitly N/A with reason. Coverage remains diagnostic rather than a
quality target, and an unexplained flaky FAIL cannot become PASS through retry. The main agent owns requirements, architecture,
decomposition, integration, evaluation, and final judgment; bounded exploration,
Slice implementation, and testing may be delegated when useful, with the host
selecting the subagent.

## Optional project-scoped delegation

The project configuration keeps multi-agent support deliberately small. Each
host reads its own agent directory, and each host selects the subagent from the
agent's own `description`:

- Codex reads `.codex/config.toml` (subagents enabled, spawned-agent threads
  capped at three excluding the main thread) and `.codex/agents/`.
- Claude Code reads `.claude/agents/`.
Delegation remains optional and the safety rules live in
[`AGENTS.md`](AGENTS.md#multi-agent-delegation).

## Architecture

Detailed views: [component responsibilities source](docs/diagrams/components.puml),
[Plan/Ticket lifecycle and nested loops](docs/architecture/overview.md#ticket-to-slice-hierarchy), and the
[architecture guide](docs/architecture/overview.md).

See the [architecture overview](docs/architecture/overview.md) for the unified
branch/PR lifecycle, Ticket/Slice decomposition, bounded verification, recovery state, redaction, post-delivery evaluation, bounded
self-improvement, and package boundaries.

## Install from this repository

```bash
git clone https://github.com/i-zrhe2016/codex-development-workflow.git
cd codex-development-workflow
bash scripts/install-all.sh
```

The installer copies the local bundles under `skills/`; it does not clone
specialist repositories. Select the host with `--target codex` (the default) or
`--target claude`, and repeat that target when updating — `--update` without
`--target` always updates the Codex destination. See the
[installation and update guide](docs/deployment/installation.md) for the
destination of each target.

Update existing installations:

```bash
bash scripts/install-all.sh --update
```

Restart the host after installation so it discovers the new skill directories.

## Installed skills

- `codex-development-workflow`
- `context-efficiency`
- `plan-to-ticket`
- `test-workflow`
- `repo-current-state`
- `repo-documentation`
- `data-document-redaction`
- `github-push-when-ready`

`plan-to-ticket` persists exactly one Plan and every child Ticket to GitHub
Issues before the Plan branch starts. GitHub Issues are the sole durable
Plan/Ticket authority; chat output and `Repo_Current_State.md` provide links and
recovery context, not a parallel backlog. Every requirement has one Plan, and a
Plan may contain one or more Tickets; the branch/PR/merge gate is mandatory once
per Plan, never once per Ticket.

## Skill documentation

Runtime skill sources live under `skills/` and are installed by
[`scripts/install-all.sh`](scripts/install-all.sh). Specialist documentation
is grouped under
[`docs/skills/`](docs/skills/); operational references remain beside the
relevant bundle.

| Skill | Runtime source | Documentation |
|---|---|---|
| `codex-development-workflow` | [`SKILL.md`](SKILL.md) | [Workflow usage](docs/workflow/usage.md) · [Architecture](docs/architecture/overview.md) |
| `context-efficiency` | [`skills/context-efficiency/`](skills/context-efficiency/) | [Skill documentation](docs/skills/context-efficiency/README.md) |
| `plan-to-ticket` | [`skills/plan-to-ticket/`](skills/plan-to-ticket/) | [Skill README](docs/skills/plan-to-ticket/README.md) · [Architecture](docs/skills/plan-to-ticket/architecture.md) |
| `test-workflow` | [`skills/test-workflow/`](skills/test-workflow/) | [Skill README](docs/skills/test-workflow/README.md) · [Architecture](docs/skills/test-workflow/architecture.md) · [Usage](docs/skills/test-workflow/usage.md) |
| `repo-current-state` | [`skills/repo-current-state/`](skills/repo-current-state/) | [Skill README](docs/skills/repo-current-state/README.md) · [Architecture](docs/skills/repo-current-state/architecture.md) |
| `repo-documentation` | [`skills/repo-documentation/`](skills/repo-documentation/) | [Skill documentation](docs/skills/repo-documentation/README.md) |
| `data-document-redaction` | [`skills/data-document-redaction/`](skills/data-document-redaction/) | [Skill documentation](docs/skills/data-document-redaction/README.md) |
| `github-push-when-ready` | [`skills/github-push-when-ready/`](skills/github-push-when-ready/) | [Skill documentation](docs/skills/github-push-when-ready/README.md) |


## Documentation

- [Architecture overview](docs/architecture/overview.md)
- [Installation and update guide](docs/deployment/installation.md)
- [Workflow usage guide](docs/workflow/usage.md)
- [Redaction workflow](docs/workflow/redaction.md)
- [Workflow process evaluation](docs/workflow/process-evaluation.md)
- [Managed skill source map](references/skill-map.md)
