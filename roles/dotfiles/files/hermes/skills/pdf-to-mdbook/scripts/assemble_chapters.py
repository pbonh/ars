#!/usr/bin/env python3
"""
assemble_chapters.py — Group page Markdown into chapters using outline.json.

For each outline item, concatenates its pages, runs cleanup (de-
hyphenation, header/footer stripping, blank-line collapse, heading
normalization), writes one chapter Markdown file. Then writes a draft
SUMMARY.md following mdBook's strict format.

Usage:
    python assemble_chapters.py \\
        --pages work/pages \\
        --outline work/outline.json \\
        --out work/chapters

    # If you don't have an outline, use heuristic detection:
    python assemble_chapters.py \\
        --pages work/pages \\
        --detect-headings \\
        --out work/chapters
"""

import argparse
import collections
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path


# --- Cleanup primitives ---

LIGATURES = {
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
    "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "ft", "\ufb06": "st",
}


def normalize_ligatures(text: str) -> str:
    for k, v in LIGATURES.items():
        text = text.replace(k, v)
    return text


def dehyphenate(text: str) -> str:
    """Join 'compre-\\nhensive' → 'comprehensive'.

    Heuristic: a hyphen at end of line followed by a lowercase letter
    on the next line is almost always a soft break. We don't join when
    the second part starts with uppercase (likely a real compound or
    proper noun). Allow arbitrary intervening whitespace (including a
    blank line) so this catches both line-break and page-break splits.
    """
    return re.sub(r"(\w)-\n[ \t]*\n?[ \t]*([a-z])", r"\1\2", text)


def collapse_blanklines(text: str) -> str:
    """3+ blank lines → 2 (single paragraph break)."""
    return re.sub(r"\n{3,}", "\n\n", text)


def strip_repeated_lines(pages_text: list[str], frac: float = 0.5) -> list[str]:
    """Find lines (top 3 + bottom 3 of each page) that recur on >frac of
    pages and remove them. Catches running headers and footers."""
    if not pages_text:
        return pages_text

    candidates: collections.Counter = collections.Counter()
    page_count = len(pages_text)

    for page in pages_text:
        lines = page.splitlines()
        # Take meaningful (non-empty, not pure-numeric-page-number-only) lines
        # from the top 3 and bottom 3
        top = [l.strip() for l in lines[:3] if l.strip()]
        bot = [l.strip() for l in lines[-3:] if l.strip()]
        for l in set(top + bot):
            # Don't dedupe pure page numbers as "running headers" — handle
            # them separately below
            if re.fullmatch(r"\d{1,4}", l):
                continue
            if 3 <= len(l) <= 80:
                candidates[l] += 1

    threshold = frac * page_count
    repeated = {line for line, count in candidates.items() if count >= threshold}

    # Also strip standalone numeric lines (page numbers) anywhere in top 3 / bot 3
    cleaned_pages = []
    for page in pages_text:
        lines = page.splitlines()
        new = []
        for i, l in enumerate(lines):
            stripped = l.strip()
            in_edge = i < 3 or i >= len(lines) - 3
            if in_edge:
                if stripped in repeated:
                    continue
                if re.fullmatch(r"\d{1,4}", stripped):
                    continue
            new.append(l)
        cleaned_pages.append("\n".join(new))

    return cleaned_pages


def normalize_chapter_heading(chapter_md: str, title: str) -> str:
    """Ensure chapter starts with a single `# Title` line."""
    chapter_md = chapter_md.lstrip()
    # If first non-blank line already starts with '#', keep as is (but
    # normalize to one h1)
    first_line = chapter_md.split("\n", 1)[0] if chapter_md else ""
    if first_line.startswith("#"):
        return chapter_md
    return f"# {title}\n\n{chapter_md}"


# --- Outline handling ---


def slugify(title: str, max_len: int = 60) -> str:
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    lower = ascii_only.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lower).strip("-")
    return (slug[:max_len].rstrip("-") or "section")


def load_outline(path: str) -> list[dict]:
    """Return list of {title, level, page, slug} sorted by page."""
    data = json.loads(Path(path).read_text())
    if not data.get("has_outline"):
        return []
    items = data["items"]
    # Ensure slugs exist
    used = set()
    for it in items:
        slug = it.get("slug") or slugify(it["title"])
        base = slug
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        it["slug"] = slug
        used.add(slug)
    return items


def detect_headings(pages_dir: Path, manifest: dict) -> list[dict]:
    """Heuristic chapter detection from page contents."""
    items = []
    chapter_re = re.compile(
        r"^\s*(?:CHAPTER|Chapter|PART|Part|BOOK|Book)\s+(?:[IVXLCDM]+|\d+|\w+)"
        r"\b.*$",
        re.MULTILINE,
    )
    used = set()
    for entry in manifest["pages"]:
        page_no = entry["page"]
        text = (pages_dir / entry["file"]).read_text()
        # Look at first ~10 non-empty lines
        lines = [l.strip() for l in text.splitlines() if l.strip()][:10]
        for line in lines:
            if chapter_re.match(line):
                title = line.strip()
                slug = slugify(title)
                base = slug
                n = 2
                while slug in used:
                    slug = f"{base}-{n}"
                    n += 1
                used.add(slug)
                items.append({"title": title, "level": 1, "page": page_no,
                              "slug": slug})
                break
    return items


# --- Assembly ---


def assemble(outline: list[dict], pages_dir: Path, manifest: dict,
             out_dir: Path, header_strip_frac: float) -> list[dict]:
    """For each outline item, write a chapter Markdown file."""
    if not outline:
        # Single-chapter fallback
        outline = [{"title": "Document", "level": 1, "page": 1,
                    "slug": "document"}]

    # Build per-item page range: [start_page, next_item_start_page)
    sorted_pages = sorted(p["page"] for p in manifest["pages"])
    last_page = sorted_pages[-1] if sorted_pages else 1
    items_by_page = sorted(outline, key=lambda x: x["page"])

    ranges = []
    for i, item in enumerate(items_by_page):
        start = item["page"]
        # Each item ends where the next item begins, regardless of level.
        # This keeps a parent chapter's pages from absorbing all of its
        # children's pages (which would duplicate every subsection's
        # content into the parent file).
        if i + 1 < len(items_by_page):
            end = items_by_page[i + 1]["page"] - 1
        else:
            end = last_page
        # Outline items that share a page (anthologies, multi-section spreads)
        # get a 1-page span instead of an inverted range.
        if end < start:
            end = start
        ranges.append({"item": item, "start": start, "end": end})

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for r in ranges:
        item = r["item"]
        # Gather page texts in range
        page_texts = []
        for entry in manifest["pages"]:
            p = entry["page"]
            if r["start"] <= p <= r["end"]:
                content = (pages_dir / entry["file"]).read_text()
                page_texts.append(content)

        # Cleanup pipeline
        page_texts = strip_repeated_lines(page_texts, frac=header_strip_frac)
        joined = "\n\n".join(page_texts)
        joined = normalize_ligatures(joined)
        joined = dehyphenate(joined)
        joined = collapse_blanklines(joined)
        joined = normalize_chapter_heading(joined, item["title"])

        out_path = out_dir / f"{item['slug']}.md"
        out_path.write_text(joined)
        written.append({**item, "file": out_path.name,
                        "page_range": [r["start"], r["end"]],
                        "chars": len(joined)})
        print(f"  wrote {out_path.name}  "
              f"(pages {r['start']}-{r['end']}, {len(joined)} chars)",
              file=sys.stderr)

    return written


# --- SUMMARY.md generation ---


def write_summary(items: list[dict], out_path: Path, title: str):
    """Write a draft SUMMARY.md respecting mdBook's strict format."""
    lines = [f"# {title}", ""]

    # Find prefix items (level 1, before any deeper structure starts).
    # To keep it simple, emit all items as numbered chapters with
    # appropriate nesting.
    for item in items:
        indent = "  " * (item["level"] - 1)
        lines.append(f"{indent}- [{item['title']}]({item['file']})")

    out_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_path}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pages", required=True,
                    help="Page directory (containing manifest.json + page_NNNN.md)")
    ap.add_argument("--outline",
                    help="outline.json path (from extract_outline.py)")
    ap.add_argument("--detect-headings", action="store_true",
                    help="Heuristically detect chapters from page content")
    ap.add_argument("--out", required=True,
                    help="Output directory for chapter files + SUMMARY.md")
    ap.add_argument("--title", default="Summary",
                    help="Title to put at top of SUMMARY.md (default: 'Summary')")
    ap.add_argument("--header-strip-frac", type=float, default=0.5,
                    help="Fraction of pages on which a top/bottom line must "
                         "appear to be stripped (default: 0.5)")
    args = ap.parse_args()

    pages_dir = Path(args.pages)
    manifest_path = pages_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: {manifest_path} not found. "
              "Run extract_text_pages.py or ocr_pages.py first.",
              file=sys.stderr)
        sys.exit(1)
    manifest = json.loads(manifest_path.read_text())

    outline: list[dict] = []
    if args.outline and Path(args.outline).exists():
        outline = load_outline(args.outline)

    if not outline and args.detect_headings:
        print("Detecting chapter headings heuristically...", file=sys.stderr)
        outline = detect_headings(pages_dir, manifest)
        if outline:
            print(f"  detected {len(outline)} chapters", file=sys.stderr)
        else:
            print("  no chapters detected; using single-chapter fallback",
                  file=sys.stderr)

    if not outline:
        print("WARNING: no outline; producing single-chapter book.",
              file=sys.stderr)

    out_dir = Path(args.out)
    written = assemble(outline, pages_dir, manifest, out_dir,
                       args.header_strip_frac)

    # Carry the pages/images/ tree (produced by ocr_pages.py's image
    # fallback) into the chapters output so init_mdbook.py picks it up
    # via its subdirectory-copy step. Without this, image-fallback
    # pages render as broken links in the final mdBook.
    pages_images = pages_dir / "images"
    if pages_images.is_dir():
        out_images = out_dir / "images"
        shutil.copytree(pages_images, out_images, dirs_exist_ok=True)
        print(f"Copied OCR fallback images → {out_images}", file=sys.stderr)

    summary_path = out_dir / "SUMMARY.md"
    write_summary(written, summary_path, args.title)

    print(f"\nWrote {len(written)} chapter file(s) to {out_dir}")
    print(f"Draft SUMMARY: {summary_path}")
    print("Spot-check a chapter or two before running init_mdbook.py.")


if __name__ == "__main__":
    main()
