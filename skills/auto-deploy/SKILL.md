---
name: auto-deploy
description: Safely plan, configure, execute, verify, and roll back automatic deployments using a repository's existing CI/CD or deployment contract. Use when asked to deploy, release, wire deployment automation, or inspect a failed deployment; do not invent cloud resources or credentials when the target environment is unspecified.
---

# Automatic Deployment

Use this skill for the deployment boundary. It coordinates release intent,
existing automation, preflight validation, bounded observation, health checks,
and rollback. It does not own an application's infrastructure, invent a cloud
provider, or replace the repository's test and publication gates.

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
3. **Run preflight checks.** Use `test-workflow` for the smallest checks that
   prove the release contract: configuration validation, focused tests, build,
   image/package creation, and relevant integration or smoke tests. Confirm
   the source revision is available, the artifact is traceable, required secret
   names and permissions are present, and the destination has capacity and a
   rollback target. Do not bypass a failed required check just to trigger a
   deployment.
4. **Prepare the release.** Produce or select the immutable artifact, record
   its digest/checksum/build ID, and ensure the deployment configuration is
   reviewed. If automation must be added or changed, make the smallest
   reviewable change, use least-broad triggers, protect production environments,
   and keep secrets outside the repository.
5. **Trigger the existing automation.** Use the documented interface and pass
   only non-secret inputs. For GitHub Actions, a typical controlled trigger is
   `gh workflow run <workflow> --ref <immutable-ref>` followed by bounded run
   monitoring; adapt to the repository's actual workflow and required inputs.
   Record the workflow/run ID or platform deployment ID.
6. **Observe and verify.** Follow the rollout state until completion or a
   bounded timeout. Check deployment status, logs, health endpoints, error
   rates, readiness, and the smallest meaningful smoke flow. Confirm the
   running revision/digest matches the intended artifact, not merely that a
   command exited successfully.
7. **Recover on failure.** Stop or pause further rollout, capture safe failure
   evidence, and compare the running state with the last known-good release.
   Roll back through the documented immutable artifact or platform mechanism
   when the rollback is authorized and safe. Re-run health and smoke checks
   after rollback. If rollback is unsafe, unavailable, or partially applied,
   stop and report the concrete recovery action needed.
8. **Close the release.** Report the target, source revision, artifact ID,
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
- `data-document-redaction` before deployment artifacts or logs cross a
  sharing/publication boundary;
- `github-push-when-ready` for commits, pushes, PRs, and merged source-branch
  cleanup; and
- `repo-current-state` after verified deployment-contract or repository-state
  changes.
