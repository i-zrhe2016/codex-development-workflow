# Codex Development Workflow

A zero-Skill repository policy for Codex.

Codex handles software-engineering work natively. This repository does not install or expose runtime Skills. Repository-specific requirements live in `AGENTS.md`; deterministic checks live under `scripts/`.

## Runtime model

```text
User goal
  -> Codex native reasoning/execution
  -> AGENTS.md repository contracts
  -> deterministic scripts when a hard check is needed
  -> completion
```

Native Codex work includes planning, decomposition, architecture, implementation, refactoring, testing, delegation, integration, ordinary Git/GitHub operations, and diagram authoring.

## Repository-specific contracts

`AGENTS.md` owns:

- GitHub Issues as the sole development-task authority;
- optional durable Plan/Ticket Issue schema and lifecycle;
- mandatory verification / Documentation Impact / Repo Current State records;
- canonical documentation ownership;
- `docs/Repo_Current_State.md` shape and reconciliation;
- staged sensitive-data gate;
- publication identity / branch / commit / PR policy;
- diagram source/render synchronization rules.

## Deterministic tooling

Sensitive-data scan:

```bash
python3 scripts/redaction/scan_staged.py
```

Publication readiness:

```bash
python3 scripts/publication/assess_push_readiness.py --json
```

Guarded commit/push:

```bash
python3 scripts/publication/push_if_ready.py \
  --message "type(scope): description" \
  --pathspec path/to/file \
  --execute
```

Diagram rendering:

```bash
bash scripts/render-diagrams.sh render
bash scripts/render-diagrams.sh --check
```

## No Skill installation

There is no Skill installer.

To remove bundles installed by older versions of this repository:

```bash
bash scripts/retire-skills.sh
bash scripts/retire-skills.sh --target claude
```

Only directories carrying this repository's ownership marker are removed automatically; unrelated or unverified directories are preserved.

## Documentation

- [Repository policy](AGENTS.md)
- [Architecture](docs/architecture/overview.md)
- [Migration / retirement](docs/deployment/installation.md)
- [Repository current state](docs/Repo_Current_State.md)
- [Documentation file standard](docs/reference/doc-file-standard.md)
