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
import subprocess
import sys
from pathlib import Path

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf --break-system-packages",
          file=sys.stderr)
    sys.exit(2)


LOW_TEXT_THRESHOLD = 100  # chars below which page is flagged needs_ocr


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

    if engine == "pdfplumber":
        with pdfplumber.open(args.pdf) as pdf_obj:
            for p in range(start, end + 1):
                text = extract_with_pdfplumber(pdf_obj, p - 1)
                fname = out_dir / f"page_{p:04d}.md"
                fname.write_text(text)
                chars = len(text)
                pages_meta.append({
                    "page": p,
                    "file": fname.name,
                    "chars": chars,
                    "needs_ocr": chars < args.threshold,
                })
                if p % 25 == 0 or p == end:
                    print(f"  page {p}/{end}  ({chars} chars)", file=sys.stderr)
    else:  # pdftotext
        for p in range(start, end + 1):
            text = extract_with_pdftotext(args.pdf, p, args.layout)
            fname = out_dir / f"page_{p:04d}.md"
            fname.write_text(text)
            chars = len(text)
            pages_meta.append({
                "page": p,
                "file": fname.name,
                "chars": chars,
                "needs_ocr": chars < args.threshold,
            })
            if p % 25 == 0 or p == end:
                print(f"  page {p}/{end}  ({chars} chars)", file=sys.stderr)

    needs_ocr = [m["page"] for m in pages_meta if m["needs_ocr"]]
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
          f"needs_ocr={s['needs_ocr_count']}")
    if needs_ocr:
        preview = ", ".join(str(p) for p in needs_ocr[:10])
        more = f" ... +{len(needs_ocr) - 10} more" if len(needs_ocr) > 10 else ""
        print(f"  needs_ocr pages: {preview}{more}")


if __name__ == "__main__":
    main()
