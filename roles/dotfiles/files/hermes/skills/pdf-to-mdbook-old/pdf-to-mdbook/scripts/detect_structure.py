#!/usr/bin/env python3
"""
detect_structure.py — Intelligent chapter detection using multiple signals.

Used when extract_outline.py reports no PDF bookmarks. Combines:

  1. Printed TOC detection — find pages that look like a table of
     contents by layout signature (lines ending in page numbers, dot
     leaders, hierarchical indent).
  2. TOC parsing — extract entries with title, indent level, and
     printed page number.
  3. Page-offset estimation — locate the first few chapters in the
     body and compute the offset between printed and PDF page numbers.
  4. Font analysis — use pdfplumber to find heading-sized text and
     either supplement TOC results or stand alone if no TOC exists.
  5. Cross-validation — confirm each chapter title actually appears on
     its predicted PDF page; flag mismatches.
  6. Rasterize TOC pages — so the agent can verify with vision when
     confidence is low.

Outputs:
  outline.json          — same schema as extract_outline.py
  outline_review.json   — confidence scores, issues, paths to TOC images
  toc-images/*.png      — rasterized TOC pages (low DPI, just for review)

Usage:
    python detect_structure.py input.pdf --out work/
"""

import argparse
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import unicodedata
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


# --- Utility ---


def slugify(title: str, max_len: int = 60) -> str:
    nfkd = unicodedata.normalize("NFKD", title)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return (slug[:max_len].rstrip("-") or "section")


def normalize_for_match(s: str) -> str:
    """Lowercase, strip leading numbering, collapse whitespace."""
    s = re.sub(r"^[\dIVXivx]+[.)]?\s+", "", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def fuzzy_contains(haystack: str, needle: str, min_overlap: float = 0.7) -> bool:
    """Check if `needle` appears in `haystack` allowing some character drift."""
    if not needle or not haystack:
        return False
    n = normalize_for_match(needle)
    h = normalize_for_match(haystack)
    if len(n) < 4:
        return False
    if n in h:
        return True
    # Token-overlap fallback for OCR'd text where exact match fails
    n_tokens = set(n.split())
    h_tokens = set(h.split())
    if not n_tokens:
        return False
    overlap = len(n_tokens & h_tokens) / len(n_tokens)
    return overlap >= min_overlap and len(n_tokens) >= 2


def pdftotext_page(pdf_path: str, page: int, layout: bool = True) -> str:
    cmd = ["pdftotext"]
    if layout:
        cmd.append("-layout")
    cmd += ["-f", str(page), "-l", str(page), pdf_path, "-"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return r.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


# --- Step 1: Detect TOC pages ---


# A TOC-looking line ends with a page number (arabic or roman) optionally
# followed by trailing whitespace/dots (which can happen with overflowing
# dot leaders). We also accept long dot runs anywhere as a strong signal.
TOC_LINE_TAIL = re.compile(
    r"\b(?:\d{1,4}|[ivxlcdm]{1,8})\b[\s.]*$",
    re.IGNORECASE,
)
TOC_DOT_RUN = re.compile(r"\.{4,}|(?:\.\s){3,}")


def page_toc_score(text: str) -> tuple[float, int]:
    """Return (fraction-of-toc-like-lines, line-count)."""
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 5:
        return 0.0, len(lines)
    matches = 0
    for l in lines:
        # Strong signal: line has both a long dot run and ends in a number.
        # Weaker signal: line ends in a number with multiple spaces before it.
        ends_in_num = bool(TOC_LINE_TAIL.search(l))
        has_dots = bool(TOC_DOT_RUN.search(l))
        if ends_in_num and (has_dots or re.search(r"\s{3,}\S", l)):
            matches += 1
    return matches / len(lines), len(lines)


def detect_toc_pages(pdf_path: str, page_count: int,
                     max_scan: int = 30,
                     threshold: float = 0.35) -> list[int]:
    """Return PDF page numbers (1-indexed) of the most likely TOC run."""
    scan_limit = min(max_scan, page_count)
    candidates = []
    for p in range(1, scan_limit + 1):
        text = pdftotext_page(pdf_path, p, layout=True)
        score, n_lines = page_toc_score(text)
        if score >= threshold and n_lines >= 8:
            candidates.append((p, score))

    if not candidates:
        return []

    # Find longest contiguous run
    runs: list[list[int]] = []
    current = [candidates[0][0]]
    for p, _ in candidates[1:]:
        if p == current[-1] + 1:
            current.append(p)
        else:
            runs.append(current)
            current = [p]
    runs.append(current)
    longest = max(runs, key=len)
    return longest


# --- Step 2: Parse TOC text into entries ---


# (indent, title, page)  — common patterns
# Allow trailing dots/spaces after the page number (overflowing dot
# leaders are common in real-world TOCs).
TOC_PATTERNS = [
    # "Title .... 23 ......" — dot leader, optional trailing junk
    re.compile(
        r"^(\s*)(.+?)\s*[.\s]{3,}\s*"
        r"(\d{1,4}|[ivxlcdmIVXLCDM]+)"
        r"\b[.\s]*$"
    ),
    # "Title    23" — no dots, 2+ spaces before page
    re.compile(
        r"^(\s*)(\S.{2,}?)\s{2,}"
        r"(\d{1,4}|[ivxlcdmIVXLCDM]+)"
        r"\b[.\s]*$"
    ),
]


def parse_roman(s: str) -> int | None:
    s = s.strip().upper()
    if not re.fullmatch(r"[IVXLCDM]+", s):
        return None
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for ch in reversed(s):
        v = vals[ch]
        if v < prev:
            total -= v
        else:
            total += v
        prev = v
    return total


def parse_toc_lines(text_blocks: list[str]) -> list[dict]:
    entries: list[dict] = []
    for block in text_blocks:
        for raw_line in block.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue
            for pat in TOC_PATTERNS:
                m = pat.match(line)
                if not m:
                    continue
                indent_str = m.group(1)
                title = m.group(2).strip().rstrip(".").strip()
                page_str = m.group(3)
                # Avoid junk like a single character + page number
                if len(title) < 3:
                    break
                # Avoid lines that are mostly digits
                if sum(c.isdigit() for c in title) > len(title) * 0.5:
                    break
                # Convert page
                if page_str.isdigit():
                    page = int(page_str)
                    page_kind = "arabic"
                else:
                    rn = parse_roman(page_str)
                    if rn is None:
                        break
                    page = rn
                    page_kind = "roman"

                indent_chars = len(indent_str.expandtabs(4))
                entries.append({
                    "title": title,
                    "indent": indent_chars,
                    "printed_page": page,
                    "page_kind": page_kind,
                })
                break

    return entries


def assign_levels(entries: list[dict], max_levels: int = 4) -> None:
    """Cluster indent values to integer levels (1..max_levels)."""
    if not entries:
        return
    indents = sorted({e["indent"] for e in entries})
    # Greedy: each distinct indent is a level, capped at max_levels
    level_map: dict[int, int] = {}
    for i, ind in enumerate(indents):
        level_map[ind] = min(i + 1, max_levels)
    for e in entries:
        e["level"] = level_map[e["indent"]]


# --- Step 3: Find printed→PDF page offset ---


def get_page_count(pdf_path: str) -> int:
    return len(PdfReader(pdf_path).pages)


def estimate_page_offset(pdf_path: str, entries: list[dict],
                         total_pages: int,
                         exclude_pages: set[int] | None = None
                         ) -> tuple[int, str, int]:
    """Try to match the first few entries against PDF pages.

    Excludes any pages in `exclude_pages` (typically the detected TOC
    pages) so the search doesn't match chapter titles on the TOC itself.

    Returns (offset, method_description, n_matched)."""
    exclude_pages = exclude_pages or set()
    # Only use entries with arabic page numbers (front matter often uses
    # roman numerals which complicate offset calculation)
    arabic_entries = [e for e in entries if e["page_kind"] == "arabic"]
    if not arabic_entries:
        return 0, "no-arabic-entries", 0

    # Probe up to 8 entries spread through the book. Prefer level-1
    # entries (chapter titles), which are more likely to appear
    # prominently in body text than sub-section titles.
    top_level = [e for e in arabic_entries if e.get("level", 1) == 1]
    pool = top_level if len(top_level) >= 3 else arabic_entries
    n = len(pool)
    if n <= 8:
        probes = pool
    else:
        step = n // 8
        probes = [pool[i * step] for i in range(8)]

    offsets: list[int] = []
    for probe in probes:
        target = probe["title"]
        printed = probe["printed_page"]
        # Bias the search forward (typical books have +offset due to
        # front matter), then fall back to nearby reverse pages.
        forward = list(range(printed, total_pages + 1))
        backward = list(range(printed - 1, 0, -1))
        scan_pages = [p for p in (forward + backward) if p not in exclude_pages]

        for pdf_page in scan_pages[:80]:  # cap effort per probe
            text = pdftotext_page(pdf_path, pdf_page, layout=False)[:1500]
            if fuzzy_contains(text, target):
                offsets.append(pdf_page - printed)
                break

    if not offsets:
        return 0, "no-matches", 0

    counter = collections.Counter(offsets)
    best_offset, count = counter.most_common(1)[0]
    method = f"matched-{count}-of-{len(probes)}-probes"
    return best_offset, method, count


# --- Step 4: Font analysis (pdfplumber) ---


def group_chars_to_lines(chars, y_tol: float = 2.0) -> list[list]:
    """Group chars into visual lines by y-coordinate."""
    if not chars:
        return []
    chars = sorted(chars, key=lambda c: (round(c.get("top", 0)), c.get("x0", 0)))
    lines: list[list] = []
    current: list = []
    cur_top: float | None = None
    for c in chars:
        top = c.get("top", 0)
        if cur_top is None or abs(top - cur_top) <= y_tol:
            if cur_top is None:
                cur_top = top
            current.append(c)
        else:
            lines.append(sorted(current, key=lambda x: x.get("x0", 0)))
            current = [c]
            cur_top = top
    if current:
        lines.append(sorted(current, key=lambda x: x.get("x0", 0)))
    return lines


def font_analysis(pdf_path: str, sample_pages: int = 60) -> dict:
    """Estimate body text size; find heading-sized lines per page."""
    if not HAS_PDFPLUMBER:
        return {"available": False}

    sizes = collections.Counter()
    headings: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        # First pass: body-text size from a sample
        sample_step = max(1, total // sample_pages)
        for i in range(0, total, sample_step):
            page = pdf.pages[i]
            for c in page.chars:
                size = round(c.get("size", 0) * 2) / 2
                if size > 0:
                    sizes[size] += 1

        if not sizes:
            return {"available": True, "body_size": None, "headings": []}

        body_size = sizes.most_common(1)[0][0]
        threshold = body_size * 1.25  # tolerant on the low side

        # Second pass: heading-sized lines on every page
        for idx, page in enumerate(pdf.pages):
            page_no = idx + 1
            if not page.chars:
                continue
            lines = group_chars_to_lines(page.chars)
            for line in lines:
                if not line:
                    continue
                avg_size = sum(c.get("size", 0) for c in line) / len(line)
                if avg_size < threshold:
                    continue
                text = "".join(c.get("text", "") for c in line).strip()
                if not (3 <= len(text) <= 120):
                    continue
                if text.lower() in {"contents", "table of contents", "index"}:
                    # These are valid headings; keep
                    pass
                headings.append({
                    "page": page_no,
                    "size": round(avg_size, 2),
                    "text": text,
                    "y": round(line[0].get("top", 0), 1),
                })

    # Cluster heading sizes into levels (largest = level 1)
    if headings:
        unique_sizes = sorted({h["size"] for h in headings}, reverse=True)
        level_map = {sz: min(i + 1, 4) for i, sz in enumerate(unique_sizes[:4])}
        for h in headings:
            h["level"] = level_map.get(h["size"], 4)

    return {
        "available": True,
        "body_size": body_size,
        "size_distribution": dict(sizes.most_common(10)),
        "headings": headings,
    }


# --- Step 5: Cross-validate ---


def cross_validate(pdf_path: str, entries: list[dict], offset: int,
                   total_pages: int,
                   exclude_pages: set[int] | None = None) -> list[dict]:
    """For each entry, check the title appears on/near its predicted page.

    Excludes TOC pages from neighbor-checking so a TOC entry doesn't
    appear to validate against itself."""
    exclude_pages = exclude_pages or set()
    issues: list[dict] = []
    for e in entries:
        if e["page_kind"] != "arabic":
            continue
        predicted = e["printed_page"] + offset
        if not (1 <= predicted <= total_pages):
            issues.append({
                "title": e["title"],
                "issue": "predicted-page-out-of-range",
                "predicted_pdf_page": predicted,
            })
            continue
        found_on = None
        for delta in (0, -1, 1, -2, 2):
            p = predicted + delta
            if not (1 <= p <= total_pages) or p in exclude_pages:
                continue
            text = pdftotext_page(pdf_path, p, layout=False)[:1500]
            if fuzzy_contains(text, e["title"]):
                found_on = p
                break
        if found_on is None:
            issues.append({
                "title": e["title"],
                "issue": "title-not-found-near-predicted-page",
                "predicted_pdf_page": predicted,
            })
        elif found_on != predicted:
            issues.append({
                "title": e["title"],
                "issue": "found-on-neighbor",
                "predicted_pdf_page": predicted,
                "actual_pdf_page": found_on,
            })
    return issues


# --- Step 6: Rasterize TOC pages for vision review ---


def rasterize_pages(pdf_path: str, pages: list[int], out_dir: Path,
                    dpi: int = 150) -> list[str]:
    """Rasterize the given pages as PNGs. Returns absolute paths."""
    if not pages or shutil.which("pdftoppm") is None:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for p in pages:
        prefix = out_dir / f"toc_p{p:03d}"
        try:
            subprocess.run(
                ["pdftoppm", "-png", "-r", str(dpi),
                 "-f", str(p), "-l", str(p),
                 pdf_path, str(prefix)],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError:
            continue
        # Find the produced file
        produced = sorted(out_dir.glob(f"toc_p{p:03d}*.png"))
        if produced:
            written.append(str(produced[0].resolve()))
    return written


# --- Step 7: Reconcile signals ---


def reconcile_signals(toc_entries: list[dict], offset: int,
                      offset_match_count: int,
                      font_headings: list[dict],
                      cross_val_issues: list[dict],
                      total_pages: int) -> tuple[list[dict], dict]:
    """Build final entries + a review summary describing confidence."""
    review: dict = {
        "method": None,
        "confidence": "low",
        "summary": "",
        "page_offset": offset,
        "page_offset_match_count": offset_match_count,
        "issues": cross_val_issues,
        "needs_review": True,
    }

    # Path A: TOC parsed and offset is consistent
    if toc_entries and offset_match_count >= 2:
        items = []
        for e in toc_entries:
            if e["page_kind"] == "roman":
                pdf_page = e["printed_page"]  # roman pages = front matter, often 1:1-ish
            else:
                pdf_page = e["printed_page"] + offset
            if not (1 <= pdf_page <= total_pages):
                continue
            items.append({
                "title": e["title"],
                "level": e.get("level", 1),
                "page": pdf_page,
                "slug": slugify(e["title"]),
                "source": "toc",
                "confidence": "high",
            })
        review["method"] = "toc-parse"

        # Confidence weighting: level-1 (chapter) issues are critical;
        # level-2+ (section) issues are common because section titles
        # often render differently in body than in TOC. We grade
        # primarily on chapter-level cross-validation health.
        l1_total = sum(1 for e in toc_entries if e.get("level", 1) == 1)
        l1_critical = sum(
            1 for issue in cross_val_issues
            if issue["issue"] != "found-on-neighbor"
            and any(e["title"] == issue["title"] and e.get("level", 1) == 1
                    for e in toc_entries)
        )
        sub_critical = sum(
            1 for issue in cross_val_issues
            if issue["issue"] != "found-on-neighbor"
            and any(e["title"] == issue["title"] and e.get("level", 1) > 1
                    for e in toc_entries)
        )

        l1_bad_frac = l1_critical / max(1, l1_total)
        # High confidence: very few chapter-level mismatches AND offset
        # was confirmed by multiple probes.
        if l1_bad_frac < 0.1 and offset_match_count >= 3:
            review["confidence"] = "high"
            review["needs_review"] = False
        elif l1_bad_frac < 0.25:
            review["confidence"] = "medium"
            review["needs_review"] = True
        else:
            review["confidence"] = "low"
            review["needs_review"] = True

        review["summary"] = (
            f"Detected {len(items)} entries from printed TOC. "
            f"Page offset {offset:+d} (confirmed by {offset_match_count} probe match(es)). "
            f"Chapter-level issues: {l1_critical}/{l1_total}. "
            f"Section-level issues: {sub_critical} (often expected — "
            f"sections may render differently in body)."
        )
        return items, review

    # Path B: TOC parsed but offset uncertain → emit but flag for review
    if toc_entries:
        items = [{
            "title": e["title"],
            "level": e.get("level", 1),
            "page": e["printed_page"],  # raw, no offset; agent must fix
            "slug": slugify(e["title"]),
            "source": "toc-no-offset",
            "confidence": "low",
        } for e in toc_entries]
        review["method"] = "toc-parse-no-offset"
        review["confidence"] = "low"
        review["needs_review"] = True
        review["summary"] = (
            f"Parsed {len(items)} entries from TOC, but could not establish "
            f"a reliable printed-to-PDF page offset. Page numbers are "
            f"PRINTED page numbers; correct manually after viewing TOC images."
        )
        return items, review

    # Path C: Font analysis fallback
    if font_headings:
        # Take only top-2 levels, deduped
        candidate = [h for h in font_headings if h.get("level", 4) <= 2]
        items = []
        seen_pages = set()
        for h in candidate:
            if h["page"] in seen_pages:
                continue
            items.append({
                "title": h["text"],
                "level": h["level"],
                "page": h["page"],
                "slug": slugify(h["text"]),
                "source": "font-analysis",
                "confidence": "medium",
            })
            seen_pages.add(h["page"])
        review["method"] = "font-analysis"
        review["confidence"] = "medium" if len(items) >= 3 else "low"
        review["needs_review"] = True
        review["summary"] = (
            f"No printed TOC found. Detected {len(items)} candidate "
            f"chapter heading(s) by font-size analysis. Review carefully "
            f"— this method has higher false-positive rates."
        )
        return items, review

    # Path D: Nothing worked
    review["method"] = "none"
    review["confidence"] = "none"
    review["summary"] = (
        "No bookmarks, no parseable TOC, no font-size signal. "
        "Falling back to single-chapter outline. Recommend rasterizing "
        "the first 25 pages and hand-writing outline.json."
    )
    return [{
        "title": "Document",
        "level": 1,
        "page": 1,
        "slug": "document",
        "source": "fallback-single-chapter",
        "confidence": "none",
    }], review


# --- Main ---


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="Path to input PDF")
    ap.add_argument("--out", required=True,
                    help="Output directory; writes outline.json + outline_review.json + toc-images/")
    ap.add_argument("--max-scan", type=int, default=30,
                    help="Max pages to scan looking for TOC (default: 30)")
    ap.add_argument("--toc-threshold", type=float, default=0.35,
                    help="Min line-ends-in-pagenum fraction to flag a TOC page")
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"ERROR: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_pages = get_page_count(args.pdf)
    print(f"Document: {total_pages} pages", file=sys.stderr)

    # Step 1: Detect TOC pages
    print("Scanning for printed table of contents...", file=sys.stderr)
    toc_pages = detect_toc_pages(args.pdf, total_pages,
                                 max_scan=args.max_scan,
                                 threshold=args.toc_threshold)
    if toc_pages:
        print(f"  candidate TOC pages: {toc_pages}", file=sys.stderr)
    else:
        print("  no TOC pages detected", file=sys.stderr)

    # Step 2: Parse TOC
    toc_entries: list[dict] = []
    if toc_pages:
        toc_text_blocks = [pdftotext_page(args.pdf, p, layout=True)
                           for p in toc_pages]
        toc_entries = parse_toc_lines(toc_text_blocks)
        assign_levels(toc_entries)
        print(f"  parsed {len(toc_entries)} TOC entries", file=sys.stderr)

    # Step 3: Estimate page offset
    offset = 0
    offset_method = "none"
    offset_count = 0
    if toc_entries:
        print("Estimating printed→PDF page offset...", file=sys.stderr)
        offset, offset_method, offset_count = estimate_page_offset(
            args.pdf, toc_entries, total_pages,
            exclude_pages=set(toc_pages),
        )
        print(f"  offset={offset:+d} ({offset_method})", file=sys.stderr)

    # Step 4: Font analysis (always run; useful as cross-check or fallback)
    print("Running font-size analysis...", file=sys.stderr)
    font_data = font_analysis(args.pdf)
    if font_data.get("available"):
        body = font_data.get("body_size")
        n_headings = len(font_data.get("headings", []))
        print(f"  body size ~{body}pt; "
              f"{n_headings} heading-sized line(s) detected", file=sys.stderr)

    # Step 5: Cross-validate TOC entries
    issues: list[dict] = []
    if toc_entries and offset_count >= 1:
        issues = cross_validate(args.pdf, toc_entries, offset, total_pages,
                                exclude_pages=set(toc_pages))
        if issues:
            print(f"  {len(issues)} cross-validation issue(s)", file=sys.stderr)

    # Step 6: Rasterize TOC pages for review
    toc_images: list[str] = []
    if toc_pages:
        toc_images = rasterize_pages(
            args.pdf, toc_pages, out_dir / "toc-images", dpi=150
        )
        if toc_images:
            print(f"  rasterized {len(toc_images)} TOC page(s) for review",
                  file=sys.stderr)

    # Step 7: Reconcile
    items, review = reconcile_signals(
        toc_entries, offset, offset_count,
        font_data.get("headings", []), issues, total_pages
    )

    # Outputs
    outline = {
        "has_outline": len(items) > 0,
        "items": items,
        "source": review["method"],
        "page_offset": offset,
    }
    (out_dir / "outline.json").write_text(json.dumps(outline, indent=2))

    review["toc_pages_pdf"] = toc_pages
    review["rasterized_toc_pages"] = toc_images
    review["font_body_size"] = font_data.get("body_size")
    review["items_count"] = len(items)
    (out_dir / "outline_review.json").write_text(json.dumps(review, indent=2))

    # Console summary
    print()
    print(f"Method:     {review['method']}")
    print(f"Confidence: {review['confidence']}")
    print(f"Items:      {len(items)}")
    print(f"Summary:    {review['summary']}")
    print(f"\nWrote:")
    print(f"  {out_dir / 'outline.json'}")
    print(f"  {out_dir / 'outline_review.json'}")
    if toc_images:
        print(f"  {len(toc_images)} TOC images in {out_dir / 'toc-images'}/")
    if review.get("needs_review"):
        print("\n⚠ NEEDS REVIEW. Open outline_review.json for details.")
        if toc_images:
            print(f"  → View the TOC images in {out_dir / 'toc-images'}/")
            print("    and edit outline.json to reflect what you see.")
    else:
        print("\n✓ High confidence. Safe to proceed to assemble_chapters.py.")


if __name__ == "__main__":
    main()
