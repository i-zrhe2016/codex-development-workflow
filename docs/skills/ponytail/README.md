# Ponytail

This repository bundles the six Codex-compatible skills from
[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail):

- `ponytail` — minimal implementation decision ladder; implicitly eligible for coding tasks.
- `ponytail-review` — diff-only over-engineering review.
- `ponytail-audit` — whole-repository over-engineering audit.
- `ponytail-debt` — report tracked `ponytail:` shortcut markers.
- `ponytail-gain` — show the upstream benchmark scoreboard.
- `ponytail-help` — show modes, skills, invocation, and update guidance.

## Source and license

The imported source is pinned to Ponytail v4.10.0 at
[`e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156`](https://github.com/DietrichGebert/ponytail/tree/e3ba2aa6f1e6f0bc4d69eb09c9f0d0a93af56156)
and is distributed under the MIT License. The attribution text is retained in
[`third-party/ponytail/LICENSE`](../../../third-party/ponytail/LICENSE).

## Workflow integration boundary

The local package exposes the upstream Skill instructions and interface
metadata through `scripts/install-all.sh`. The core Skill may be selected
implicitly for coding work; the report and help skills are explicit utilities.

The upstream repository's Claude/Copilot/Gemini/OpenCode adapters, lifecycle
hooks, plugin manifests, benchmark assets, package dependencies, and host
commands are intentionally not bundled. The workflow's own Ticket, branch,
test, redaction, PR, review, merge, and state gates remain authoritative.

## Update

From this repository checkout, refresh all managed Skills with:

```bash
bash scripts/install-all.sh --update
```

Restart Codex after installation. The installer updates only the directories it
manages and leaves unrelated Skills in the destination alone.

## Maintenance

When refreshing Ponytail, update the pinned commit and verify the six Skill
directories, interface metadata, attribution, and the exclusion boundary before
changing the installer mapping.
