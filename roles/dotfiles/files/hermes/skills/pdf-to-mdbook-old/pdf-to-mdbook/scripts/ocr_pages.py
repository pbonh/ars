#!/usr/bin/env python3
"""
ocr_pages.py — OCR each page of a PDF, write Markdown to disk.

Rasterizes pages with pdftoppm, OCRs with Tesseract, writes
page_NNNN.md files. Skips pages whose .md is already present (resume
support). Updates manifest.json incrementally so progress is visible
to the supervising agent.

Usage:
    # Whole document
    python ocr_pages.py input.pdf --out work/pages --dpi 300 --lang eng

    # Specific page list/ranges
    python ocr_pages.py input.pdf --out work/pages --pages 47-52,89,142-145

    # Re-OCR only pages flagged as needs_ocr in an existing manifest
    python ocr_pages.py input.pdf --out work/pages \\
        --from-manifest work/pages/manifest.json
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf --break-system-packages",
          file=sys.stderr)
    sys.exit(2)


def check_tools():
    missing = []
    for tool in ("pdftoppm", "tesseract"):
        if shutil.which(tool) is None:
            missing.append(tool)
    if missing:
        print(f"ERROR: missing required tools: {', '.join(missing)}",
              file=sys.stderr)
        print("Install with:", file=sys.stderr)
        print("  apt-get install poppler-utils tesseract-ocr  # Debian/Ubuntu",
              file=sys.stderr)
        print("  brew install poppler tesseract               # macOS",
              file=sys.stderr)
        sys.exit(2)


def parse_pages_arg(spec: str, max_page: int) -> list[int]:
    """Parse '1,5-7,12' into [1, 5, 6, 7, 12]."""
    out: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            for p in range(int(a), int(b) + 1):
                if 1 <= p <= max_page:
                    out.add(p)
        else:
            p = int(chunk)
            if 1 <= p <= max_page:
                out.add(p)
    return sorted(out)


def ocr_one_page(pdf: str, page: int, dpi: int, lang: str, psm: int,
                 preprocess: str | None) -> str:
    """Rasterize page (1-indexed) and OCR it. Returns text."""
    with tempfile.TemporaryDirectory() as tmp:
        prefix = os.path.join(tmp, "p")
        # pdftoppm -png -r DPI -f N -l N input prefix
        cmd = ["pdftoppm", "-png", "-r", str(dpi),
               "-f", str(page), "-l", str(page), pdf, prefix]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            return f"<!-- pdftoppm failed for page {page}: {e.stderr.decode()} -->"

        # Find the produced image (zero-padded by pdftoppm based on page count)
        produced = sorted(Path(tmp).glob("p-*.png"))
        if not produced:
            return f"<!-- no image produced for page {page} -->"
        img_path = str(produced[0])

        # Optional preprocessing
        if preprocess == "unpaper" and shutil.which("unpaper"):
            clean = img_path.replace(".png", ".clean.png")
            subprocess.run(["unpaper", "--no-noisefilter", img_path, clean],
                           capture_output=True)
            if os.path.exists(clean):
                img_path = clean

        # Tesseract → stdout
        cmd = ["tesseract", img_path, "stdout",
               "-l", lang, "--psm", str(psm)]
        try:
            r = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return r.stdout
        except subprocess.CalledProcessError as e:
            return f"<!-- tesseract failed for page {page}: {e.stderr} -->"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", required=True, help="Output directory for page files")
    ap.add_argument("--pages", help="Page list/ranges, e.g. '1,5-7,12'")
    ap.add_argument("--from-manifest",
                    help="Path to manifest.json; OCR only its needs_ocr pages")
    ap.add_argument("--dpi", type=int, default=300, help="Rasterization DPI")
    ap.add_argument("--lang", default="eng",
                    help="Tesseract language (e.g. eng, deu, eng+deu)")
    ap.add_argument("--psm", type=int, default=3,
                    help="Tesseract page-segmentation mode (default: 3; "
                         "try 1 for academic books, 6 for single column)")
    ap.add_argument("--preprocess", choices=["none", "unpaper"], default="none",
                    help="Pre-OCR cleanup")
    ap.add_argument("--force", action="store_true",
                    help="Re-OCR pages even if their .md file already exists")
    args = ap.parse_args()

    check_tools()

    if not os.path.exists(args.pdf):
        print(f"ERROR: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        reader = PdfReader(args.pdf)
        total = len(reader.pages)
    except Exception as e:
        print(f"ERROR: cannot read PDF: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine page set
    if args.from_manifest:
        m = json.loads(Path(args.from_manifest).read_text())
        target_pages = [p["page"] for p in m["pages"] if p.get("needs_ocr")]
        if not target_pages:
            print("Manifest reports no pages needing OCR. Nothing to do.")
            return
    elif args.pages:
        target_pages = parse_pages_arg(args.pages, total)
    else:
        target_pages = list(range(1, total + 1))

    print(f"OCR plan: {len(target_pages)} pages, dpi={args.dpi}, lang={args.lang}, psm={args.psm}",
          file=sys.stderr)

    preprocess = None if args.preprocess == "none" else args.preprocess

    done = 0
    skipped = 0
    pages_meta = []
    for p in target_pages:
        fname = out_dir / f"page_{p:04d}.md"
        if fname.exists() and not args.force:
            skipped += 1
            text = fname.read_text()
        else:
            text = ocr_one_page(args.pdf, p, args.dpi, args.lang,
                                args.psm, preprocess)
            fname.write_text(text)
            done += 1
            if done % 5 == 0 or p == target_pages[-1]:
                print(f"  ocr {done}/{len(target_pages) - skipped}: page {p} → {len(text)} chars",
                      file=sys.stderr)

        pages_meta.append({
            "page": p,
            "file": fname.name,
            "chars": len(text),
            "needs_ocr": False,  # we just OCR'd it
        })

    # Merge into existing manifest if present, else write fresh
    manifest_path = out_dir / "manifest.json"
    if manifest_path.exists():
        m = json.loads(manifest_path.read_text())
        existing = {p["page"]: p for p in m.get("pages", [])}
        for entry in pages_meta:
            existing[entry["page"]] = entry
        m["pages"] = sorted(existing.values(), key=lambda x: x["page"])
        m["engine"] = m.get("engine", "tesseract") + "+ocr_pages"
        m["summary"] = {
            "extracted": len(m["pages"]),
            "needs_ocr_count": sum(1 for p in m["pages"] if p.get("needs_ocr")),
            "total_chars": sum(p["chars"] for p in m["pages"]),
            "avg_chars_per_page": (sum(p["chars"] for p in m["pages"])
                                   // max(1, len(m["pages"]))),
        }
    else:
        m = {
            "pdf": os.path.abspath(args.pdf),
            "engine": "tesseract",
            "dpi": args.dpi,
            "lang": args.lang,
            "psm": args.psm,
            "page_range": [min(target_pages), max(target_pages)],
            "total_pages_in_pdf": total,
            "pages": sorted(pages_meta, key=lambda x: x["page"]),
            "summary": {
                "extracted": len(pages_meta),
                "needs_ocr_count": 0,
                "total_chars": sum(p["chars"] for p in pages_meta),
                "avg_chars_per_page": (sum(p["chars"] for p in pages_meta)
                                       // max(1, len(pages_meta))),
            },
        }

    manifest_path.write_text(json.dumps(m, indent=2))

    print(f"\nDone. OCR'd {done} pages, skipped {skipped} (already existed).")
    print(f"Manifest: {manifest_path}")
    print(f"  total pages in manifest: {len(m['pages'])}")
    print(f"  avg chars/page: {m['summary']['avg_chars_per_page']}")


if __name__ == "__main__":
    main()
