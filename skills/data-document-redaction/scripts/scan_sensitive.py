#!/usr/bin/env python3
"""Scan text-bearing files for common PII and secret patterns.

The scanner deliberately never prints matched values.  It is a baseline
detector, not proof that a file is anonymous; use format-aware review and a
human check for free text, images, OCR, and unusual identifiers.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Sequence, Tuple


TEXT_SUFFIXES = {
    ".txt",
    ".csv",
    ".tsv",
    ".json",
    ".jsonl",
    ".ndjson",
    ".log",
    ".sql",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".htm",
    ".md",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".properties",
    ".sh",
    ".bash",
    ".py",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".rs",
    ".toml",
}
ARCHIVE_SUFFIXES = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".zip"}


def _luhn(value: str) -> bool:
    digits = [int(ch) for ch in value if ch.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    total = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


RULES: Sequence[Tuple[str, re.Pattern[str]]] = (
    (
        "PRIVATE_KEY",
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
    ),
    (
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "SECRET_ASSIGNMENT",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|token|bearer|auth(?:orization)?|password|passwd|secret|client[_-]?secret|private[_-]?key|cookie)\b\s*[:=]\s*[\"']?[^\s,;\"']{6,}"
        ),
    ),
    (
        "EMAIL",
        re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    ),
    (
        "URL_SECRET_PARAMETER",
        re.compile(
            r"(?i)(?:[?&](?:token|access_token|apikey|api_key|password|passwd|secret|sig|signature)=)[^&#\s]+"
        ),
    ),
    (
        "IPV4",
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
        ),
    ),
    (
        "CHINA_MOBILE",
        re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)"),
    ),
    (
        "CHINA_ID",
        re.compile(r"(?<![0-9Xx])\d{17}[0-9Xx](?![0-9Xx])"),
    ),
    (
        "SSN_LIKE",
        re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
    ),
    (
        "CREDIT_CARD_LIKE",
        re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
    ),
    (
        "PHONE_LIKE",
        re.compile(
            r"(?<!\d)(?:\+\d{1,3}[ -]?)?(?:\(?\d{2,4}\)?[ -])\d{3,4}[ -]\d{3,4}(?!\d)"
        ),
    ),
)


def iter_files(inputs: Sequence[Path]) -> Iterator[Path]:
    seen = set()
    for item in inputs:
        if not item.exists():
            continue
        candidates = [item] if item.is_file() else item.rglob("*")
        for path in candidates:
            if not path.is_file() or path.is_symlink():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield path


def _read_text(data: bytes) -> str:
    # UTF-8 is preferred; latin-1 keeps byte offsets inspectable for legacy logs.
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def _iter_surfaces(path: Path, max_bytes: int) -> Iterator[Tuple[str, str]]:
    suffix = path.suffix.lower()
    try:
        size = path.stat().st_size
    except OSError:
        return
    if size > max_bytes:
        yield ("file", "")
        return

    if suffix in TEXT_SUFFIXES:
        try:
            yield ("file", _read_text(path.read_bytes()))
        except OSError:
            return
        return

    if suffix in ARCHIVE_SUFFIXES:
        try:
            with zipfile.ZipFile(path) as archive:
                for info in archive.infolist():
                    if info.is_dir() or info.file_size > max_bytes:
                        continue
                    name = info.filename.lower()
                    if not (
                        name.endswith(tuple(TEXT_SUFFIXES))
                        or name.endswith((".rels", ".vml", ".xml", ".json"))
                    ):
                        continue
                    try:
                        yield (f"archive:{info.filename}", _read_text(archive.read(info)))
                    except (OSError, KeyError, RuntimeError, zipfile.BadZipFile):
                        continue
        except (OSError, zipfile.BadZipFile):
            return
        return

    if suffix == ".pdf":
        try:
            import fitz  # type: ignore

            document = fitz.open(path)
            for number, page in enumerate(document, start=1):
                yield (f"pdf-page:{number}", page.get_text("text"))
            metadata = document.metadata or {}
            yield ("pdf-metadata", json.dumps(metadata, ensure_ascii=False))
            document.close()
        except Exception:
            # A PDF that cannot be parsed must be reviewed by the caller.
            return


def _findings(text: str) -> Iterable[Tuple[str, int, int]]:
    valid_card_spans = []
    card_pattern = dict(RULES)["CREDIT_CARD_LIKE"]
    for card_match in card_pattern.finditer(text):
        card_value = card_match.group(0)
        card_digits = "".join(ch for ch in card_value if ch.isdigit())
        if card_digits and card_digits[0] in "3456" and _luhn(card_value):
            valid_card_spans.append((card_match.start(), card_match.end()))

    for rule_name, pattern in RULES:
        for match in pattern.finditer(text):
            value = match.group(0)
            if rule_name == "CREDIT_CARD_LIKE":
                digits = "".join(ch for ch in value if ch.isdigit())
                # Avoid treating mobile numbers and arbitrary long numbers as
                # cards; require a card-like leading digit and Luhn validity.
                if not digits or digits[0] not in "3456" or not _luhn(value):
                    continue
            # A formatted card number often also matches the broad phone rule.
            # Keep the higher-confidence card finding only.
            if rule_name == "PHONE_LIKE" and _luhn(value):
                continue
            if rule_name == "PHONE_LIKE" and any(
                match.start() < end and match.end() > start
                for start, end in valid_card_spans
            ):
                continue
            line = text.count("\n", 0, match.start()) + 1
            yield rule_name, line, 1


def scan(inputs: Sequence[Path], max_bytes: int) -> Dict[str, object]:
    findings: List[Dict[str, object]] = []
    summary: Dict[str, int] = {}
    files_scanned = 0
    files_unreadable: List[str] = []
    bytes_scanned = 0

    for path in iter_files(inputs):
        files_scanned += 1
        try:
            bytes_scanned += path.stat().st_size
        except OSError:
            pass
        surfaces = list(_iter_surfaces(path, max_bytes))
        if not surfaces:
            files_unreadable.append(str(path))
            continue
        for surface, text in surfaces:
            if not text:
                continue
            local_counts: Dict[str, int] = {}
            line_numbers: Dict[str, List[int]] = {}
            for rule, line, count in _findings(text):
                local_counts[rule] = local_counts.get(rule, 0) + count
                line_numbers.setdefault(rule, []).append(line)
                summary[rule] = summary.get(rule, 0) + count
            for rule, count in sorted(local_counts.items()):
                findings.append(
                    {
                        "path": str(path),
                        "surface": surface,
                        "rule": rule,
                        "count": count,
                        "lines": sorted(set(line_numbers[rule]))[:100],
                    }
                )

    status = "findings" if findings else "pass"
    if files_unreadable:
        status = "needs_review" if status == "pass" else status
    return {
        "status": status,
        "files_scanned": files_scanned,
        "bytes_scanned": bytes_scanned,
        "summary": dict(sorted(summary.items())),
        "findings": findings,
        "unreadable_or_unsupported": files_unreadable,
        "note": "No matched values are included; this is a baseline scan, not proof of anonymity.",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="Files or directories to scan")
    parser.add_argument("--max-bytes", type=int, default=25 * 1024 * 1024)
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args(argv)

    result = scan(args.paths, max(1, args.max_bytes))
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    if result["status"] == "findings":
        return 1
    if result["status"] == "needs_review":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
