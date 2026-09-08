#!/usr/bin/env python3
"""Run non-destructive postconditions against a redacted PDF.

The script checks the text layer and common hidden surfaces without printing
forbidden terms or metadata values.  A clean result is limited to the checks
requested; it is not a legal or absolute re-identification guarantee.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Sequence


def _read_terms(term_file: Path | None, terms: Sequence[str]) -> List[str]:
    values = [term for term in terms if term]
    if term_file:
        for line in term_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                values.append(line)
    # Preserve order while removing duplicate terms without exposing them later.
    return list(dict.fromkeys(values))


def _metadata_count(metadata: Dict[str, object] | None) -> int:
    if not metadata:
        return 0
    # `format` and `encryption` describe the container, not the author's
    # identity.  Count only privacy-relevant document properties.
    ignored = {"format", "encryption"}
    return sum(
        1
        for key, value in metadata.items()
        if key not in ignored and value not in (None, "", "null")
    )


def _annotation_count(page: object) -> int:
    try:
        annots = page.annots()
        return sum(1 for _ in annots) if annots else 0
    except Exception:
        return 0


def _widget_count(page: object) -> int:
    try:
        widgets = page.widgets()
        return sum(1 for _ in widgets) if widgets else 0
    except Exception:
        return 0


def verify(
    path: Path,
    terms: Sequence[str],
    require_clean_metadata: bool,
    require_no_annotations: bool,
    require_no_attachments: bool,
    require_no_forms: bool,
    require_no_links: bool,
) -> Dict[str, object]:
    try:
        import fitz  # type: ignore
    except ImportError:
        return {
            "status": "blocked",
            "error": "PyMuPDF is required; install it locally before verifying a PDF.",
        }

    try:
        document = fitz.open(path)
    except Exception as exc:
        return {"status": "blocked", "error": f"Could not open PDF: {type(exc).__name__}"}

    if document.is_encrypted:
        try:
            authenticated = bool(document.authenticate(""))
        except Exception:
            authenticated = False
        if not authenticated:
            document.close()
            return {"status": "blocked", "error": "Password-protected PDF; decrypt in an authorized local workflow first"}

    page_text: List[str] = []
    auxiliary_text: List[str] = []
    pages_with_images = 0
    pages_without_text_with_images = 0
    annotation_count = 0
    widget_count = 0
    link_count = 0
    for page in document:
        text = page.get_text("text") or ""
        page_text.append(text)
        try:
            image_count = len(page.get_images(full=True))
        except Exception:
            image_count = 0
        if image_count:
            pages_with_images += 1
            if not text.strip():
                pages_without_text_with_images += 1
        annotation_count += _annotation_count(page)
        widget_count += _widget_count(page)
        try:
            links = page.get_links()
            link_count += len(links)
            auxiliary_text.append(json.dumps(links, ensure_ascii=False))
        except Exception:
            pass
        try:
            widgets = page.widgets()
            if widgets:
                widget_values = []
                for widget in widgets:
                    widget_values.append(
                        {
                            "field_name": getattr(widget, "field_name", ""),
                            "field_value": getattr(widget, "field_value", ""),
                            "field_label": getattr(widget, "field_label", ""),
                        }
                    )
                auxiliary_text.append(json.dumps(widget_values, ensure_ascii=False))
        except Exception:
            pass

    all_text = "\n".join(page_text)
    metadata = document.metadata or {}
    auxiliary_text.append(json.dumps(metadata, ensure_ascii=False))
    try:
        auxiliary_text.append(json.dumps(document.get_toc(simple=False), ensure_ascii=False))
    except Exception:
        pass
    try:
        auxiliary_text.append(json.dumps(document.embfile_names(), ensure_ascii=False))
    except Exception:
        pass
    search_text = all_text + "\n" + "\n".join(auxiliary_text)
    term_matches = 0
    for term in terms:
        # Case-insensitive search is intentionally conservative.  The term is
        # never echoed in the report.
        term_matches += len(re.findall(re.escape(term), search_text, flags=re.IGNORECASE))

    metadata_count = _metadata_count(metadata)
    try:
        attachment_count = len(document.embfile_names())
    except Exception:
        attachment_count = 0
    try:
        bookmark_count = len(document.get_toc(simple=False))
    except Exception:
        bookmark_count = 0

    raw_markers = {
        "incremental_prev": 0,
        "javascript": 0,
        "embedded_files": 0,
        "launch_actions": 0,
        "xmp_metadata": 0,
    }
    try:
        raw = path.read_bytes()
        raw_markers["incremental_prev"] = len(re.findall(rb"/Prev\s+\d+", raw))
        raw_markers["javascript"] = len(re.findall(rb"/JavaScript|/JS\b", raw))
        raw_markers["embedded_files"] = len(re.findall(rb"/EmbeddedFiles\b", raw))
        raw_markers["launch_actions"] = len(re.findall(rb"/Launch\b", raw))
        raw_markers["xmp_metadata"] = len(re.findall(rb"/Metadata\b", raw))
    except OSError:
        pass

    checks: Dict[str, object] = {
        "forbidden_terms": {
            "status": "pass" if terms and term_matches == 0 else ("fail" if term_matches else "not_run"),
            "terms_checked": len(terms),
            "matches": term_matches,
        },
        "text_extraction": {"status": "pass", "pages": len(page_text), "characters": len(all_text)},
        "metadata": {
            "status": "fail" if require_clean_metadata and metadata_count else ("review" if metadata_count else "pass"),
            "non_empty_fields": metadata_count,
        },
        "annotations": {
            "status": "fail" if require_no_annotations and annotation_count else ("review" if annotation_count else "pass"),
            "count": annotation_count,
        },
        "forms": {
            "status": "fail" if require_no_forms and widget_count else ("review" if widget_count else "pass"),
            "count": widget_count,
        },
        "attachments": {
            "status": "fail" if require_no_attachments and attachment_count else ("review" if attachment_count else "pass"),
            "count": attachment_count,
        },
        "links": {
            "status": "fail" if require_no_links and link_count else ("review" if link_count else "pass"),
            "count": link_count,
        },
        "bookmarks": {"status": "review" if bookmark_count else "pass", "count": bookmark_count},
        "ocr_surface": {
            "status": "review" if pages_without_text_with_images else "pass",
            "pages_with_images": pages_with_images,
            "image_only_pages": pages_without_text_with_images,
        },
        "incremental_revisions": {
            "status": "review" if raw_markers["incremental_prev"] else "pass",
            "count": raw_markers["incremental_prev"],
        },
        "active_or_embedded_content": {
            "status": "review"
            if raw_markers["javascript"]
            or raw_markers["embedded_files"]
            or raw_markers["launch_actions"]
            else "pass",
            "javascript_markers": raw_markers["javascript"],
            "embedded_file_markers": raw_markers["embedded_files"],
            "launch_action_markers": raw_markers["launch_actions"],
        },
        "xmp_surface": {
            "status": "review" if raw_markers["xmp_metadata"] else "pass",
            "markers": raw_markers["xmp_metadata"],
        },
        "raw_file_markers": raw_markers,
    }

    statuses = []
    for value in checks.values():
        if isinstance(value, dict):
            statuses.append(value.get("status"))
    if not terms:
        status = "needs_review"
    elif "fail" in statuses:
        status = "fail"
    elif "review" in statuses:
        status = "needs_review"
    else:
        status = "pass"

    document.close()
    return {
        "status": status,
        "file": str(path),
        "checks": checks,
        "note": "Pass means only the requested postconditions passed; inspect rendered pages and policy-specific surfaces separately.",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--term", action="append", default=[], help="Forbidden term (never echoed in output)")
    parser.add_argument("--term-file", type=Path)
    parser.add_argument("--require-clean-metadata", action="store_true")
    parser.add_argument("--require-no-annotations", action="store_true")
    parser.add_argument("--require-no-attachments", action="store_true")
    parser.add_argument("--require-no-forms", action="store_true")
    parser.add_argument("--require-no-links", action="store_true")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    if not args.pdf.is_file():
        print(json.dumps({"status": "blocked", "error": "PDF path is not a file"}, ensure_ascii=False))
        return 2
    try:
        terms = _read_terms(args.term_file, args.term)
    except OSError:
        print(json.dumps({"status": "blocked", "error": "Could not read term file"}, ensure_ascii=False))
        return 2
    result = verify(
        args.pdf,
        terms,
        args.require_clean_metadata,
        args.require_no_annotations,
        args.require_no_attachments,
        args.require_no_forms,
        args.require_no_links,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return {"pass": 0, "needs_review": 3, "fail": 1, "blocked": 2}.get(result.get("status"), 2)


if __name__ == "__main__":
    sys.exit(main())
