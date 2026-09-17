#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
UPDATE=0

usage() {
  cat <<'USAGE'
Install the complete Codex development workflow skill set bundled in this
repository.

Usage:
  install-all.sh [--update] [--dest PATH]

Options:
  --update       Replace already-installed workflow skills.
  --dest PATH    Install into PATH instead of $CODEX_HOME/skills.
  -h, --help     Show this help.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --update) UPDATE=1; shift ;;
    --dest)
      [ "$#" -ge 2 ] || { echo "error: --dest requires a path" >&2; exit 2; }
      DEST_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

command -v tar >/dev/null 2>&1 || { echo "error: tar is required" >&2; exit 1; }

[ -f "$REPO_ROOT/SKILL.md" ] || {
  echo "error: repository root not found; run this script from a complete checkout" >&2
  exit 1
}

mkdir -p "$DEST_ROOT"
DEST_ROOT="$(cd -- "$DEST_ROOT" && pwd -P)"
case "$DEST_ROOT" in
  "$REPO_ROOT"|"$REPO_ROOT"/*)
    echo "error: installation destination must not be inside this repository" >&2
    exit 1
    ;;
esac

# source path relative to the repository root|destination-name
# The root package is kept at the repository root for backward compatibility.
SKILLS=(
  ".|codex-development-workflow"
  "skills/context-efficiency|context-efficiency"
  "skills/plan-to-ticket|plan-to-ticket"
  "skills/test-workflow|test-workflow"
  "skills/repo-current-state|repo-current-state"
  "skills/data-document-redaction|data-document-redaction"
  "skills/github-push-when-ready|github-push-when-ready"
  "skills/auto-deploy|auto-deploy"
)

installed=0
skipped=0

for spec in "${SKILLS[@]}"; do
  IFS='|' read -r subpath name <<< "$spec"
  dest="$DEST_ROOT/$name"

  if [ "$subpath" = "." ]; then
    src="$REPO_ROOT"
  else
    src="$REPO_ROOT/$subpath"
  fi

  if [ ! -f "$src/SKILL.md" ]; then
    echo "error: bundled source $subpath does not contain SKILL.md" >&2
    exit 1
  fi
  if [ ! -f "$src/agents/openai.yaml" ]; then
    echo "error: bundled source $subpath does not contain agents/openai.yaml" >&2
    exit 1
  fi

  if [ -e "$dest" ]; then
    if [ "$UPDATE" -eq 1 ]; then
      rm -rf "$dest"
    else
      echo "skip: $name already exists at $dest"
      skipped=$((skipped + 1))
      continue
    fi
  fi

  echo "install: $name <- $subpath"
  mkdir -p "$dest"
  if [ "$subpath" = "." ]; then
    (
      cd "$REPO_ROOT"
      tar -cf - SKILL.md agents docs/workflow/redaction.md references/skill-map.md
    ) | (cd "$dest" && tar -xf -)
  else
    (
      cd "$src"
      tar --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' -cf - .
    ) | (cd "$dest" && tar -xf -)
  fi
  installed=$((installed + 1))
done

echo
echo "Installed: $installed"
echo "Skipped:   $skipped"
echo "Location:  $DEST_ROOT"
echo "Restart Codex to discover newly installed skills."
