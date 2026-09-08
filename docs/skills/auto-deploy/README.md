# Automatic Deployment

`auto-deploy` is the deployment-boundary Skill for planning and executing
automatic releases through a repository's existing CI/CD or deployment
contract.

It requires an explicit target and release revision, uses immutable artifacts,
keeps credentials in the platform secret mechanism, runs bounded health and
smoke verification, and reports or performs a safe rollback when authorized.
It does not assume a cloud provider, create infrastructure without an explicit
request, or treat a successful trigger command as proof of a healthy release.

The runtime instructions are in
[`skills/auto-deploy/SKILL.md`](../../../skills/auto-deploy/SKILL.md), and the
installed destination is `auto-deploy` under the configured Codex skills
directory.
