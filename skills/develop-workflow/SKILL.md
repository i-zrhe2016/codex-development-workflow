---
name: develop-workflow
description: "Implement, fix, refactor or modify repository content for a persisted Ticket through Development Complete with focused local validation. Stops before delivery verification, publication, Issue closure and state refresh."
---

# Develop Workflow

Owns **context -> implementation -> Development Complete**.

When the user controls the overall flow, development executes only the approved
Ticket scope. It may surface the next workflow step, blockers, risks and
available choices, but must not choose new scope, re-planning, verification,
publication or merge actions for the user.

1. Load only affected files, direct dependencies, relevant tests and repository
   state. Confirm the smallest useful local validation before editing.
2. Follow the role boundary below. Keep unresolved dependencies and overlapping
   writes, shared interfaces/schemas/migrations/config, and shared test state
   sequential.
3. Where practical, use meaningful failing tests first for behavior changes,
   bugs/regressions, APIs, core logic, data processing or high risk. Validate
   docs/config/dependencies/styling/typos/simple refactors directly; no forced RED.
4. Make the minimum change satisfying Ticket acceptance; run focused checks and
   fix clear failures. Keep all work within the persisted Ticket.
5. The worker reports each completion and material checkpoint promptly; the
   coordinator integrates eligible results and immediately recomputes the
   Ready Queue. Scheduling is event-driven, with no batch barrier. Wrong design
   assumptions require re-planning, not patch expansion.

## Ticket owners and workers

These minimum execution rules apply even without `AGENTS.md`; when present, it
owns the full scheduling policy.

- Main agent: own requirements, dependencies, scheduling, integration, stage
  gates and final judgment. Directly dispatch one fresh implementation owner
  per Ticket, including docs/config/test; also dispatch
  independent verifiers and fresh repair implementers.
- Ticket owner: retain context across the Ticket and local repairs. Validate
  changes and report at integration and Development Complete checkpoints.
  Owners never spawn agents or perform independent
  acceptance verification.
- Optional module assistants may work only to fixed interfaces with
  non-overlapping file and shared-test-state ownership. Parallel writes require
  isolated detached worktrees or complete returned patches for main integration.
  Capture staged and unstaged additions, modifications, deletions, renames and
  binary changes from the full worker worktree, including changes without
  commits, while protecting its dirty baseline. A dependent Ticket may prepare
  read-only. Delivery writes become eligible only after each prerequisite's
  work is integrated on the Plan branch, a fresh independent verifier passes
  that fixed integrated snapshot, and PASS evidence is saved to its Issue. A
  failed Issue write never unlocks work.
- Keep a live Ready Queue over the validated Ticket dependency DAG, including
  runnable integration, verification and durable evidence-write work as well as
  owner work. Recompute on
  each individual completion, material checkpoint, failure, dependency change
  or integration result; never wait for a batch barrier. Prioritize critical-path
  tasks and tasks that clear downstream gates, using relative effort estimates
  where known and dependency depth otherwise; refresh as progress arrives and
  use FIFO ties to prevent starvation. This
  changes scheduling order only; it adds no Ticket, status or acceptance gate.
  Count the active main agent and all workers against actual host capacity.
  The repository sets no fixed concurrency cap or total/lifetime quota; a direct
  dispatch needs one free slot for its worker. Queue when no slot is free. No
  leaf-slot reservation applies. Workers never spawn agents.
- Use the host's native worker creation, communication and completion/wait
  controls to dispatch, receive checkpoints and requeue work; do not add a local
  scheduler, service or persistent state store for this policy.
- Before dispatch and integration, check actual overlap in paths, interfaces,
  schemas, migrations, configuration, fixtures, databases, ports, caches,
  service instances and other shared test resources. Serialize conflicting
  writes and shared runtime state. Never create Ticket branches or switch a
  directory used by active workers. Maintain the Plan's **logical baseline**:
  its initial intended contents plus only coordinator-recorded, accepted
  integrations. Record a content fingerprint when establishing that baseline
  and after each integration. Before snapshotting or integrating, compare the
  actual Plan contents with the last recorded fingerprint; preserve and
  reconcile any unexplained drift, including user edits, before proceeding. A
  Git commit or Plan HEAD alone is not this baseline: accepted prerequisite work
  may be uncommitted.

  To prepare a dependent owner, materialize the current accepted Plan contents
  `S` in a new isolated detached worktree at Plan HEAD, without making a commit.
  First ensure the Plan matches its recorded logical baseline. In the Plan
  worktree, use a temporary index to build and retain a binary delta from HEAD;
  retain this patch outside the worktree until worker output is integrated so
  `S` can be reconstructed even if its unreferenced tree object is pruned. For
  example (paths and environment setup are per task):

  ```sh
  # Plan worktree P; preserve/hash the primary index file before and after.
  GIT_INDEX_FILE="$tmp/plan.index" git -C "$P" read-tree HEAD
  GIT_INDEX_FILE="$tmp/plan.index" git -C "$P" add -A
  S=$(GIT_INDEX_FILE="$tmp/plan.index" git -C "$P" write-tree)
  GIT_INDEX_FILE="$tmp/plan.index" git -C "$P" diff --cached --binary --full-index HEAD > "$tmp/S.patch"

  git worktree add --detach "$W" "$(git -C "$P" rev-parse HEAD)"
  git -C "$W" apply --binary "$tmp/S.patch"
  GIT_INDEX_FILE="$tmp/worker-baseline.index" git -C "$W" read-tree HEAD
  GIT_INDEX_FILE="$tmp/worker-baseline.index" git -C "$W" add -A
  test "$(GIT_INDEX_FILE="$tmp/worker-baseline.index" git -C "$W" write-tree)" = "$S" || exit 1
  ```

  The equality check proves the worker starts from accepted contents `S`;
  record `S`, the retained patch, the logical-baseline fingerprint and the
  relevant runtime/configuration fingerprint as its exact base. The primary
  index and shared Git configuration remain untouched. The worker's ordinary
  status relative to HEAD will include inherited baseline changes; do not treat
  those as worker output. At capture, seed a fresh alternate index from `S`,
  stage the full worker contents, and compare only the resulting delta against
  `S` to enforce declared path ownership. For example:

  ```sh
  GIT_INDEX_FILE="$tmp/worker-delta.index" git -C "$W" read-tree "$S"
  GIT_INDEX_FILE="$tmp/worker-delta.index" git -C "$W" add -A
  GIT_INDEX_FILE="$tmp/worker-delta.index" git -C "$W" diff --cached --binary --full-index --find-renames "$S" > "$tmp/worker.patch"
  ```

  This captures only the owner's additions, modifications, deletions, renames
  and binary changes since `S`. Refuse capture if worker contents differ from
  recorded `S` for paths outside ownership, or if the Plan has drifted from its
  recorded baseline; inherited accepted content is not a dirty-baseline
  conflict. Preflight the worker delta in a scratch checkout/materialization of
  the CURRENT integrated Plan snapshot, including earlier uncommitted
  integrated Tickets; resolve conflicts there and recheck the full Plan
  status/content fingerprint immediately before applying. If it changed,
  reconcile and repeat preflight against the new snapshot. Apply while retaining
  a recoverable checkpoint and all worker outputs. Roll back only this
  integration attempt on failure. Identify the resulting snapshot by building a
  fresh alternate index from the intended integrated contents: seed from the
  Plan HEAD with `git read-tree`, stage the full intended tree with `git add -A`,
  then use `git write-tree`. This captures staged, unstaged, untracked and
  deleted files; never hash the stale primary index alone. Pair the tree hash
  with a non-secret runtime/environment fingerprint and hold both fixed
  throughout independent verification. Use per-command configuration or
  environment when line-ending/filter behavior needs control; never change
  shared worktree config, and include effective `.gitattributes` and filter/EOL
  settings in snapshot identity when relevant. Isolate databases, ports, caches
  and service instances for concurrent checks. A later change to a verified
  surface invalidates that Ticket and every dependent descendant. Stop active
  descendants before they consume a stale base, or let their isolated work
  finish and reconcile it against the new integrated base before any
  integration. Recovery reconciles actual workspace contents, durable Issue
  evidence and repair counts; failed required Issue persistence blocks the
  affected Ready Queue entries.
- Compare one-, two- and three-owner scheduling only with matched Plan scope,
  acceptance criteria, tools, permissions, host and verification procedure.
  Measure elapsed time from the authorized request to every Ticket independently
  passing on the integrated snapshot; report rework, failures and quality gates
  alongside elapsed time. These are comparison conditions, not a speedup claim
  or a reason to exceed actual host capacity.

- Codex main agent, before dispatch: identify **this active entrypoint's** path
  from the explicit user-selected/dispatched path first, otherwise its loaded
  catalog location (resolve aliases). Project `.agents/skills` copies are valid
  installed Skills. Read only the catalog-discovered
  `codex-development-workflow/SKILL.md` sibling under that same installation root
  (the parent of this Skill directory). Duplicate names do not authorize
  switching to another, possibly stale, global copy. Apply that root's **Codex
  worker model routing** policy to each direct dispatch. Ambiguous active-copy
  association, missing/unreadable sibling, absent routing section or unsupported
  settings blocks dispatch. Inspect named-role settings only when selecting a
  role; do not explore generic/global defaults. Dispatched workers do not route
  models. Claude selection is unchanged.
- For every Codex dispatch, explicitly request the selected model and effort
  with `fork_turns="none"`; other hosts need equivalent fresh independent
  workers. If unavailable, report BLOCKED without main-agent fallback. Requested
  settings are dispatch metadata, not proof of runtime identity; report observed
  identity only when exposed.
- Keep the main agent long-lived and thin. Hand off only role, current
  Ticket goal, scope/non-goals, dependencies and acceptance, files and
  ownership, Plan branch/base, verified prerequisites and validation summary.
  Do not include parent conversation or unrelated history. Replace interrupted
  workers from verified checkpoints and preserve failure evidence/counts.
- Serialize dependencies and conflicting/shared-state work. Verification
  failures return to implementation,
  followed by a new verifier for affected functionality. Preserve flaky-test
  evidence and the Test Quality Gate.
- The initial implementation failure does not count as a repair round. After
  two consecutive failed same-problem repair rounds, the main agent diagnoses
  and replans. Development and repair implementation use Sol/low from the start.
  Final Plan acceptance is a separate fresh verifier, except
  one NEW verifier may satisfy Ticket and final gates for a one-Ticket Plan only
  when full scope, artifact/version, configuration and deployment surface match
  exactly. The main agent owns the Test Quality Gate and stage decision.
- Record durable Ticket Issue checkpoints at each integration, Development
  Complete, acceptance failures, and pause/retirement. A required Issue write
  failure is BLOCKED. Do not create per-step acknowledgements or gates.

**Development Complete:** acceptance is implemented and local validation passes.
Report Ticket, changed files, commands/results, unresolved risks and follow-up work.
It does not trigger commit, push, PR creation/update or merge. After independent
verification, local verified functionality may stop normally pending the user's
publication decision; that wait is not BLOCKED. New scope in an unmerged Plan
requires `plan-to-ticket`'s Plan/Ticket updates before implementation edits.

`verify-workflow` owns delivery verification breadth; publish/integrate own
commit/push/PR/merge, Issue closure and state refresh. No post-delivery evaluation,
unrelated requirements, refactors, formatting sweeps or dependency upgrades.
