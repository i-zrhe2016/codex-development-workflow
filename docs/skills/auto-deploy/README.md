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

## Access catalog

The bundled `scripts/update_access_catalog.py` maintains a dependency-free JSON
registry and escaped HTML page. On a hardened publishing host, serve the page
through the existing HTTP service at
`http://<local-tailscale-ip>/` on TCP/80. The page shows the host's Tailscale
IP plus each verified service name and deployment address. The updater accepts
only HTTP(S) addresses on that exact Tailscale IP, updates rows idempotently by
service name, serializes concurrent updates behind the deployment mutation
fence, and uses a durable journal to reconcile the registry/page pair after an
interrupted write. It preserves the existing page mode and preserves the
serving group or exact page owner when the writer has that capability; otherwise
the shared-readable group or other-readable owner contract is required. The
HTML document-root directory must be pre-provisioned with safe real directory
components and must not be world-writable; the updater never creates it and
rejects a world-writable page. The registry directory is also pre-provisioned,
shared by deployment and recovery, and its `0660` journal sidecars include a
cleanup marker retained when journal deletion cannot be confirmed.

Initialize and update it on the target with:

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

The mutation authority must provide an owner-only active fence record and a
stable owner-only sibling `.lock` file. Deployment and recovery acquire that
same lock before changing the fence record and never replace its inode while
an operation is active. The record contains the current owner, positive
generation, future `expires_at`, and `role` set to `deployment` (or `recovery`
for authorized pending-transaction rollback). The updater always discovers the
local Tailscale IPv4; an optional `--tailscale-ip` value is checked against
that discovery. Run the update only after health and
smoke verification, then verify the page from an approved Tailscale peer and
confirm public port-80 denial. The script does not install an HTTP server or
modify the firewall. The pre-provisioned registry directory must be a real,
non-world-writable path accessible to both the deployment and independent
recovery Unix principals; the updater does not create it and its lock,
transaction journal, cleanup marker, and mode `0660` registry use their shared
group. The cleanup marker is rewritten to a durable `cleared` tombstone after
successful cleanup and remains available if marker retirement is uncertain.
World permissions are rejected. The page writer must preserve its
owner or satisfy the documented shared-readable owner contract. Lock waits are
bounded at five seconds, and `--recover-pending` uses the journal and recovery
fence without requiring Tailscale discovery.

The runtime instructions are in
[`skills/auto-deploy/SKILL.md`](../../../skills/auto-deploy/SKILL.md), and the
installed destination is `auto-deploy` under the configured Codex skills
directory.
