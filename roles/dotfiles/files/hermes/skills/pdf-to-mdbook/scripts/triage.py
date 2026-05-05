#!/usr/bin/env python3
"""
triage.py — Quick PDF metrics so the agent can choose a pipeline.

Reads a PDF, samples text density across the document, checks for
bookmarks, and returns a small JSON summary. NO page contents go to
stdout — only metrics. This keeps the agent's context lean.

Usage:
    python triage.py input.pdf [--out triage.json]
"""

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf --break-system-packages",
          file=sys.stderr)
    sys.exit(2)

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


SAMPLE_TARGET = 7  # number of pages to sample for text density
LOW_TEXT_THRESHOLD = 100  # chars below which a page looks scanned


def sample_indices(total: int, n: int) -> list[int]:
    """Pick n evenly-spaced page indices, including first and last."""
    if total <= n:
        return list(range(total))
    step = (total - 1) / (n - 1)
    return sorted({int(round(i * step)) for i in range(n)})


def page_chars(pdf_path: str, idx: int) -> int:
    """Return number of characters extractable from page idx (0-indexed)."""
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if idx < len(pdf.pages):
                    text = pdf.pages[idx].extract_text() or ""
                    return len(text)
        except Exception:
            pass
    # Fallback to pypdf
    try:
        reader = PdfReader(pdf_path)
        if idx < len(reader.pages):
            text = reader.pages[idx].extract_text() or ""
            return len(text)
    except Exception:
        pass
    return 0


def count_bookmarks(reader: PdfReader) -> int:
    """Count outline items recursively. Returns 0 on failure."""
    try:
        outline = reader.outline
    except Exception:
        return 0

    def walk(node):
        n = 0
        for item in node:
            if isinstance(item, list):
                n += walk(item)
            else:
                n += 1
        return n

    try:
        return walk(outline)
    except Exception:
        return 0


def classify(densities: list[int]) -> tuple[str, str]:
    """Return (scanned_estimate, recommended_pipeline)."""
    if not densities:
        return "unknown", "text"
    low = sum(1 for d in densities if d < LOW_TEXT_THRESHOLD)
    high = sum(1 for d in densities if d >= LOW_TEXT_THRESHOLD)
    if low == 0:
        return "text", "text"
    if high == 0:
        return "scanned", "ocr"
    # Mixed
    if low / len(densities) > 0.6:
        return "mostly_scanned", "ocr"
    return "hybrid", "hybrid"


def warnings_for(densities: list[int], indices: list[int],
                 page_count: int) -> list[str]:
    out = []
    # Cover-page detection: very low text on first/last sampled pages
    if densities and indices:
        if indices[0] == 0 and densities[0] < 30:
            out.append("page 1 looks like a cover (very low text)")
        if indices[-1] == page_count - 1 and densities[-1] < 30:
            out.append(f"page {page_count} looks like a cover (very low text)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", help="Optional path to write JSON; default stdout")
    ap.add_argument("--samples", type=int, default=SAMPLE_TARGET,
                    help=f"Number of pages to sample (default: {SAMPLE_TARGET})")
    args = ap.parse_args()

    pdf_path = args.pdf
    if not os.path.exists(pdf_path):
        print(f"ERROR: {pdf_path} not found", file=sys.stderr)
        sys.exit(1)

    size_mb = round(os.path.getsize(pdf_path) / (1024 * 1024), 2)

    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        print(f"ERROR: cannot read PDF: {e}", file=sys.stderr)
        sys.exit(1)

    page_count = len(reader.pages)
    bm_count = count_bookmarks(reader)
    has_bm = bm_count > 0

    indices = sample_indices(page_count, args.samples)
    densities = [page_chars(pdf_path, i) for i in indices]
    scanned, recommended = classify(densities)
    warns = warnings_for(densities, indices, page_count)

    if recommended == "ocr":
        # Rough estimate: 2 sec/page Tesseract @ 300dpi
        est_minutes = round(page_count * 2 / 60, 1)
        warns.append(f"OCR estimate: ~{est_minutes} minutes for full document")

    result = {
        "pdf": os.path.abspath(pdf_path),
        "pages": page_count,
        "size_mb": size_mb,
        "has_bookmarks": has_bm,
        "bookmark_count": bm_count,
        "sample_pages": [i + 1 for i in indices],  # 1-indexed for humans
        "sample_text_density": densities,
        "scanned_estimate": scanned,
        "recommended_pipeline": recommended,
        "warnings": warns,
    }

    out_text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(out_text)
        print(f"Wrote {args.out}")
        print(out_text)
    else:
        print(out_text)


if __name__ == "__main__":
    main()
