#!/usr/bin/env python3
"""
extract_outline.py — Pull bookmarks/outline from a PDF.

Outputs an outline.json file with the chapter structure. If the PDF
has no embedded outline, writes {"has_outline": false} so the agent
can fall back to TOC-page rasterization or heuristic detection (see
reference/structure.md).

Usage:
    python extract_outline.py input.pdf --out outline.json
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

try:
    from pypdf import PdfReader
    from pypdf.generic import Destination
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf --break-system-packages",
          file=sys.stderr)
    sys.exit(2)


def slugify(title: str, max_len: int = 60) -> str:
    """Turn 'Chapter 3: The Beginning!' into 'chapter-3-the-beginning'."""
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lower = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "section"


# Bookmarks generated from filenames during PDF concatenation are
# common in scanned/republished books and look like ``01.pdf``,
# ``appG.pdf``, or ``chapter02.pdf``. Treat them as missing-outline so
# the agent falls back to detect_structure.py instead of trying to
# build a book whose chapter titles are filenames.
GARBAGE_TITLE = re.compile(
    r"^(?:[\w\-]+\.pdf|page[_\- ]?\d+|booktext|untitled[_\- ]?\d*)$",
    re.IGNORECASE,
)


def is_garbage_title(t: str) -> bool:
    return bool(GARBAGE_TITLE.match(t.strip()))


def get_page_number(reader: PdfReader, dest) -> int | None:
    """Convert a Destination to a 1-indexed PDF page number."""
    try:
        idx = reader.get_destination_page_number(dest)
        if idx is not None:
            return idx + 1
    except Exception:
        pass
    return None


def walk_outline(reader: PdfReader, node, level: int, out: list,
                 used_slugs: set):
    """Recurse over the outline tree, building flat list of items."""
    for item in node:
        if isinstance(item, list):
            walk_outline(reader, item, level + 1, out, used_slugs)
        elif isinstance(item, Destination):
            title = (item.title or "").strip()
            if not title:
                continue
            page = get_page_number(reader, item)
            base_slug = slugify(title)
            slug = base_slug
            n = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{n}"
                n += 1
            used_slugs.add(slug)
            out.append({
                "title": title,
                "level": level,
                "page": page,
                "slug": slug,
            })


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", required=True, help="Output JSON path")
    ap.add_argument("--max-level", type=int, default=3,
                    help="Maximum outline nesting level to keep (default: 3)")
    args = ap.parse_args()

    try:
        reader = PdfReader(args.pdf)
    except Exception as e:
        print(f"ERROR: cannot read PDF: {e}", file=sys.stderr)
        sys.exit(1)

    items: list[dict] = []
    used: set[str] = set()
    try:
        outline = reader.outline
        walk_outline(reader, outline, level=1, out=items, used_slugs=used)
    except Exception as e:
        print(f"WARNING: error walking outline: {e}", file=sys.stderr)

    items = [it for it in items if it["level"] <= args.max_level]
    items = [it for it in items if it["page"] is not None]
    items.sort(key=lambda it: (it["page"], it["level"]))

    # Reject outlines whose titles are auto-generated filenames or
    # placeholders. These come from scanners/concatenators and are
    # never useful chapter titles. The agent should fall through to
    # detect_structure.py for a real outline.
    garbage_count = sum(1 for it in items if is_garbage_title(it["title"]))
    garbage = items and garbage_count / len(items) > 0.5
    if garbage:
        result = {
            "has_outline": False,
            "items": [],
            "source": "none",
            "rejected_garbage_outline": {
                "count": len(items),
                "garbage_titles": garbage_count,
                "sample": [it["title"] for it in items[:5]],
            },
        }
    else:
        result = {
            "has_outline": len(items) > 0,
            "items": items,
            "source": "pdf-bookmarks" if items else "none",
        }

    Path(args.out).write_text(json.dumps(result, indent=2))
    print(f"Wrote {args.out}")
    if garbage:
        print(f"Rejected {len(items)} outline items: titles look like "
              f"auto-generated filenames "
              f"(e.g. {result['rejected_garbage_outline']['sample'][:3]}). "
              f"Falling back: run detect_structure.py next.")
    elif items:
        print(f"Found {len(items)} outline items "
              f"({sum(1 for i in items if i['level'] == 1)} top-level)")
        for it in items[:8]:
            indent = "  " * (it["level"] - 1)
            print(f"  {indent}p.{it['page']:>4}: {it['title']}")
        if len(items) > 8:
            print(f"  ... and {len(items) - 8} more")
    else:
        print("No outline found. See reference/structure.md for fallbacks.")


if __name__ == "__main__":
    main()
