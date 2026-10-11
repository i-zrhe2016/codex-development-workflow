# Repository Instructions

This repository packages four documentation-oriented skills. Keep the bundle focused on repository documentation, verified current-state notes, PlantUML diagrams, and staged-document redaction.

## Documentation

- Keep `README.md` as the project introduction and documentation index.
- Put detailed documentation under `docs/` and link it from the README or a linked index.
- Give each fact one canonical owner; link to it instead of copying it elsewhere.
- Verify claims against tracked files, configuration, Git state, or executed checks. Mark uncertain claims clearly.
- Keep skill guidance self-contained and avoid links to skills or processes that are not shipped here.

## Skills and installer

- `skills/` contains the installable skill sources; each bundle needs `SKILL.md` and Codex `agents/openai.yaml` metadata.
- `scripts/install-all.sh` is the authority for the set of packages installed by a fresh install.
- Updates may remove only retired packages carrying this installer's ownership marker. Preserve unowned directories.
- Installation copies skill guidance only; it must not modify global or project instructions/configuration.

## Diagrams

Keep each `.puml` beside its canonical owner document and its same-basename `.svg`. Update source and render together when diagram meaning changes. Use `scripts/render-diagrams.sh` to render or check the maintained sources; do not edit SVGs by hand.

## Validation

Use `python -m unittest discover -s scripts/tests -p 'test_*.py'` and `bash -n` for the installer and diagram script after relevant changes. Check links, package inventory, and `git diff --check` before handoff.
