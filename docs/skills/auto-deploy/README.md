# Automatic Deployment

`auto-deploy` is the deployment-boundary Skill for planning and executing
automatic releases through a repository's existing CI/CD or deployment
contract.

It requires an explicit target and release revision, uses immutable artifacts,
keeps credentials in the platform secret mechanism, runs bounded health and
smoke verification, and reports or performs a safe rollback when authorized.
It does not assume a cloud provider, create infrastructure without an explicit
request, or treat a successful trigger command as proof of a healthy release.

For a service-publishing target explicitly designated `tailscale-hardened`, the
runtime Skill performs a read-only gate that requires the target hostname to
contain `deploy` (case-insensitive), the approved Tailscale node identity, a
live local Tailscale address, and an authorized Tailscale SSH or non-SSH access
path. A separate authorized hardening phase then limits SSH to Tailscale,
denies every public inbound port, preserves the existing outbound policy,
scopes the catalog and declared service ports to approved Tailscale sources,
and serializes the complete release with independent recovery. The firewall is
verified again after service and catalog changes before recovery is retired.
An explicitly non-publishing local/development target may skip this gate when
the contract records that no shared service is exposed.

The runtime instructions are in
[`skills/auto-deploy/SKILL.md`](../../../skills/auto-deploy/SKILL.md), and the
installed destination is `auto-deploy` under the configured Codex skills
directory.
