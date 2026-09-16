---
name: auto-deploy
description: Safely plan, configure, execute, verify, and roll back automatic deployments using a repository's existing CI/CD or deployment contract. Use when asked to deploy, release, wire deployment automation, or inspect a failed deployment; do not invent cloud resources or credentials when the target environment is unspecified.
---

# Automatic Deployment

Use this skill for the deployment boundary. It coordinates release intent,
existing automation, preflight validation, bounded observation, health checks,
and rollback. It does not own an application's infrastructure, invent a cloud
provider, or replace the repository's test and publication gates.

## Mandatory target security preflight

Run this gate for every target designated `tailscale-hardened`; service
publication requires that designation. A target without a designation is
ineligible. A local or development target may skip this gate only when the
deployment contract explicitly records that it is non-publishing and no
shared service will be exposed.

The security preflight is read-only. Run it on the target before any SSH,
firewall, HTTP listener, access-catalog, or deployment mutation. A failed or
ambiguous check is a refusal; do not continue with a best-effort deployment.
For `verify` on a `tailscale-hardened` target, after the approved immutable
node ID is known and before resolving or using the target address or making
the first target read, acquire the read-only observation lease through the
independent lock authority. Hold it through target identity, release, catalog,
health, smoke, and final-boundary reads, and release it on every success,
refusal, timeout, or failure path. If acquisition or retirement cannot be
verified, mark verification `blocked` and do not inspect or mutate the target.
Before opening the bootstrap session, resolve the approved immutable node ID
through an authenticated Tailscale control-plane status/API lookup or the
approved tailnet DNS name. Use only the resulting Tailscale address; never use
an address supplied by the caller. If the selected resolution source is
unavailable, stop before connecting; an unselected alternative source does not
have to be available. Before opening any credential-bearing bootstrap session,
use the selected authenticated source plus current Tailscale peer status to
verify that the resolved address belongs to the approved node ID and that the
route uses the approved Tailscale interface and peer policy. If the peer or
route cannot be verified, stop before connecting. Connect only to the resolved
address for the read-only bootstrap. After connecting, verify that the
target's local Tailscale status maps back to the same node ID and attests the
resolved address. If that attestation fails, stop immediately, make no
mutation, and use the lock cleanup path below. An initial session to the
approved Tailscale address is allowed solely as a read-only bootstrap for this
preflight. It may inspect status and listeners but must not change SSH,
firewall, HTTP, catalog, or deployment state. If that session is unavailable,
use a concrete approved non-SSH management channel; a public SSH bootstrap is
never permitted.
For `execute` or an explicitly authorized `rollback`, acquire an exclusive
target-scoped lock keyed by the approved immutable Tailscale node ID before
that bootstrap. Hold it through target hardening, deployment, catalog
publication, final boundary verification, and recovery. For `verify`, use only
a read-only observation lease that cannot authorize mutation, release it after
the checks, and never acquire or reuse the mutating target lock or hardening
restore. The observation authority must atomically refuse the lease while a
mutating target lock, deployment generation, or hardening restore is active,
and must prevent a mutating lease from being acquired until observation ends.
If that mutual exclusion cannot be verified, mark verification `blocked` and
do not inspect or mutate the target.
The lock must be a bounded renewable lease with a heartbeat and a fencing
token or generation. Every hardening, deployment, catalog, and recovery
mutation must go through a mutation authority that atomically verifies the
current owner, unexpired lease, and fencing value as part of accepting the
mutation and rejects an old or revoked generation. A separate pre-check before
a normal command is insufficient. If the mutation authority cannot enforce
that atomic check, refuse the deployment. If the heartbeat, renewal, or
fencing check fails, stop new mutations and invoke the armed recovery before
its lease expires; never continue under an uncertain lock. The independent
recovery owner must use the independent lock authority
to revoke the lost generation, obtain a new recovery-only fencing generation,
and verify that the old generation is rejected before any restore mutation.
If that handoff cannot be issued and verified while recovery is valid, mark
the target `blocked` and hand it to the out-of-band owner; never mutate with a
stale token. Refuse the deployment when the mechanism cannot provide this
fencing.
If the lock is unavailable, its owner or lease is stale, or the mechanism
cannot prevent a second actor from mutating the target, refuse the deployment;
never steal a stale lock without independent recovery authorization.
If any later read-only preflight check refuses before mutation, release the
current owner's lock in a cleanup path and verify that it was released. If the
lock cannot be released, mark the operation `blocked` and hand it to the
independent recovery owner; do not leave an ordinary preflight refusal holding
the target indefinitely.

1. **Require a deployment host and approved identity.** The deployment
   contract must contain the exact approved immutable Tailscale node ID and
   expected target hostname. A node name is display metadata and cannot
   authorize a target. On the target, read the actual `hostname` and
   Tailscale identity/status, then verify that they map to the approved node ID
   and expected hostname before proceeding. The
   actual hostname must also contain `deploy`, case-insensitively. A missing
   command, empty result, hostname without that substring, identity mismatch,
   or unverifiable mapping stops the deployment. Do not trust a hostname, node
   name, or IP
   supplied only by the caller or inferred from a repository label.

   ```bash
   TARGET_HOSTNAME="$(hostname)" || exit 1
   case "${TARGET_HOSTNAME,,}" in
     *deploy*) ;;
     *) echo "refusing deployment: target hostname must contain deploy" >&2; exit 1 ;;
   esac
   ```

2. **Require Tailscale.** Confirm that the Tailscale daemon is running and
   authenticated, that the target has a current Tailscale address, and that
   the address belongs to the target itself. Obtain the address on the target
   (for example, with `tailscale ip -4`) instead of accepting an arbitrary
   caller-provided address. Missing, stale, or conflicting Tailscale state
   stops the deployment.

3. **Require an authorized Tailscale path.** When the deployment uses SSH,
   the connection must target the discovered Tailscale address and its source
   peer must be in the same Tailscale network. Inspect the connection metadata
   (`SSH_CONNECTION` where available) and the route actually used. Verify the
   deployment peer and catalog readers through a Tailscale ACL/tailnet policy
   or an explicit source-peer allowlist; interface membership alone is not
   authorization. A public source address, public DNS/IP target, wildcard
   fallback, unknown route, or unverifiable peer policy stops the deployment.
   Non-SSH runners must provide an equivalent verified target access path.

4. **Inventory the current boundary without changing it.** Record the
   effective SSH listeners and every effective SSH port, firewall rules on
   every interface, current outbound policy, Tailscale interface, and
   Tailscale transport mode (direct underlay or relay), its required underlay
   interface/port policy, and listeners for TCP/80 and all declared service
   ports. If SSH is enabled, this contract permits exactly one SSH listener on
   TCP/22; any non-22 or additional SSH listener is a refusal before mutation.
   If the approved access path is non-SSH, record that SSH is disabled. Record
   whether the baseline access catalog exists,
   its registry/page paths, and the HTTP service that serves it. A public
   listener or wildcard allow rule is a hardening task, not permission to
   deploy. If the listener or firewall state cannot be inspected, stop.

## Authorized target hardening

Apply this separate mutating phase only to a `tailscale-hardened` target,
after it passes the read-only preflight, the deployment contract is known,
required approvals are present, and the release has an authorized rollback
owner. The phase must be recorded as part of the deployment evidence; it is
not an implicit side effect of connecting over SSH.

1. **Prepare independent recovery.** Snapshot the SSH configuration, firewall
   policy, HTTP service configuration, catalog registry/page, and relevant
   ownership or service-unit state. Prepare exact restore commands for all of
   those surfaces and arm a tested time-bounded restore through an independent
   channel such as a provider console, separate management plane, or an
   already-authorized recovery operator. The restore lease must have an
   end-to-end TTL that covers hardening, deployment, observation, catalog
   publication, rollback, and final verification. Renew it with a heartbeat
   under the target lock before expiry; if renewal is lost or the TTL cannot
   cover the bounded operation, stop new mutations and invoke recovery before
   the restore expires. Do not mutate any boundary when independent recovery
   is unavailable. Treat any snapshot, restore-command, arming, lease, or
   heartbeat setup failure as a recovery-setup failure: stop before boundary
   mutation, cancel or disarm every recovery artifact that may have been
   partially created through the independent channel, and independently verify
   that it is disarmed. Only then release the current owner's target lock and
   verify that its lease and fencing token are retired. If disarming or release
   cannot be verified, keep the target `blocked` with the recovery owner in
   control; do not leave a restore or lease waiting for its TTL. A restore must
   also cover a catalog initialization or HTTP-service change that fails before
   firewall verification.

2. **Deny every public inbound port before listener changes.** Apply the
   incoming policy before reloading SSH or starting/reloading the HTTP service.
   Preserve the existing outbound policy;
   never change a restricted egress policy to allow all outgoing traffic as a
   side effect. The effective inbound policy must drop unsolicited traffic by
   default on every public interface and allow only established/related
   traffic, loopback, and explicitly authorized Tailscale sources for:

   - TCP/22 for deployment SSH only when SSH is the approved access path;
   - TCP/80 for the access catalog; and
   - declared service ports.

   Before activating this policy, verify that the approved peer has a usable
   Tailscale transport. For a direct underlay, preserve the currently
   required Tailscale underlay interface and port rule in the same atomic
   fenced mutation and verify reachability after activation. If that cannot be
   preserved, require a verified relay-only path before applying the public
   default deny. A Tailscale underlay exception carries encrypted Tailscale
   transport only; it is not a public login or application-port exception. If
   neither transport can be verified, refuse hardening before changing the
   firewall.

   A broad allow rule for SSH, port 80, or a service port is a refusal. For a
   UFW target, preserve the current outgoing default and have the target's
   atomic mutation authority apply `ufw default deny incoming` plus
   interface- and approved-source-scoped rules for the allowed ports. Carry
   the current fencing value into that authority for every rule change; never
   run raw `ufw` commands outside it. Omit the TCP/22 rule when the approved
   access path is non-SSH. Add declared service ports with the same interface
   and approved-source scope. Inspect and remove conflicting wildcard allow
   rules only under the recovery plan; do not run a blind firewall reset or
   `ufw default allow outgoing`. If UFW is inactive, activate it only after
   the allowlist is staged, then reload it as required and verify that the
   `ufw status` output is active and the effective kernel rules enforce the
   policy. Activation and reload are also mutations and must use the same
   atomic fencing authority. A saved UFW policy is not evidence of filtering.
   For nftables or another provider,
   validate, activate, and inspect the effective ruleset through the same
   atomic mutation authority; preserve egress policy and drop all public input.
   Immediately after the firewall is active and before
   reloading any listener or starting/reloading the HTTP service, inspect the
   connection-tracking and socket/session state and drain every existing
   inbound session whose source or route is public or outside the approved
   Tailscale policy. Preserve only the current approved Tailscale management
   session and approved Tailscale flows. If non-Tailscale sessions cannot be
   identified and terminated, or the drain cannot be verified, invoke
   recovery and do not change a listener.

3. **Limit SSH to Tailscale.** If SSH is enabled, configure the target SSH
   service to listen only on the discovered Tailscale address(es); for
   OpenSSH, use explicit `ListenAddress` entries and remove wildcard
   listeners. This hardened contract supports exactly one SSH listener on
   TCP/22. Enumerate every effective SSH port before reload and reject any
   non-22 or additional listener; never leave a secondary SSH listener
   outside the same Tailscale-only boundary. Validate the configuration before
   reload. The change is rejected if the socket table still shows TCP/22 on a
   public address, or if the daemon cannot enforce the Tailscale-only listener
   requirement. If the approved target access path is non-SSH, do not enable
   SSH: the effective SSH listener set must be empty and the firewall must
   contain no TCP/22 allow rule. The firewall source/ACL restriction for the
   catalog and declared service ports remains mandatory.

4. **Stage the baseline catalog offline.** Create or validate the catalog
   registry and page without starting or reloading the HTTP service. The page
   must show the discovered target Tailscale IP and may start with zero service
   entries; only verified deployments may add service rows. Keep the staged
   page and its atomic restore in the recovery plan. Do not expose the new
   page until the scoped firewall policy in step 2 is effective.

5. **Activate, verify, recover, and retain the restore.** With the firewall
   policy effective, configure the existing HTTP service to serve the staged
   page at the target's Tailscale address on TCP/80, then start or reload it.
   Bind it to that address where supported; if the service uses a wildcard
   listener, the already-active firewall and public-side probe below must
   still prove that it is not publicly reachable. If the approved target
   access path uses SSH, open a new SSH connection to the Tailscale address
   from an approved peer. Otherwise, exercise the approved non-SSH management
   path and record that SSH was not used. In both cases request the catalog
   through the approved Tailscale path. Verify from a public-side probe or
   equivalent firewall evidence that TCP/22, TCP/80, and every declared
   service port are denied publicly. Before that verification, inspect the
   connection-tracking and socket/session state and drain every existing
   inbound session whose source or route is public or otherwise outside the
   approved Tailscale policy. Preserve the current approved Tailscale
   management session and approved Tailscale flows. If non-Tailscale sessions
   cannot be identified and terminated (or an equivalent connection-drain
   operation cannot be verified), invoke recovery; a new-connection probe alone
   is insufficient.
   If any check fails, invoke the independently armed restore immediately and
   verify the restored SSH, firewall, HTTP, and catalog boundary. If restore
   also fails, mark the target `blocked`, stop deployment, and hand the
   recovery action to the out-of-band owner. After a successful hardening
   verification, keep the time-bounded restore armed and retain the target
   lock through deployment and catalog publication; the final post-deployment
   boundary check retires it. After a completed restore, cancel and retire the
   time-bounded restore, then verify through the independent channel that it is
   disarmed before ending the failed operation. If disarming cannot be
   confirmed, keep the target `blocked` and do not continue. Never declare
   success while a boundary or recovery result is unknown. Record only safe
   status and addresses; never print credentials or secret-bearing command
   arguments.
   After the restore is verified disarmed, release the current owner's target
   lock and verify that its lease and fencing token are no longer active. If
   the lock cannot be released or its retirement cannot be verified, keep the
   target `blocked` and hand it to the independent recovery owner.

## Tailscale access catalog

For a `tailscale-hardened` publishing target, the access catalog is a generated
page served by the target's existing HTTP service at
`http://<local-tailscale-ip>/` on TCP/80. The page displays the current local
Tailscale IP and one row per verified service with its service name and
deployment address. The HTTP service must bind to the target Tailscale address
where supported; otherwise the already-effective firewall must deny TCP/80 on
every public interface and allow it only from the approved Tailscale sources.

Use `scripts/update_access_catalog.py` on the target to maintain the registry
and page. Initialize an empty baseline before the first publication, then run
the updater after the service revision, health, and smoke checks pass:

The deployment mutation authority must first create a target-scoped, owner-only
fence file and its stable sibling `.lock` authority file. Deployment and
recovery must acquire that same sibling lock before changing the fence record;
the updater refuses a missing lock and never recreates it, and the lock inode
must never be replaced while an operation is active. The fence must have one
hard-link; aliases are rejected. Its active JSON record contains
`state: "active"`, `role` set to `deployment` or `recovery`, the current
`owner`, positive `generation`, and a future timezone-aware `expires_at`. Pass
the exact owner and generation to the updater. Recovery must use a newly issued
generation that differs from the pending transaction's deployment generation.
The updater holds the fence while it stages and publishes both files.
Each replacement, unlink, or metadata repair is performed through the fenced
mutation authority while that exact fence is current; the updater rejects a
missing, expired, replaced, or revoked fence. A stale pending transaction is
left for the independent recovery owner; that owner may use a `recovery` fence
with `--recover-pending` to restore the prior pair.
The registry parent must be pre-provisioned as a real, non-world-writable
directory accessible to both authorized Unix principals; provision it with
their shared group (and setgid when needed). The updater never creates this
directory and rejects unsafe path components. The lock, transaction, and
cleanup-marker sidecars use that directory group with mode `0660`. The
registry also uses mode `0660` and is private to that shared group; world
permissions are rejected. Pre-provision the HTML document-root
directory as a real, non-world-writable directory; the updater never creates
it and rejects unsafe path components. The page writer must either be able to
preserve its exact UID/GID or use its shared readable group/other-readable
contract; an incompatible or world-writable page is refused. Both locks use
bounded non-blocking acquisition, and a five-second lock timeout is a failed
update.

```bash
python3 <skill-dir>/scripts/update_access_catalog.py \
  --registry /var/lib/auto-deploy/access-catalog.json \
  --output /var/www/auto-deploy/index.html \
  --fence-file /run/auto-deploy/catalog-fence.json \
  --fence-owner "$DEPLOYMENT_LOCK_OWNER" \
  --fence-generation "$DEPLOYMENT_FENCE_GENERATION" \
  --initialize

python3 <skill-dir>/scripts/update_access_catalog.py \
  --registry /var/lib/auto-deploy/access-catalog.json \
  --output /var/www/auto-deploy/index.html \
  --fence-file /run/auto-deploy/catalog-fence.json \
  --fence-owner "$DEPLOYMENT_LOCK_OWNER" \
  --fence-generation "$DEPLOYMENT_FENCE_GENERATION" \
  --service-name <service-name> \
  --deployment-address http://<local-tailscale-ip>:<declared-port>/
```

The updater always discovers the local Tailscale IPv4 and treats
`--tailscale-ip`, when supplied, only as an assertion against that fresh
discovery. It accepts only `http` or `https` addresses whose host is that exact
Tailscale IP, escapes all HTML values, replaces a matching service name without
duplicates, and retains unrelated rows. It serializes updates with the fence
authority and a registry-side lock. A durable transaction journal records both
snapshots before replacement, records rollback intent until both replacements
are complete, and reconciles an interrupted pair before a later update. If
journal removal or its directory sync cannot be confirmed, a durable cleanup
marker remains until an authorized retry or recovery clears it. The marker is
rewritten to a durable `cleared` tombstone after successful cleanup so an
uncertain marker sync never removes the last recovery metadata; generated files
are size-limited. A missing registry with an existing page,
non-regular path, malformed metadata, different host, unsafe address, stale
fence, unsafe document root, incompatible or world-writable page owner, lock
timeout, or failed write is an error. The
`--recover-pending` path uses the durable snapshots and an authorized recovery
fence; it does not require the Tailscale CLI. The updater never starts an HTTP
server or changes firewall rules. After each update, request the page through
the approved Tailscale path and run the public-denial probe before marking the
deployment verified. A failed update or probe leaves the release unverified
and follows the documented recovery path.

## Required deployment contract

Before any mutating deployment action, identify and record:

- target environment (`local`, `development`, `staging`, or `production`);
- target designation (`tailscale-hardened` for every service-publishing target,
  or an explicit non-publishing local/development target);
- for a `tailscale-hardened` target, the approved target identity (exact
  immutable Tailscale node ID and expected hostname; node names are display
  metadata only);
- for a `tailscale-hardened` target, the trusted node-ID-to-address resolution
  source (authenticated Tailscale control-plane lookup or approved tailnet
  DNS name);
- for a `tailscale-hardened` target, the approved Tailscale transport mode and
  its verified underlay rule or relay-only path;
- source commit, tag, release, or other immutable revision;
- artifact and provenance (image digest, package checksum, or build ID);
- existing trigger and deployment entry point (workflow, release job, script,
  platform command, or operator runbook);
- required approvals, environment protections, permissions, and maintenance
  window;
- for a `tailscale-hardened` target, the target-lock mechanism and owner/lease
  policy that serialize hardening, deployment, catalog, and recovery, including
  lease expiry, heartbeat renewal, and fencing-token or generation checks;
- for a `tailscale-hardened` target, an authenticated handoff by which the
  existing deployment entry point receives and validates that target fence
  before each mutation, or an explicit refusal to use that entry point;
- for a `tailscale-hardened` target, the access-catalog registry/page paths,
  HTTP serving entry point, and all declared service ports. Each catalog
  deployment address must be target-local or resolve and route through the
  approved Tailscale identity and address; public load balancers and other
  hosts require a separate endpoint contract with its own identity, ACL, and
  public-denial verification;
- health endpoint, smoke test, success threshold, and observation window; and
- the last known-good artifact and a tested rollback path.

If the target, authorization, source revision, or rollback boundary is missing,
inspect the repository and report the gap, but stop before changing a shared or
production environment. Do not infer production approval from a successful
build or from a request to deploy to a different environment.

## Safety boundaries

- Prefer the repository's existing CI/CD or deployment mechanism. Do not create
  new cloud resources, alter DNS, change production secrets, or add a new
  provider without an explicit request and a reviewable change.
- Use immutable revisions and artifacts for deployment. Do not deploy a
  mutable `latest` reference to production when a commit, tag, digest, or
  build ID is available.
- Never print, commit, or place credentials in command arguments, logs,
  screenshots, artifacts, or Skill output. Read secrets only through the
  target platform's secret/environment mechanism and verify presence by name
  or status, never by echoing values.
- Keep Git publication identity separate from deployment credentials. Route
  commits, pushes, and pull requests through `github-push-when-ready`; use the
  repository's configured non-root identity and do not change global Git
  configuration. Run deployment jobs with the least-privileged service
  identity; do not introduce root or `sudo` as a default.
- Treat database and infrastructure migrations as separate risk boundaries.
  Check backward compatibility, backups, lock/timeout behavior, and rollback
  feasibility before applying them. Do not automatically reverse an
  irreversible migration without an explicit recovery plan.
- Keep waits and retries bounded. A timeout, missing telemetry, or ambiguous
  health result is a failed verification, not evidence of success.
- Do not delete the previous release, backups, or rollback artifacts until the
  observation window and retention policy permit it.

## Workflow

1. **Classify the release.** Define the operation mode (`plan` (plan-only),
   `execute`, `verify`, or explicitly authorized `rollback`), environment, target designation,
   approved target identity, release scope, source revision, artifact,
   expected user impact, approval boundary, and rollback owner. A service
   publication must use `tailscale-hardened`; a local/development deployment
   may use the non-publishing designation only when it exposes no shared
   service. For a scheduled or event-triggered deployment, verify the exact
   trigger and branch/tag filter.
2. **Discover the deployment contract.** Inspect the README and deployment
   documentation, CI workflows, container/build files, manifests, scripts,
   environment examples, and runbooks. Prefer an existing workflow dispatch,
   release job, or documented command. Distinguish local development commands
   from shared-environment deployment commands.
3. **Run the target eligibility gate.** For a service-publishing or otherwise
   `tailscale-hardened` target, complete the mandatory read-only security
   preflight above and preserve the discovered hostname, approved node
   ID, Tailscale address, interface, authorized peer policy, and
   verification result as safe deployment evidence. For an explicitly
   non-publishing local/development target, record why the gate is not
   applicable and do not expose a shared service. An unknown designation is a
   refusal. In `plan` mode, collect the contract, target requirements, release
   metadata, approvals, and selected checks as read-only evidence. Do not
   acquire a mutating lease, harden the target, trigger automation, write the
   catalog, or recover; after step 4, go to step 12 with status `planned`.
   In `verify` mode, collect only read-only target and release
   evidence. Skip only mutating hardening and release actions: steps 5-7, the
   catalog write in step 9, and recovery step 11. Continue with the read-only
   observation in step 8 and the read-only final-boundary checks in step 10,
   then go to step 12. A verify result is successful only when those checks
   establish the intended running revision, health, smoke flow, and, for a
   `tailscale-hardened` target, its access boundary and catalog state; an
   unknown or failed check is unverified. A
   requested hardening, deployment, catalog update, or rollback requires the
   corresponding authorized `execute` or `rollback` mode.
4. **Run release preflight checks.** For an authorized `execute`, use
   `test-workflow` for the smallest checks that prove the release contract:
   configuration validation, focused tests, build, image/package creation, and
   relevant integration or smoke tests. Confirm the source revision is
   available, the artifact is traceable, required secret names and permissions
   are present, and the destination has capacity and a rollback target. For a
   `tailscale-hardened` target, also confirm the target hardening approval and
   independent recovery path are ready. For an authorized `rollback`, select
   the recorded last-known-good immutable artifact or digest, confirm its
   migration compatibility and availability, and verify target capacity and
   recovery readiness; do not build or package a replacement artifact. In
   `verify` mode, inspect the existing immutable release, its running revision
   or digest, runtime configuration, and available health and smoke evidence;
   do not build, package, trigger, or require execute-only hardening approval
   or recovery setup. In `plan` mode, record the proposed source, artifact,
   checks, approvals, target requirements, and rollback target without
   contacting mutation authorities or creating release artifacts. Missing
   required evidence leaves the release unverified, or leaves a plan
   incomplete. Do not bypass a failed required check just to trigger a
   deployment.
5. **Apply and verify target hardening.** For an authorized `execute` or
   `rollback` operation on a `tailscale-hardened` target,
   complete the separate authorized target-hardening phase. Do not continue
   unless SSH is disabled or has exactly one TCP/22 listener only on
   Tailscale, the approved non-SSH path is verified when SSH is disabled, the
   baseline catalog is served on Tailscale TCP/80, public inbound ports are
   denied, the catalog and declared service ports are limited to approved
   Tailscale sources, and the recovery verification passes. Keep the target
   lock lease, heartbeat, fencing checks, and hardening restore armed through
   the later deployment and catalog steps; the final boundary check retires
   the restore. Skip this phase only for the explicitly non-publishing
   local/development designation.
6. **Prepare the release.** Produce or select the immutable artifact, record
   its digest/checksum/build ID, and ensure the deployment configuration is
   reviewed. If automation must be added or changed, make the smallest
   reviewable change, use least-broad triggers, protect production environments,
   and keep secrets outside the repository.
7. **Trigger the existing automation.** Use the documented interface and pass
   only non-secret ordinary inputs; transfer any fencing value through the
   authenticated, protected handoff defined by the target contract. For a
   `tailscale-hardened` target, before triggering bind the run to the current
   target-lock owner, renewable lease, and exact fencing token or generation.
   The workflow or platform job must validate that
   same authenticated fence immediately before every target mutation and stop
   on expiry, owner change, or generation mismatch. Verify that scheduled and
   concurrent runs use the same target serialization and cannot bypass this
   handshake. For GitHub Actions, a typical controlled trigger is `gh workflow
   run <workflow> --ref <immutable-ref>` followed by bounded run monitoring;
   adapt to the repository's actual workflow and required inputs. If the
   existing entry point cannot carry and enforce the current target fence,
   refuse to trigger it, cancel and retire the hardening restore through the
   independent channel, and verify it is disarmed. Only then release the current
   owner's target lock and verify its lease and fencing token are retired. If
   either retirement cannot be verified, keep the lock state under the
   independent recovery owner and mark the target `blocked`. Record the
   workflow/run ID or platform deployment ID. An explicitly non-publishing
   local/development target may use its existing local automation without the
   hardened target lock or restore only after verifying that it exposes no
   shared service; otherwise refuse it.
8. **Observe and verify.** Follow the rollout state until completion or a
   bounded timeout. Check deployment status, logs, health endpoints, error
   rates, and readiness. For an `execute` or authorized `rollback`, run the
   smallest configured smoke flow after the release. For `verify`, use existing
   smoke evidence or run only a contract-declared read-only or idempotent
   check through the approved Tailscale path; do not POST, enqueue work, invoke
   administrative actions, or otherwise change target state. If no safe smoke
   evidence or check exists, leave verification unverified. Confirm the
   running revision/digest matches the intended artifact, not merely that a
   command exited successfully.
9. **Update the access catalog.** For an `execute` or explicitly authorized
   `rollback` on a `tailscale-hardened` target, after a service's revision and
   health are verified, update the generated catalog with the service name, a
   target-local deployment address, and the target's discovered Tailscale IP.
   Validate that every address resolves and routes to the approved target
   identity and address before writing it; refuse public load-balancer or
   different-host addresses unless a separate endpoint contract supplies and
   verifies that endpoint's identity, ACL, and public denial. Serve that page
   on the target's Tailscale address at TCP/80 through the existing HTTP
   service. The update must preserve an atomic restore of the previous
   catalog. In `verify` mode on a `tailscale-hardened` target, read and
   validate the existing catalog without writing or publishing it; a missing,
   malformed, or mismatched catalog is unverified. A catalog update or
   Tailscale-only access check in `execute`/`rollback` that fails makes the
   release unverified and follows the rollback policy; a verify-only read
   check failure makes verification unverified and must not trigger a
   mutation. Do not publish a shared service or update a catalog for the
   explicitly non-publishing local/development designation.
10. **Recheck the final boundary and retire recovery.** For an `execute` or
   authorized `rollback` on a `tailscale-hardened` target, while the target
   lock lease and hardening restore remain active, continue the lock heartbeat
   and validate its fencing value before each check or mutation. Repeat the
   connection-tracking and
   socket/session inspection at this final boundary and drain every existing
   inbound session whose source or route is public or outside the approved
   Tailscale policy, preserving only the approved Tailscale management session
   and flows. Repeat the complete boundary checks after service startup and
   catalog publication: approved target identity and hostname, Tailscale
   access path, SSH or approved non-SSH path, Tailscale transport reachability
   and its recorded underlay or relay-only policy, and the effective SSH port
   set (exactly TCP/22 when SSH is enabled, or empty when it is disabled),
   active and effective firewall rules, catalog access, listener bindings, and
   public denial for every declared port. Compare the effective outbound
   policy with the recorded baseline. If sessions cannot be drained, the
   outbound policy
   differs from baseline, or the lock cannot be renewed or fenced, stop and
   enter recovery. If all checks pass,
   cancel and retire the hardening restore, verify through the independent
   channel that it is disarmed, release the target lock, and independently
   verify that its lease and fencing generation are inactive. If any
   retirement or verification is uncertain, keep the target `blocked` under
   the independent recovery owner. If a check fails, keep both active and
   enter recovery. For `verify` mode on a `tailscale-hardened` target, continue
   holding only the read-only observation lease acquired before the first
   target read. If acquisition was refused or a mutating target lock,
   deployment generation, or hardening restore is active or appears during
   verification, mark the result `blocked`/unverified, release only an
   observation lease owned by this verify run, and do not cancel, retire,
   release, or alter the mutating resources. While the observation lease is
   held, perform the same final checks without
   changing listeners, firewall rules,
   catalog files, or sessions: approved target identity and hostname,
   Tailscale path and transport policy, the effective SSH port set, firewall
   ingress and outbound policy, existing catalog contents, listener bindings,
   public denial for every declared port, and the running revision, health,
   and smoke results from step 8. Do not drain or terminate sessions in this
   mode; any public or outside-policy session, unknown state, or failed check
   is unverified. Release the observation lease and verify that it is
   inactive. For an explicitly non-publishing
   local/development target, verify that no shared service is exposed and close
   the release without requiring a hardened lock, restore, or access catalog.
11. **Recover on failure.** Stop or pause further rollout, capture safe failure
   evidence, and compare the running state with the last known-good release.
   For a `tailscale-hardened` target, the independent recovery owner must
   first revoke the current deployment generation through the independent
   mutation authority, even if its lease still appears valid. Then cancel or
   pause the deployment run and verify that no active, queued, or retrying
   executor can issue another target mutation. Acquire the target lock under
   a new recovery-only fencing generation and verify that the old generation
   is rejected before any restore mutation. If run quiescence or this fencing
   handoff cannot be verified, keep the target `blocked` and do not roll back.
   Keep that fenced target lock and the
   hardening restore active while rolling back through the documented immutable
   artifact or platform mechanism. Atomically
   reconcile the access catalog at the same time: restore the prior page or
   remove/update the
   affected row to the last known-good deployment address. Before retiring
   recovery, rerun the configured health endpoint and smoke flow, and verify
   that the running revision or digest matches the intended last-known-good
   artifact. Request the restored page through the approved Tailscale path,
   repeat the final session drain, and rerun the full final boundary checks,
   including the current lock fencing value and an exact comparison of the
   effective outbound policy with the recorded baseline. Only then cancel and
   retire the restore and independently verify that it is disarmed. Release
   the lock and independently verify that its lease and fencing generation are
   inactive.
   If either retirement cannot be verified, keep the target `blocked` and hand
   it to the out-of-band recovery owner. For an explicitly non-publishing
   local/development target, use its documented local rollback, rerun its
   applicable health and smoke checks, and verify that no shared service was
   exposed; do not require or retain the hardened lock, restore, or catalog. If
   rollback is unsafe, unavailable, partially applied, or cannot retire
   recovery safely, stop and report the concrete recovery action needed.
12. **Close the release.** Report the target, source revision, artifact ID,
   automation/run ID, checks, observed health, rollback result, residual risk,
   and next action without exposing secrets. Update `Repo_Current_State.md` or
   deployment documentation only when verified repository behavior or the
   deployment contract changed. For `plan`, report status `planned`, the
   proposed immutable artifact and checks, required approvals, target gate,
   rollback target, and unresolved blockers; do not report an execution or
   deployment run that was never created.

## Operating modes

### Execute existing automation

Use when the repository already has a workflow, release pipeline, deployment
script, or platform integration. Inspect its inputs and protections first,
trigger the narrowest appropriate target, and preserve the provider's audit
trail. Do not replace a working pipeline with an ad-hoc local deployment.

### Add or update automation

Use only when the user asks to create or change deployment automation. Identify
the artifact, trigger, environment protection, secret names, permissions,
concurrency policy, health check, timeout, and rollback behavior before
editing. Keep deployment configuration separate from application secrets and
test the workflow syntax plus any locally executable steps before publishing.

### Verify or roll back

Use when a deployment is reported as complete or unhealthy. Verify the running
revision and health independently of the triggering command. For rollback,
select a known-good immutable artifact, confirm migration compatibility, and
verify the recovered state before declaring success.

## Handoff and reporting

The final handoff must distinguish `planned`, `triggered`, `verified`,
`rolled_back`, `failed`, and `blocked`. Include only safe identifiers and
short paths; never include secret values, access tokens, private keys, or full
credential-bearing URLs. State unverified surfaces explicitly, including
missing telemetry, unchecked background jobs, untested rollback, or an
unavailable production health endpoint.

Use related Skills when their triggers apply:

- `test-workflow` for release validation and smoke-test evidence;
- `data-document-redaction` for the staged commit set, and project-specific
  sanitization/review when deployment artifacts or logs cross a non-Git
  sharing/publication boundary;
- `github-push-when-ready` for commits, pushes, PRs, and merged source-branch
  cleanup; and
- `repo-current-state` after verified deployment-contract or repository-state
  changes.
