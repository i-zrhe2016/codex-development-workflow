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

The security preflight is read-only. Run it on the target before any SSH,
firewall, HTTP listener, access-catalog, or deployment mutation. A failed or
ambiguous check is a refusal; do not continue with a best-effort deployment.

1. **Require a deployment host.** Read the target's actual `hostname` output
   on the target and compare it case-insensitively with the substring
   `deploy`. A missing command, empty result, or hostname without that
   substring stops the deployment. Do not trust a hostname supplied by the
   caller or inferred from a repository label.

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
   effective SSH listeners, firewall rules on every interface, current
   outbound policy, Tailscale interface, and listeners for TCP/80 and all
   declared service ports. A public listener or wildcard allow rule is a
   hardening task, not permission to deploy. If the listener or firewall state
   cannot be inspected, stop.

## Authorized target hardening

Apply this separate mutating phase only after the target passes the read-only
preflight, the deployment contract is known, required approvals are present,
and the release has an authorized rollback owner. The phase must be recorded
as part of the deployment evidence; it is not an implicit side effect of
connecting over SSH.

1. **Prepare independent recovery.** Snapshot the SSH configuration and
   firewall policy, prepare the exact restore commands, and arm a tested
   time-bounded restore through an independent channel such as a provider
   console, separate management plane, or an already-authorized recovery
   operator. Do not mutate either boundary when independent recovery is
   unavailable.

2. **Limit SSH to Tailscale.** Configure the target SSH service to listen only
   on the discovered Tailscale address(es); for OpenSSH, use explicit
   `ListenAddress` entries and remove wildcard listeners. Validate the
   configuration before reload. The change is rejected if the socket table
   still shows TCP/22 on a public address, or if the daemon cannot enforce the
   Tailscale-only listener requirement. The firewall source/ACL restriction
   below remains mandatory.

3. **Deny every public inbound port.** Preserve the existing outbound policy;
   never change a restricted egress policy to allow all outgoing traffic as a
   side effect. The effective inbound policy must drop unsolicited traffic by
   default on every public interface and allow only established/related
   traffic, loopback, and explicitly authorized Tailscale sources for:

   - TCP/22 for deployment SSH;
   - TCP/80 for the access catalog; and
   - declared service ports.

   A broad allow rule for SSH, port 80, or a service port is a refusal. For a
   UFW target, preserve the current outgoing default and use the approved
   Tailscale source range or peer address in every allow rule:

   ```bash
   APPROVED_TAILSCALE_PEER_CIDR="<verified-peer-cidr>"
   ufw default deny incoming
   ufw allow in on tailscale0 from "$APPROVED_TAILSCALE_PEER_CIDR" to any port 22 proto tcp
   ufw allow in on tailscale0 from "$APPROVED_TAILSCALE_PEER_CIDR" to any port 80 proto tcp
   ```

   Add declared service ports with the same interface and approved-source
   scope. Inspect and remove conflicting wildcard allow rules only under the
   recovery plan; do not run a blind firewall reset or `ufw default allow
   outgoing`. For nftables or another provider, enforce the same source and
   interface allowlist, preserve egress policy, and drop all public input.

4. **Verify and recover.** Validate the SSH daemon and firewall syntax,
   inspect effective listeners and rules, open a new SSH connection to the
   Tailscale address from an approved peer, and request the catalog through
   that path. Verify from a public-side probe or equivalent firewall evidence
   that TCP/22, TCP/80, and every declared service port are denied publicly.
   If any check fails, invoke the independently armed restore immediately and
   verify the restored boundary. If restore also fails, mark the target
   `blocked`, stop deployment, and hand the recovery action to the out-of-band
   owner. Never declare success while a boundary or recovery result is
   unknown. Record only safe status and addresses; never print credentials or
   secret-bearing command arguments.

## Required deployment contract

Before any mutating deployment action, identify and record:

- target environment (`local`, `development`, `staging`, or `production`);
- source commit, tag, release, or other immutable revision;
- artifact and provenance (image digest, package checksum, or build ID);
- existing trigger and deployment entry point (workflow, release job, script,
  platform command, or operator runbook);
- required approvals, environment protections, permissions, and maintenance
  window;
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

1. **Classify the release.** Define the environment, release scope, source
   revision, artifact, expected user impact, approval boundary, and rollback
   owner. For a scheduled or event-triggered deployment, verify the exact
   trigger and branch/tag filter.
2. **Discover the deployment contract.** Inspect the README and deployment
   documentation, CI workflows, container/build files, manifests, scripts,
   environment examples, and runbooks. Prefer an existing workflow dispatch,
   release job, or documented command. Distinguish local development commands
   from shared-environment deployment commands.
3. **Run the read-only target security preflight.** Complete the mandatory
   target security preflight above and preserve the discovered hostname,
   Tailscale address, interface, authorized peer policy, and verification
   result as safe deployment evidence.
4. **Run release preflight checks.** Use `test-workflow` for the smallest checks that
   prove the release contract: configuration validation, focused tests, build,
   image/package creation, and relevant integration or smoke tests. Confirm
   the source revision is available, the artifact is traceable, required secret
   names and permissions are present, and the destination has capacity and a
   rollback target. Confirm the target hardening approval and independent
   recovery path are ready. Do not bypass a failed required check just to
   trigger a deployment.
5. **Apply and verify target hardening.** Complete the separate authorized
   target-hardening phase. Do not continue unless SSH is Tailscale-only,
   public inbound ports are denied, the catalog and declared service ports are
   limited to approved Tailscale sources, and the recovery verification passes.
6. **Prepare the release.** Produce or select the immutable artifact, record
   its digest/checksum/build ID, and ensure the deployment configuration is
   reviewed. If automation must be added or changed, make the smallest
   reviewable change, use least-broad triggers, protect production environments,
   and keep secrets outside the repository.
7. **Trigger the existing automation.** Use the documented interface and pass
   only non-secret inputs. For GitHub Actions, a typical controlled trigger is
   `gh workflow run <workflow> --ref <immutable-ref>` followed by bounded run
   monitoring; adapt to the repository's actual workflow and required inputs.
   Record the workflow/run ID or platform deployment ID.
8. **Observe and verify.** Follow the rollout state until completion or a
   bounded timeout. Check deployment status, logs, health endpoints, error
   rates, readiness, and the smallest meaningful smoke flow. Confirm the
   running revision/digest matches the intended artifact, not merely that a
   command exited successfully.
9. **Update the access catalog.** After a service's revision and health are
   verified, update the generated catalog with the service name, deployment
   address, and target's discovered Tailscale IP. Serve that page on the
   target's Tailscale address at TCP/80 through the existing HTTP service. A
   catalog update or Tailscale-only access check that fails makes the release
   unverified and follows the rollback policy.
10. **Recover on failure.** Stop or pause further rollout, capture safe failure
   evidence, and compare the running state with the last known-good release.
   Roll back through the documented immutable artifact or platform mechanism
   when the rollback is authorized and safe. Re-run health and smoke checks
   after rollback. If rollback is unsafe, unavailable, or partially applied,
   stop and report the concrete recovery action needed.
11. **Close the release.** Report the target, source revision, artifact ID,
   automation/run ID, checks, observed health, rollback result, residual risk,
   and next action without exposing secrets. Update `Repo_Current_State.md` or
   deployment documentation only when verified repository behavior or the
   deployment contract changed.

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
