#!/usr/bin/env bash
set -euo pipefail

TARGET="codex"
DEST_ROOT=""
DEST_EXPLICIT=0
MANAGED_MARKER=".codex-development-workflow-managed"

usage() {
  cat <<'USAGE'
Remove Skills previously managed by codex-development-workflow.

This repository no longer installs runtime Skills. AGENTS.md is the only
repository instruction surface.

Usage:
  retire-skills.sh [--target codex|claude] [--dest PATH]

Options:
  --target NAME  codex (default) or claude
  --dest PATH    Override the target skills directory
  -h, --help     Show this help
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || { echo "error: --target requires a name" >&2; exit 2; }
      TARGET="$2"; shift 2 ;;
    --dest)
      [ "$#" -ge 2 ] || { echo "error: --dest requires a path" >&2; exit 2; }
      DEST_ROOT="$2"; DEST_EXPLICIT=1; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$TARGET" in
  codex)
    [ "$DEST_EXPLICIT" -eq 1 ] || DEST_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
    ;;
  claude)
    [ "$DEST_EXPLICIT" -eq 1 ] || DEST_ROOT="$HOME/.claude/skills"
    ;;
  *)
    echo "error: unknown target: $TARGET (expected codex or claude)" >&2
    exit 2
    ;;
esac

mkdir -p "$DEST_ROOT"
DEST_ROOT="$(cd -- "$DEST_ROOT" && pwd -P)"

MANAGED_NAMES=(
  "codex-development-workflow"
  "github-issue-persistence"
  "repo-current-state"
  "repo-documentation"
  "data-document-redaction"
  "github-publish"
  "context-efficiency"
  "pr-review"
  "ponytail"
  "ponytail-review"
  "ponytail-audit"
  "ponytail-debt"
  "ponytail-gain"
  "ponytail-help"
  "auto-deploy"
  "plan-workflow"
  "develop-workflow"
  "verify-workflow"
  "publish-workflow"
  "integrate-workflow"
  "test-workflow"
  "test-quality"
  "plan-to-ticket"
  "plantuml"
  "github-push-when-ready"
)

removed=0
preserved=0

for name in "${MANAGED_NAMES[@]}"; do
  dest="$DEST_ROOT/$name"
  [ -e "$dest" ] || [ -L "$dest" ] || continue

  marker="$dest/$MANAGED_MARKER"
  if [ -f "$marker" ] && grep -Fqx -- "codex-development-workflow:$name" "$marker"; then
    echo "remove: $name"
    rm -rf "$dest"
    removed=$((removed + 1))
  else
    echo "preserve: $name (ownership unverified)"
    preserved=$((preserved + 1))
  fi
done

echo
echo "Removed:   $removed"
echo "Preserved: $preserved"
echo "Location:  $DEST_ROOT"
