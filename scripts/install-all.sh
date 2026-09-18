#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
UPDATE=0
ADOPT_LEGACY=0
MANAGED_MARKER=".codex-development-workflow-managed"

usage() {
  cat <<'USAGE'
Install the complete Codex development workflow skill set bundled in this
repository.

Usage:
  install-all.sh [--update] [--adopt-legacy] [--dest PATH]

Options:
  --update       Replace already-installed workflow skills.
  --adopt-legacy Adopt pre-marker destinations during --update, moving them
                 to a recoverable backup first.
  --dest PATH    Install into PATH instead of $CODEX_HOME/skills.
  -h, --help     Show this help.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --update) UPDATE=1; shift ;;
    --adopt-legacy) ADOPT_LEGACY=1; shift ;;
    --dest)
      [ "$#" -ge 2 ] || { echo "error: --dest requires a path" >&2; exit 2; }
      DEST_ROOT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ "$ADOPT_LEGACY" -eq 1 ] && [ "$UPDATE" -eq 0 ]; then
  echo "error: --adopt-legacy requires --update" >&2
  exit 2
fi

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
  "skills/pr-review|pr-review"
)

# Destinations from bundles retired by the workflow. These are removed only
# during an explicit update so old installations do not keep discovering them.
OBSOLETE_SKILLS=(
  "ponytail"
  "ponytail-review"
  "ponytail-audit"
  "ponytail-debt"
  "ponytail-gain"
  "ponytail-help"
  "auto-deploy"
)

destination_is_managed() {
  local dest="$1"
  local name="$2"

  [ -d "$dest" ] || return 1
  [ -f "$dest/$MANAGED_MARKER" ] || return 1
  grep -Fqx -- "codex-development-workflow:$name" "$dest/$MANAGED_MARKER"
}

backup_legacy_destination() {
  local dest="$1"
  local name="$2"

  if [ -z "${LEGACY_BACKUP:-}" ]; then
    LEGACY_BACKUP="$(mktemp -d "$DEST_ROOT/.codex-development-workflow-legacy.XXXXXX")"
  fi

  local backup="$LEGACY_BACKUP/$name"
  if [ -e "$backup" ] || [ -L "$backup" ]; then
    echo "error: legacy backup destination already exists: $backup" >&2
    return 1
  fi

  mv -- "$dest" "$backup"
  echo "adopt: $name -> $backup"
  migrated=$((migrated + 1))
}

installed=0
skipped=0
migrated=0
LEGACY_BACKUP=""

if [ "$UPDATE" -eq 1 ]; then
  for name in "${OBSOLETE_SKILLS[@]}"; do
    dest="$DEST_ROOT/$name"
    if [ -e "$dest" ] || [ -L "$dest" ]; then
      if destination_is_managed "$dest" "$name"; then
        echo "remove: $name (retired)"
        rm -rf "$dest"
      elif [ "$ADOPT_LEGACY" -eq 1 ]; then
        backup_legacy_destination "$dest" "$name"
      else
        echo "preserve: $name (ownership unverified)"
      fi
    fi
  done
fi

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

  if [ -e "$dest" ] || [ -L "$dest" ]; then
    if [ "$UPDATE" -eq 1 ]; then
      if destination_is_managed "$dest" "$name"; then
        rm -rf "$dest"
      elif [ "$ADOPT_LEGACY" -eq 1 ]; then
        backup_legacy_destination "$dest" "$name"
      else
        echo "preserve: $name (ownership unverified)"
        skipped=$((skipped + 1))
        continue
      fi
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
  printf '%s\n' "codex-development-workflow:$name" > "$dest/$MANAGED_MARKER"
  installed=$((installed + 1))
done

echo
echo "Installed: $installed"
echo "Skipped:   $skipped"
echo "Migrated:  $migrated"
echo "Location:  $DEST_ROOT"
if [ -n "$LEGACY_BACKUP" ]; then
  echo "Backup:    $LEGACY_BACKUP"
fi
echo "Restart Codex to discover newly installed skills."
