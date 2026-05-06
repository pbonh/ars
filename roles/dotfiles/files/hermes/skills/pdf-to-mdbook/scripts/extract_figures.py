#!/usr/bin/env python3
"""
extract_figures.py — Pull embedded figures from a PDF.

Combines two extractors so we don't miss either side:

  1. ``pdfimages -all`` (poppler) — embedded raster art, fast.
  2. PyMuPDF (``page.get_images()`` + ``doc.extract_image(xref)``) —
     captures vector-rendered figures pdfimages misses, plus raster
     images stored as alpha-masked XObjects that pdfimages
     occasionally drops.

Output naming:  ``figure_p{NNNN}_{M}.{ext}`` where ``NNNN`` is the
PDF page number (1-indexed) and ``M`` is the figure index on that
page.

Usage:
    python extract_figures.py input.pdf --out work/pages/images
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


def _have_pdfimages() -> bool:
    return shutil.which("pdfimages") is not None


def _run_pdfimages(pdf: str, out_dir: Path) -> list[Path]:
    """Run ``pdfimages -all`` into ``out_dir`` and return written paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if not _have_pdfimages():
        return []
    prefix = out_dir / "raw"
    try:
        subprocess.run(
            ["pdfimages", "-all", pdf, str(prefix)],
            capture_output=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"pdfimages failed: {e.stderr.decode(errors='ignore')[:300]}",
              file=sys.stderr)
        return []
    return sorted(out_dir.glob("raw-*"))


def _rename_pdfimages_outputs(pdf: str, raw_paths: list[Path],
                              out_dir: Path) -> list[dict]:
    """pdfimages doesn't tag outputs with page numbers; re-derive them
    via ``pdfimages -list`` and rename to our ``figure_pNNNN_M.ext``
    scheme.
    """
    if not raw_paths:
        return []
    if not _have_pdfimages():
        return []
    try:
        listing = subprocess.run(
            ["pdfimages", "-list", pdf],
            capture_output=True, check=True, text=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []

    # Header line, then per-image rows. The first column is the page
    # number, second is the index, eighth-ish is the type. We don't
    # parse precisely — we just need (page, index) tuples in order.
    page_per_image: list[int] = []
    for line in listing.splitlines()[2:]:
        parts = line.split()
        if not parts:
            continue
        if not parts[0].isdigit():
            continue
        page_per_image.append(int(parts[0]))

    page_counters: dict[int, int] = {}
    manifest: list[dict] = []
    for raw, page in zip(raw_paths, page_per_image):
        page_counters[page] = page_counters.get(page, 0) + 1
        idx = page_counters[page]
        ext = raw.suffix.lstrip(".") or "img"
        new_name = f"figure_p{page:04d}_{idx}.{ext}"
        new_path = out_dir / new_name
        try:
            raw.rename(new_path)
        except OSError:
            # cross-fs fallback
            shutil.copy(raw, new_path)
            raw.unlink(missing_ok=True)
        manifest.append({
            "file": new_name,
            "page": page,
            "index": idx,
            "source": "pdfimages",
        })
    return manifest


def _extract_with_pymupdf(pdf: str, out_dir: Path,
                          existing_pairs: set[tuple[int, int]]) -> list[dict]:
    """Capture vector + alpha-masked images that pdfimages skipped."""
    if not HAS_PYMUPDF:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    try:
        doc = fitz.open(pdf)
    except Exception as e:
        print(f"PyMuPDF cannot open {pdf}: {e}", file=sys.stderr)
        return []
    try:
        for page_index in range(len(doc)):
            page = doc[page_index]
            page_no = page_index + 1
            counter = sum(1 for (p, _i) in existing_pairs if p == page_no)
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    info = doc.extract_image(xref)
                except Exception:
                    continue
                ext = info.get("ext") or "png"
                data = info.get("image")
                if not data:
                    continue
                counter += 1
                fname = f"figure_p{page_no:04d}_{counter}.{ext}"
                fpath = out_dir / fname
                fpath.write_bytes(data)
                manifest.append({
                    "file": fname,
                    "page": page_no,
                    "index": counter,
                    "source": "pymupdf",
                    "xref": xref,
                })
                existing_pairs.add((page_no, counter))
    finally:
        doc.close()
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", required=True,
                    help="Output directory for figures (will hold "
                         "figure_pNNNN_M.* files plus figures_manifest.json)")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"ERROR: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw = _run_pdfimages(args.pdf, out_dir)
    pdf_manifest = _rename_pdfimages_outputs(args.pdf, raw, out_dir)
    seen = {(m["page"], m["index"]) for m in pdf_manifest}

    py_manifest = _extract_with_pymupdf(args.pdf, out_dir, seen)
    manifest = pdf_manifest + py_manifest

    # Write the manifest at the parent of the images dir so
    # assemble_chapters.py can find it next to the page directory.
    manifest_path = out_dir.parent / "figures_manifest.json"
    manifest_path.write_text(json.dumps(
        {"figures": manifest, "count": len(manifest)}, indent=2))

    print(f"Extracted {len(manifest)} figure(s) to {out_dir}")
    print(f"Manifest: {manifest_path}")
    if not _have_pdfimages():
        print("  (pdfimages not installed — install poppler-utils for "
              "raster extraction.)", file=sys.stderr)
    if not HAS_PYMUPDF:
        print("  (PyMuPDF not installed — vector figures may be missed. "
              "pip install pymupdf --break-system-packages)",
              file=sys.stderr)


if __name__ == "__main__":
    main()
