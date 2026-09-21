#!/usr/bin/env bash
set -euo pipefail

KROKI_URL="${KROKI_URL:-https://kroki.io}"
mode="${1:-render}"

if [[ "$mode" != "render" && "$mode" != "--check" ]]; then
  echo "usage: $0 [render|--check]" >&2
  exit 2
fi

failures=0
count=0

while IFS= read -r -d '' src; do
  count=$((count + 1))
  out="${src%.puml}.svg"
  tmp="$(mktemp)"
  trap 'rm -f "$tmp"' EXIT

  http="$(curl -sS -w "%{http_code}" -o "$tmp" \
    -X POST "$KROKI_URL/plantuml/svg" \
    -H "Content-Type: text/plain" \
    --data-binary "@$src")"

  if [[ "$http" != "200" || ! -s "$tmp" ]] || ! grep -Eq '<svg([[:space:]>])' "$tmp"; then
    echo "render failed: $src (HTTP $http)" >&2
    cat "$tmp" >&2 || true
    failures=$((failures + 1))
    rm -f "$tmp"
    trap - EXIT
    continue
  fi

  if [[ "$mode" == "--check" ]]; then
    if [[ ! -f "$out" ]] || ! cmp -s "$tmp" "$out"; then
      echo "render drift: $src -> $out" >&2
      failures=$((failures + 1))
    else
      echo "ok: $src"
    fi
  else
    mv "$tmp" "$out"
    echo "rendered: $src -> $out"
  fi

  rm -f "$tmp"
  trap - EXIT
done < <(find docs -type f -name '*.puml' -print0 | sort -z)

echo "processed: $count diagram(s)"
if [[ "$failures" -ne 0 ]]; then
  echo "failed: $failures diagram(s)" >&2
  exit 1
fi
