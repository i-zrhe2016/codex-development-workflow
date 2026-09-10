#!/usr/bin/env python3
"""Scan staged Git file contents for common secrets and sensitive values.

The scanner never prints matched values. It scans the exact staged blob for
added/copied/modified/renamed paths and exits non-zero on findings or files that
cannot be safely inspected.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple


PatternRule = Tuple[str, re.Pattern[str], Callable[[str], bool] | None]


def _run_git(args: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _repo_root() -> Path:
    result = _run_git(["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        raise RuntimeError("not inside a Git repository")
    return Path(result.stdout.decode("utf-8").strip())


def _staged_paths(root: Path) -> List[str]:
    result = _run_git(
        ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"], cwd=root
    )
    if result.returncode != 0:
        raise RuntimeError("unable to list staged files")
    return [
        item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def _staged_blob(root: Path, path: str) -> bytes:
    result = _run_git(["show", f":{path}"], cwd=root)
    if result.returncode != 0:
        raise RuntimeError("unable to read staged blob")
    return result.stdout


def _is_obvious_dummy(value: str) -> bool:
    lower = value.lower()
    markers = (
        "redacted",
        "changeme",
        "change-me",
        "dummy",
        "placeholder",
        "example",
        "fake",
        "your_",
        "your-",
        "<secret>",
        "<token>",
        "${",
    )
    return any(marker in lower for marker in markers)


def _safe_email(value: str) -> bool:
    lower = value.lower()
    return lower.endswith("@example.com") or lower.endswith("@example.org") or lower.endswith("@example.net")


def _safe_ipv4(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
    except ValueError:
        return True
    if value in {"0.0.0.0", "127.0.0.1", "255.255.255.255"}:
        return True
    doc_ranges = (
        ipaddress.ip_network("192.0.2.0/24"),
        ipaddress.ip_network("198.51.100.0/24"),
        ipaddress.ip_network("203.0.113.0/24"),
    )
    return any(ip in network for network in doc_ranges)


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


def _valid_card(value: str) -> bool:
    digits = "".join(ch for ch in value if ch.isdigit())
    return bool(digits) and digits[0] in "3456" and _luhn(value)


RULES: Sequence[PatternRule] = (
    (
        "PRIVATE_KEY",
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.IGNORECASE),
        None,
    ),
    (
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
        None,
    ),
    ("AWS_ACCESS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), None),
    (
        "GITHUB_TOKEN",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
        None,
    ),
    (
        "OPENAI_API_KEY",
        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
        None,
    ),
    (
        "BEARER_TOKEN",
        re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+\-/=]{16,}"),
        _is_obvious_dummy,
    ),
    (
        "SECRET_ASSIGNMENT",
        re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|token|password|passwd|secret|client[_-]?secret|private[_-]?key)\b\s*[:=]\s*[\"']?([^\s,;\"']{6,})"
        ),
        _is_obvious_dummy,
    ),
    (
        "URL_SECRET_PARAMETER",
        re.compile(
            r"(?i)(?:[?&](?:token|access_token|apikey|api_key|password|passwd|secret|sig|signature)=)([^&#\s]+)"
        ),
        _is_obvious_dummy,
    ),
    (
        "EMAIL",
        re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE),
        _safe_email,
    ),
    (
        "IPV4",
        re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"),
        _safe_ipv4,
    ),
    (
        "CHINA_MOBILE",
        re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)"),
        None,
    ),
    (
        "CHINA_ID",
        re.compile(r"(?<![0-9Xx])\d{17}[0-9Xx](?![0-9Xx])"),
        None,
    ),
    (
        "SSN_LIKE",
        re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)"),
        None,
    ),
    (
        "CREDIT_CARD_LIKE",
        re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"),
        lambda value: not _valid_card(value),
    ),
)


def _match_value(rule: str, match: re.Match[str]) -> str:
    if rule in {"SECRET_ASSIGNMENT", "URL_SECRET_PARAMETER"} and match.lastindex:
        return match.group(1)
    if rule == "BEARER_TOKEN":
        return match.group(0).split(None, 1)[-1]
    return match.group(0)


def _findings(text: str) -> Iterable[Tuple[str, int]]:
    for rule, pattern, ignore_if in RULES:
        for match in pattern.finditer(text):
            value = _match_value(rule, match)
            if ignore_if and ignore_if(value):
                continue
            line = text.count("\n", 0, match.start()) + 1
            yield rule, line


def scan(root: Path, paths: Sequence[str], max_bytes: int) -> Dict[str, object]:
    findings: List[Dict[str, object]] = []
    summary: Dict[str, int] = {}
    needs_review: List[Dict[str, str]] = []
    scanned = 0

    for path in paths:
        try:
            data = _staged_blob(root, path)
        except RuntimeError:
            needs_review.append({"path": path, "reason": "unable_to_read_staged_blob"})
            continue

        if len(data) > max_bytes:
            needs_review.append({"path": path, "reason": "oversized"})
            continue
        if b"\0" in data[:8192]:
            needs_review.append({"path": path, "reason": "binary"})
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            needs_review.append({"path": path, "reason": "non_utf8"})
            continue

        scanned += 1
        per_rule: Dict[str, List[int]] = {}

        for rule, line in _findings(path):
            per_rule.setdefault(f"FILENAME_{rule}", []).append(0)
        for rule, line in _findings(text):
            per_rule.setdefault(rule, []).append(line)

        for rule, lines in sorted(per_rule.items()):
            unique_lines = sorted(set(lines))
            count = len(lines)
            summary[rule] = summary.get(rule, 0) + count
            findings.append(
                {
                    "path": path,
                    "rule": rule,
                    "count": count,
                    "lines": unique_lines[:100],
                }
            )

    if findings:
        status = "findings"
    elif needs_review:
        status = "needs_review"
    elif not paths:
        status = "noop"
    else:
        status = "pass"

    return {
        "status": status,
        "files_staged": len(paths),
        "files_scanned": scanned,
        "summary": dict(sorted(summary.items())),
        "findings": findings,
        "needs_review": needs_review,
        "note": "Matched values are never included in output.",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-bytes", type=int, default=5 * 1024 * 1024)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    try:
        root = _repo_root()
        paths = _staged_paths(root)
        result = scan(root, paths, max(1, args.max_bytes))
    except RuntimeError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 3

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    if result["status"] == "findings":
        return 1
    if result["status"] == "needs_review":
        return 2
    if result["status"] == "error":
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
