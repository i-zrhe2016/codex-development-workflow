# Architecture Overview

## Scope

This project is a distributable Codex skill package. It does not run a
long-lived service or own application data. Its responsibilities are limited
to:

1. describing the gated development workflow;
2. mapping the workflow to specialist skills; and
3. installing those skills into the local Codex skills directory.

The runtime is Codex. The GitHub repositories listed in
[`references/skill-map.md`](../../references/skill-map.md) are the external
sources from which the installer obtains the specialist skills.

## Components

| Component | Location | Responsibility |
|---|---|---|
| Workflow orchestrator | [`SKILL.md`](../../SKILL.md) | Defines the ordered lifecycle and the gates between planning, implementation, verification, review, state reconciliation, and publication. |
| Installer | [`scripts/install-all.sh`](../../scripts/install-all.sh) | Clones each source repository and copies the selected skill folder into the destination directory. |
| Skill source map | [`references/skill-map.md`](../../references/skill-map.md) | Documents the source repository, source path, and installed skill name for each specialist skill. |
| Package metadata | [`agents/openai.yaml`](../../agents/openai.yaml) | Supplies the display name and short description used by the package metadata surface. |
| Local skill directory | `${CODEX_HOME:-$HOME/.codex}/skills` | Stores the installed orchestrator and specialist skill folders discovered by Codex. |

## Development process diagram

The primary architecture view is the gated development process rather than the
installer implementation. The editable source is
[`architecture.puml`](../diagrams/architecture.puml); the rendered version is
embedded below and in the root README.

![Codex Development Workflow development process](../diagrams/architecture.svg)

The main path is `Context → Plan / Ticket → Implement → Test → Review → Repo
State → Commit / Push`. Frontend browser verification is conditional, and test
or review failures loop back to implementation before publication.

## Installation flow

1. A maintainer or developer runs `scripts/install-all.sh`.
2. The installer checks for `git`, `mktemp`, and `tar`, then creates the
   destination directory and a temporary workspace.
3. For each entry in the install list, the installer performs a shallow clone
   of the configured GitHub repository.
4. The requested source path is copied into the destination skill directory.
5. Existing destinations are skipped by default. With `--update`, an existing
   destination is removed before the replacement is copied.
6. Codex is restarted so it can discover the installed skills.

The installer currently keeps its install list in the script itself, while the
skill map documents the same mapping for readers. Changes to either list must
be checked against the other.

## Runtime flow

After installation, Codex loads `codex-development-workflow/SKILL.md` and uses
it as the coordinator. The coordinator invokes the specialist skills at the
appropriate gates; it does not reimplement their detailed procedures. The
frontend browser test is conditional and is used only when the change includes
frontend interaction behavior.

## Boundaries and invariants

- The package provides workflow guidance and installation; it does not manage
  project source code, deployment infrastructure, or application databases.
- The installer depends on network access to GitHub and installs the current
  default branch contents; it does not pin a commit or verify a signature.
- Installation is filesystem-scoped. The destination can be changed with
  `--dest PATH`.
- The orchestrator advances only after the relevant test and review gates pass,
  or an explicit blocker is recorded.
- A repository-state document is required by the workflow when the target
  repository has state documentation; the orchestrator does not create a
  universal state format for every target repository.
