#!/usr/bin/env python3
"""
extract_text_pages.py — Extract text per page, write Markdown to disk.

Writes one file per page (page_0001.md, page_0002.md, ...) and a
manifest.json with per-page char counts and a `needs_ocr` flag for
low-text pages. The agent reads only the manifest, never the page
files (unless diagnosing a specific problem).

Usage:
    python extract_text_pages.py input.pdf --out work/pages
    python extract_text_pages.py input.pdf --out work/pages --start 50 --end 100
    python extract_text_pages.py input.pdf --out work/pages --layout
"""

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf --break-system-packages",
          file=sys.stderr)
    sys.exit(2)


LOW_TEXT_THRESHOLD = 100  # chars below which page is flagged needs_ocr

# Quality-gate thresholds. cid_count > 5 catches font-mapping failures
# (raw "(cid:139)" glyphs). median_word_length > 12 catches space-collapse
# (pdftotext occasionally drops all spaces, producing one giant token).
CID_THRESHOLD = 5
MEDIAN_WORD_LEN_THRESHOLD = 12

_CID_RE = re.compile(r"\(cid:\d+\)")


def _quality_signals(text: str) -> tuple[int, float]:
    """Return (cid_count, median_word_length) for quality gating."""
    cid_count = len(_CID_RE.findall(text))
    words = [w for w in text.split() if w]
    if not words:
        return cid_count, 0.0
    lens = [len(w) for w in words]
    return cid_count, float(statistics.median(lens))


def _classify_quality(text: str, threshold_chars: int) -> tuple[str, dict]:
    """Bucket the page's extraction quality. Returns (label, signals)."""
    cid_count, mwl = _quality_signals(text)
    chars = len(text)
    poor = (
        cid_count > CID_THRESHOLD
        or mwl > MEDIAN_WORD_LEN_THRESHOLD
        # Tiny pages: only flag as poor if not effectively blank-by-design
        # (a true blank page yields chars==0; sub-threshold but non-trivial
        # text usually means extraction faltered).
        or (10 < chars < threshold_chars)
    )
    label = "poor" if poor else "good"
    return label, {"cid_count": cid_count, "median_word_length": mwl}


def _extract_with_pymupdf(pdf_path: str, page_idx: int) -> str:
    """Fallback page extraction via PyMuPDF (different font logic)."""
    if not HAS_PYMUPDF:
        return ""
    try:
        with fitz.open(pdf_path) as doc:
            if page_idx >= len(doc):
                return ""
            return doc[page_idx].get_text("text") or ""
    except Exception:
        return ""


def have_pdftotext() -> bool:
    try:
        subprocess.run(["pdftotext", "-v"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def extract_with_pdftotext(pdf: str, page: int, layout: bool) -> str:
    """Use pdftotext for one page. `page` is 1-indexed."""
    cmd = ["pdftotext", "-f", str(page), "-l", str(page)]
    if layout:
        cmd.append("-layout")
    cmd += [pdf, "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout
    except subprocess.CalledProcessError as e:
        return ""


def extract_with_pdfplumber(pdf_obj, idx: int) -> str:
    """idx is 0-indexed."""
    try:
        if idx >= len(pdf_obj.pages):
            return ""
        return pdf_obj.pages[idx].extract_text() or ""
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", required=True,
                    help="Output directory for page files and manifest.json")
    ap.add_argument("--start", type=int, default=1,
                    help="First page to extract, 1-indexed (default: 1)")
    ap.add_argument("--end", type=int, default=None,
                    help="Last page to extract, 1-indexed (default: last)")
    ap.add_argument("--layout", action="store_true",
                    help="Use pdftotext --layout (better for multi-column)")
    ap.add_argument("--threshold", type=int, default=LOW_TEXT_THRESHOLD,
                    help=f"Char count below which a page needs_ocr "
                         f"(default: {LOW_TEXT_THRESHOLD})")
    ap.add_argument("--engine", choices=["auto", "pdftotext", "pdfplumber"],
                    default="auto",
                    help="Extraction engine (default: auto)")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"ERROR: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(args.pdf)
        total_pages = len(reader.pages)
    except Exception as e:
        print(f"ERROR: cannot read PDF: {e}", file=sys.stderr)
        sys.exit(1)

    start = max(1, args.start)
    end = min(total_pages, args.end) if args.end else total_pages
    if start > end:
        print(f"ERROR: start {start} > end {end}", file=sys.stderr)
        sys.exit(1)

    # Pick engine
    if args.engine == "auto":
        if args.layout and have_pdftotext():
            engine = "pdftotext"
        elif HAS_PDFPLUMBER:
            engine = "pdfplumber"
        elif have_pdftotext():
            engine = "pdftotext"
        else:
            print("ERROR: neither pdfplumber nor pdftotext available",
                  file=sys.stderr)
            sys.exit(2)
    else:
        engine = args.engine

    print(f"Engine: {engine}  |  Pages {start}..{end}  |  Out: {out_dir}",
          file=sys.stderr)

    pages_meta: list[dict] = []

    def finalize_page(p: int, text: str, primary_engine: str) -> dict:
        """Quality-gate the page text; retry with PyMuPDF if poor."""
        quality, signals = _classify_quality(text, args.threshold)
        used_engine = primary_engine
        fallback_used = False
        if quality == "poor" and HAS_PYMUPDF:
            alt = _extract_with_pymupdf(args.pdf, p - 1)
            if alt:
                alt_quality, alt_signals = _classify_quality(alt, args.threshold)
                # Accept the fallback when it's no worse on either signal —
                # PyMuPDF's font logic differs from pdftotext's, so it
                # often recovers space-collapse and (cid:) cases.
                if alt_quality == "good" or (
                    alt_signals["cid_count"] < signals["cid_count"]
                    or alt_signals["median_word_length"] < signals["median_word_length"]
                ):
                    text = alt
                    quality, signals = alt_quality, alt_signals
                    used_engine = "pymupdf"
                    fallback_used = True
        fname = out_dir / f"page_{p:04d}.md"
        fname.write_text(text)
        chars = len(text)
        # Re-classify after potential fallback for the final manifest record.
        # needs_ocr fires when text density is below threshold OR quality
        # remained poor after fallback (font-mapping failures + space
        # collapse aren't recoverable without a re-render).
        needs_ocr = chars < args.threshold or quality == "poor"
        return {
            "page": p,
            "file": fname.name,
            "chars": chars,
            "needs_ocr": needs_ocr,
            "extraction_quality": quality,
            "cid_count": signals["cid_count"],
            "median_word_length": signals["median_word_length"],
            "engine_used": used_engine,
            "pymupdf_fallback": fallback_used,
        }

    if engine == "pdfplumber":
        with pdfplumber.open(args.pdf) as pdf_obj:
            for p in range(start, end + 1):
                text = extract_with_pdfplumber(pdf_obj, p - 1)
                pages_meta.append(finalize_page(p, text, "pdfplumber"))
                if p % 25 == 0 or p == end:
                    last = pages_meta[-1]
                    print(f"  page {p}/{end}  ({last['chars']} chars, "
                          f"{last['extraction_quality']})", file=sys.stderr)
    else:  # pdftotext
        for p in range(start, end + 1):
            text = extract_with_pdftotext(args.pdf, p, args.layout)
            pages_meta.append(finalize_page(p, text, "pdftotext"))
            if p % 25 == 0 or p == end:
                last = pages_meta[-1]
                print(f"  page {p}/{end}  ({last['chars']} chars, "
                      f"{last['extraction_quality']})", file=sys.stderr)

    needs_ocr = [m["page"] for m in pages_meta if m["needs_ocr"]]
    poor_pages = [m["page"] for m in pages_meta
                  if m.get("extraction_quality") == "poor"]
    fallback_pages = [m["page"] for m in pages_meta
                      if m.get("pymupdf_fallback")]
    manifest = {
        "pdf": os.path.abspath(args.pdf),
        "engine": engine,
        "layout": args.layout,
        "threshold": args.threshold,
        "page_range": [start, end],
        "total_pages_in_pdf": total_pages,
        "pages": pages_meta,
        "summary": {
            "extracted": len(pages_meta),
            "needs_ocr_count": len(needs_ocr),
            "needs_ocr_pages": needs_ocr,
            "poor_quality_count": len(poor_pages),
            "poor_quality_pages": poor_pages,
            "pymupdf_fallback_count": len(fallback_pages),
            "pymupdf_fallback_pages": fallback_pages,
            "total_chars": sum(m["chars"] for m in pages_meta),
            "avg_chars_per_page": (
                sum(m["chars"] for m in pages_meta) // max(1, len(pages_meta))
            ),
        },
    }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"\nWrote {len(pages_meta)} pages to {out_dir}")
    print(f"Manifest: {manifest_path}")
    s = manifest["summary"]
    print(f"  extracted={s['extracted']}  "
          f"avg_chars={s['avg_chars_per_page']}  "
          f"needs_ocr={s['needs_ocr_count']}  "
          f"poor_quality={s['poor_quality_count']}  "
          f"pymupdf_fallback={s['pymupdf_fallback_count']}")
    if needs_ocr:
        preview = ", ".join(str(p) for p in needs_ocr[:10])
        more = f" ... +{len(needs_ocr) - 10} more" if len(needs_ocr) > 10 else ""
        print(f"  needs_ocr pages: {preview}{more}")
    if poor_pages:
        preview = ", ".join(str(p) for p in poor_pages[:10])
        more = f" ... +{len(poor_pages) - 10} more" if len(poor_pages) > 10 else ""
        print(f"  poor_quality pages: {preview}{more}")
    if not HAS_PYMUPDF:
        print("  (PyMuPDF not installed — install for fallback on poor pages: "
              "pip install pymupdf --break-system-packages)",
              file=sys.stderr)


if __name__ == "__main__":
    main()
