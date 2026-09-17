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


def _is_url_separator(line: str, index: int) -> bool:
    """Return whether ``//`` is the separator in a URI such as ``https://``."""
    if index == 0 or line[index - 1] != ":" or index + 2 >= len(line):
        return False

    scheme_end = index - 1
    scheme_start = scheme_end - 1
    while scheme_start >= 0 and (
        line[scheme_start].isalnum()
        or line[scheme_start] in {"+", ".", "-"}
    ):
        scheme_start -= 1
    scheme = line[scheme_start + 1:scheme_end]
    return (
        bool(scheme)
        and scheme[0].isalpha()
        and not line[index + 2].isspace()
        and not _is_marker(line[index + 2:], allow_leading_star=False)
    )


SHELL_SUFFIXES = {".bash", ".command", ".fish", ".sh", ".zsh"}


def _skip_uri(line: str, index: int, suffix: str) -> int:
    while index < len(line) and not line[index].isspace():
        if line[index] in ";|" and index + 1 < len(line):
            next_index = index + 1
            if line[next_index] == "#":
                if suffix in SHELL_SUFFIXES or line[next_index + 1:next_index + 2].isspace():
                    break
            elif line.startswith("//", next_index):
                comment_body = line[next_index + 2:]
                if suffix in SHELL_SUFFIXES or not comment_body or comment_body[0].isspace() or _is_marker(comment_body, allow_leading_star=False):
                    break
        if line[index] == "#" and index + 1 < len(line) and line[index + 1].isspace():
            break
        index += 1
    return index


def _identifier_end(line: str, index: int) -> int:
    end = index
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1
    return end


def _is_rust_lifetime(line: str, index: int, suffix: str) -> bool:
    if index + 1 >= len(line) or not (
        line[index + 1].isalpha() or line[index + 1] == "_"
    ):
        return False

    identifier_end = _identifier_end(line, index + 1)
    prefix = line[:index].rstrip()
    if prefix and (
        prefix[-1] in "&<>,+"
        or prefix.endswith(("break", "continue", "where", "for"))
    ):
        return True

    label_tail = line[identifier_end:].lstrip()
    if label_tail.startswith(":") and (not prefix or prefix[-1] in "{;"):
        label_body = label_tail[1:].lstrip()
        if label_body.startswith(("loop", "while", "for")):
            return True

    return suffix == ".rs" and prefix.endswith(":")


def marker_lines(text: str, suffix: str = "") -> list[int]:
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
                if not _is_rust_lifetime(line, index, suffix):
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
                    index = _skip_uri(line, index + 2, suffix)
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
        for line_number in marker_lines(text, path.suffix.lower()):
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
