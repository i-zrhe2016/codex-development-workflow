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

  png="${src%.puml}.png"
  if [[ -f "$png" ]]; then
    ptmp="$(mktemp)"
    phttp="$(curl -sS -w "%{http_code}" -o "$ptmp" \
      -X POST "$KROKI_URL/plantuml/png" \
      -H "Content-Type: text/plain" \
      --data-binary "@$src")"
    if [[ "$phttp" != "200" || ! -s "$ptmp" ]]; then
      echo "PNG render failed: $src (HTTP $phttp)" >&2
      cat "$ptmp" >&2 || true
      failures=$((failures + 1))
    elif [[ "$mode" == "--check" ]]; then
      if ! cmp -s "$ptmp" "$png"; then
        echo "PNG render drift: $src -> $png" >&2
        failures=$((failures + 1))
      fi
    else
      mv "$ptmp" "$png"
      echo "rendered compatibility PNG: $src -> $png"
    fi
    rm -f "$ptmp"
  fi
done < <(find docs -type f -name '*.puml' -print0 | sort -z)

echo "processed: $count diagram(s)"
if [[ "$failures" -ne 0 ]]; then
  echo "failed: $failures diagram(s)" >&2
  exit 1
fi
