#!/usr/bin/env bash
set -euo pipefail

DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
UPDATE=0

usage() {
  cat <<'USAGE'
Install the complete i-zrhe2016 Codex development workflow skill set.

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

command -v git >/dev/null 2>&1 || { echo "error: git is required" >&2; exit 1; }
command -v mktemp >/dev/null 2>&1 || { echo "error: mktemp is required" >&2; exit 1; }
command -v tar >/dev/null 2>&1 || { echo "error: tar is required" >&2; exit 1; }

mkdir -p "$DEST_ROOT"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT INT TERM

# repo|path|destination-name
SKILLS=(
  "i-zrhe2016/codex-development-workflow|.|codex-development-workflow"
  "i-zrhe2016/context-skill|context-efficiency|context-efficiency"
  "i-zrhe2016/plan-to-ticket|.|plan-to-ticket"
  "i-zrhe2016/test-skill|frontend-click-test|frontend-click-test"
  "i-zrhe2016/code-review|code-review|code-review"
  "i-zrhe2016/Repo_Current_State.md|.|repo-current-state"
  "i-zrhe2016/data-document-redaction|data-document-redaction|data-document-redaction"
  "i-zrhe2016/github-push-skill|github-push-when-ready|github-push-when-ready"
)

installed=0
skipped=0

for spec in "${SKILLS[@]}"; do
  IFS='|' read -r repo subpath name <<< "$spec"
  dest="$DEST_ROOT/$name"

  if [ -e "$dest" ]; then
    if [ "$UPDATE" -eq 1 ]; then
      rm -rf "$dest"
    else
      echo "skip: $name already exists at $dest"
      skipped=$((skipped + 1))
      continue
    fi
  fi

  clone_dir="$TMP_ROOT/${name}-repo"
  echo "install: $name <- https://github.com/$repo ($subpath)"
  git clone --quiet --depth 1 "https://github.com/$repo.git" "$clone_dir"

  if [ "$subpath" = "." ]; then
    src="$clone_dir"
  else
    src="$clone_dir/$subpath"
  fi

  if [ ! -f "$src/SKILL.md" ]; then
    echo "error: $repo/$subpath does not contain SKILL.md" >&2
    exit 1
  fi

  mkdir -p "$dest"
  (cd "$src" && tar --exclude='.git' -cf - .) | (cd "$dest" && tar -xf -)
  installed=$((installed + 1))
done

echo
echo "Installed: $installed"
echo "Skipped:   $skipped"
echo "Location:  $DEST_ROOT"
echo "Restart Codex to discover newly installed skills."
