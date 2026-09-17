#!/usr/bin/env python3
"""Find Ponytail markers in source comments without matching quoted text."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
from typing import Iterator


EXCLUDED_DIRS = {
    ".git",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "vendor",
}
EXCLUDED_SUFFIXES = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".markdown",
    ".md",
    ".pdf",
    ".png",
    ".rst",
    ".svg",
    ".tar",
    ".tgz",
    ".txt",
    ".webp",
    ".zip",
}


def _is_marker(body: str, allow_leading_star: bool) -> bool:
    candidate = body.lstrip()
    if allow_leading_star:
        candidate = candidate.lstrip("*").lstrip()
    return candidate.startswith("ponytail:")


def _has_unescaped_quote(line: str, start: int, quote: str) -> bool:
    escaped = False
    for character in line[start:]:
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == quote:
            return True
    return False


def _is_url_separator(line: str, index: int) -> bool:
    """Return whether ``//`` is the separator in a URI such as ``https://``."""
    if index == 0 or line[index - 1] != ":":
        return False

    scheme_end = index - 1
    scheme_start = scheme_end - 1
    while scheme_start >= 0 and (
        line[scheme_start].isalnum()
        or line[scheme_start] in {"+", ".", "-"}
    ):
        scheme_start -= 1
    return scheme_start < scheme_end - 1


def marker_lines(text: str) -> list[int]:
    """Return line numbers whose comments begin with a Ponytail marker."""
    found: list[int] = []
    block_end: str | None = None
    quote: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        index = 0
        while index < len(line):
            if block_end is not None:
                end = line.find(block_end, index)
                if end == -1:
                    if _is_marker(line[index:], allow_leading_star=True):
                        found.append(line_number)
                    break
                if _is_marker(line[index:end], allow_leading_star=True):
                    found.append(line_number)
                index = end + len(block_end)
                block_end = None
                continue

            if quote is not None:
                if line.startswith(quote, index):
                    index += len(quote)
                    quote = None
                elif line[index] == "\\":
                    index += 2
                else:
                    index += 1
                continue

            if line.startswith("'''", index) or line.startswith('"""', index):
                quote = line[index:index + 3]
                index += 3
            elif line[index] == "'":
                # A Rust lifetime such as &'static is not a string delimiter.
                # Single-quoted literals are line-local in the source forms
                # this scanner supports, so require a closing quote first.
                if _has_unescaped_quote(line, index + 1, "'"):
                    quote = line[index]
                index += 1
            elif line[index] in {'"', chr(96)}:
                quote = line[index]
                index += 1
            elif line.startswith("/*", index):
                block_end = "*/"
                index += 2
            elif line.startswith("<!--", index):
                block_end = "-->"
                index += 4
            elif line.startswith("//", index):
                if _is_url_separator(line, index):
                    index += 2
                    continue
                if _is_marker(line[index + 2:], allow_leading_star=False):
                    found.append(line_number)
                break
            elif line[index] == "#":
                if _is_marker(line[index + 1:], allow_leading_star=False):
                    found.append(line_number)
                break
            else:
                index += 1

    return found


def _source_files(root: Path) -> Iterator[Path]:
    if root.is_file():
        if root.suffix.lower() not in EXCLUDED_SUFFIXES:
            yield root
        return

    for directory, names, files in os.walk(root):
        names[:] = sorted(name for name in names if name not in EXCLUDED_DIRS)
        for filename in sorted(files):
            path = Path(directory) / filename
            if path.suffix.lower() not in EXCLUDED_SUFFIXES:
                yield path


def scan(root: Path) -> Iterator[tuple[str, int, str]]:
    """Yield relative path, line number, and source line for each marker."""
    root = root.resolve()
    base = root.parent if root.is_file() else root
    for path in _source_files(root):
        try:
            raw = path.read_bytes()
        except OSError as exc:
            print(f"warning: skipped {path}: {exc}", file=sys.stderr)
            continue
        if b"\x00" in raw:
            continue
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        relative = path.relative_to(base).as_posix()
        for line_number in marker_lines(text):
            yield relative, line_number, lines[line_number - 1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report Ponytail markers found in source comments."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository or source-file path to scan (default: current directory).",
    )
    args = parser.parse_args()
    root = Path(args.root)
    if not root.exists():
        parser.error(f"path does not exist: {root}")

    for relative, line_number, line in scan(root):
        print(f"{relative}:{line_number}: {line.rstrip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
