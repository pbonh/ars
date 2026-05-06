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

def _require_pypdf():
    try:
        from pypdf import PdfReader  # noqa: F401
        return PdfReader
    except ImportError:
        print(
            "ERROR: pypdf not installed. Run: pip install pypdf "
            "--break-system-packages",
            file=sys.stderr,
        )
        sys.exit(2)


try:
    import pdfplumber  # noqa: F401
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


# --- Utility ---


_LIGATURE_FALLBACK = {
    "ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl",
    "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
}


def sanitize_title(title: str) -> str:
    """Normalize raw heading text for outline.json.

    Mirrors ``extract_outline.sanitize_title``: applies NFKC, expands
    leftover ligatures, neutralizes ``\\r``/``\\t`` (which truncate titles
    when used as filenames), strips control chars, and collapses
    whitespace.
    """
    if not title:
        return ""
    s = unicodedata.normalize("NFKC", title)
    for k, v in _LIGATURE_FALLBACK.items():
        s = s.replace(k, v)
    s = s.replace("\r", " ").replace("\t", " ")
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def slugify(title: str, max_len: int = 60) -> str:
    title = sanitize_title(title)
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


def read_page_text(pdf_path: str, page: int,
                   pages_dir: Path | None = None,
                   layout: bool = True) -> str:
    """Return text for ``page`` (1-indexed).

    When ``pages_dir`` is provided and ``pages_dir/page_NNNN.md`` exists,
    read it directly. This lets the structure-detection pass consume
    OCR output (or pre-extracted layout text) for scanned PDFs whose
    text layer is empty. Otherwise fall back to ``pdftotext``.

    The OCR path renders an image-fallback comment for tesseract-zero
    pages; that comment is harmless for TOC scoring (it is short and
    contains no page-number tail), so we don't strip it here.
    """
    if pages_dir is not None:
        candidate = pages_dir / f"page_{page:04d}.md"
        if candidate.exists():
            try:
                return candidate.read_text()
            except OSError:
                pass
    return pdftotext_page(pdf_path, page, layout=layout)


# --- Step 1: Detect TOC pages ---


# A TOC-looking line ends with a page number (arabic or roman) optionally
# followed by trailing whitespace/dots (which can happen with overflowing
# dot leaders). We also accept long dot runs anywhere as a strong signal.
TOC_LINE_TAIL = re.compile(
    r"\b(?:\d{1,4}|[ivxlcdm]{1,8})\b[\s.]*$",
    re.IGNORECASE,
)
TOC_DOT_RUN = re.compile(r"\.{4,}|(?:\.\s){3,}")
# OCR'd separator: a slash or comma between title and page number, used
# when the printed TOC had a right-aligned column that tesseract
# collapsed onto the title line.
TOC_OCR_SEP_TAIL = re.compile(
    r"\s+[/,]\s*(?:\d{1,4}|[ivxlcdmIVXLCDM]+)\s*$",
    re.IGNORECASE,
)
# Section-numbered TOC line opener like "5.8 ", "6 ", "6.2.1 ". When
# combined with a trailing page number, that's a strong TOC signal even
# without dot-leaders or wide-space separators (which OCR often collapses
# to a single space, defeating the dot-leader / 3-space heuristics).
TOC_NUMERIC_PREFIX = re.compile(r"^\s*\d+(?:\.\d+)*\.?\s+\S")

# Headers that mark the start of a section that LOOKS like a TOC but
# isn't (lists of figures/tables/algorithms, indices). Used to trim a
# detected TOC run when it accidentally swallows them.
NON_TOC_HEADING = re.compile(
    r"^\s*(?:list\s+of\s+(?:figures?|tables?|algorithms?|symbols?|"
    r"abbreviations?|notations?|illustrations?|exhibits?|equations?|"
    r"acronyms?)|index|glossary|nomenclature|bibliography|references?)\b",
    re.IGNORECASE,
)


def is_non_toc_section_start(text: str) -> bool:
    """True if the page's first meaningful line looks like 'List of
    Figures', 'Index', etc. — sections that share TOC layout but are
    distinct documents and should not be glued to the main contents."""
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip bare running headers (e.g. roman numeral page numbers)
        if re.fullmatch(r"[ivxlcdmIVXLCDM]{1,8}", stripped):
            continue
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        return bool(NON_TOC_HEADING.match(stripped))
    return False


def page_toc_score(text: str) -> tuple[float, int]:
    """Return (fraction-of-toc-like-lines, line-count)."""
    lines = [l for l in text.splitlines() if l.strip()]
    if len(lines) < 5:
        return 0.0, len(lines)
    matches = 0
    for l in lines:
        # Strong signal: line has both a long dot run and ends in a number.
        # Weaker signal: line ends in a number with multiple spaces before it.
        # Also strong: line has a slash/comma separator before a trailing
        # number — common OCR artifact for right-aligned TOC pages.
        ends_in_num = bool(TOC_LINE_TAIL.search(l))
        has_dots = bool(TOC_DOT_RUN.search(l))
        has_ocr_sep = bool(TOC_OCR_SEP_TAIL.search(l))
        has_section_num = bool(TOC_NUMERIC_PREFIX.match(l))
        if ends_in_num and (
            has_dots
            or has_ocr_sep
            or has_section_num
            or re.search(r"\s{3,}\S", l)
        ):
            matches += 1
    return matches / len(lines), len(lines)


def detect_toc_pages(pdf_path: str, page_count: int,
                     max_scan: int = 30,
                     threshold: float = 0.35,
                     extend_threshold: float = 0.20,
                     pages_dir: Path | None = None) -> list[int]:
    """Return PDF page numbers (1-indexed) of the most likely TOC run.

    Two-pass detection:
      1. Strong: pages scoring >= ``threshold`` are seeds.
      2. Soft extend: greedily walk outward from the longest seed run,
         absorbing adjacent pages scoring >= ``extend_threshold``.

    The soft pass catches multi-page TOCs whose second page has a
    different leader-style mix and falls just below the strong cutoff.
    Body pages score near zero on ``page_toc_score``, so they don't
    sneak in.
    """
    scan_limit = min(max_scan, page_count)
    scores: dict[int, tuple[float, int]] = {}
    texts: dict[int, str] = {}
    for p in range(1, scan_limit + 1):
        text = read_page_text(pdf_path, p, pages_dir=pages_dir, layout=True)
        texts[p] = text
        scores[p] = page_toc_score(text)

    seeds = [p for p, (s, n) in scores.items()
             if s >= threshold and n >= 8]
    if not seeds:
        return []

    # Longest contiguous run of seeds
    runs: list[list[int]] = []
    current = [seeds[0]]
    for p in seeds[1:]:
        if p == current[-1] + 1:
            current.append(p)
        else:
            runs.append(current)
            current = [p]
    runs.append(current)
    longest = max(runs, key=len)

    def soft_ok(p: int) -> bool:
        if p < 1 or p > scan_limit:
            return False
        s, n = scores[p]
        return s >= extend_threshold and n >= 8

    while soft_ok(longest[0] - 1):
        longest.insert(0, longest[0] - 1)
    while soft_ok(longest[-1] + 1):
        longest.append(longest[-1] + 1)

    # Trim the run at the first page that starts with "List of Figures",
    # "Index", etc. Those layouts mimic TOC formatting but represent a
    # different document section; gluing them onto the main contents
    # produces hundreds of bogus outline entries.
    trimmed: list[int] = []
    for p in longest:
        if p != longest[0] and is_non_toc_section_start(texts[p]):
            break
        trimmed.append(p)
    return trimmed


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
    # "Title / 23" or "Title , 23" — OCR commonly collapses a
    # right-aligned page number onto the title line with a stray
    # punctuation separator. The slash form is what tesseract
    # produced for `computer-methods-for-circuit-analysis-and-design`.
    re.compile(
        r"^(\s*)(\S.{2,}?)\s*[/,]\s*"
        r"(\d{1,4}|[ivxlcdmIVXLCDM]+)"
        r"\b[.\s]*$"
    ),
    # "5.8 References 225" / "6 Resource Sharing and Binding 229"
    # — section-numbered entry with the page on the same line,
    # single-space-separated. Common when OCR collapsed a
    # right-aligned page-number column onto the title row.
    # Anchored to a section-number prefix so it doesn't match
    # arbitrary "title number" body sentences.
    re.compile(
        r"^(\s*)((?:\d+(?:\.\d+)*\.?)\s+\S.*?)\s+"
        r"(\d{1,4}|[ivxlcdmIVXLCDM]+)"
        r"\b[.\s]*$"
    ),
    # "Chapter 10 Transferred-Electron Devices 510" — high-specificity
    # structural entries (Chapter/Part/Section/Appendix). These can
    # have just one space before the page number when the title is
    # long enough to consume the line. Single space is too permissive
    # in general but safe here because the line has to start with one
    # of these structural keywords.
    re.compile(
        r"^(\s*)((?:chapter|part|section|appendix|appendices)"
        r"\s+[\dIVXLCDMA-Z][\w\d.]*\b[^\d\n]*?)\s+"
        r"(\d{1,4}|[ivxlcdmIVXLCDM]+)"
        r"\b[.\s]*$",
        re.IGNORECASE,
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
                title = sanitize_title(m.group(2).strip().rstrip("."))
                page_str = m.group(3)
                # Avoid junk like a single character + page number
                if len(title) < 3:
                    break
                # Avoid lines that are mostly digits
                if sum(c.isdigit() for c in title) > len(title) * 0.5:
                    break
                # Drop running-header / TOC self-reference lines (the
                # word "CONTENTS" with a roman/arabic page number
                # appears on every TOC page and gets parsed as a fake
                # entry otherwise).
                if re.fullmatch(
                    r"(?:contents|table\s+of\s+contents|toc|index|"
                    r"bibliography|references?|glossary|nomenclature)",
                    title.lower().strip(".").strip(),
                ):
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
    PdfReader = _require_pypdf()
    return len(PdfReader(pdf_path).pages)


def estimate_page_offset(pdf_path: str, entries: list[dict],
                         total_pages: int,
                         exclude_pages: set[int] | None = None,
                         pages_dir: Path | None = None,
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

    # Probe up to 16 entries spread through the book. Prefer level-1
    # entries (chapter titles), which are more likely to appear
    # prominently in body text than sub-section titles. Always include
    # the last entry — late chapters live deep in the body and give the
    # cleanest offset signal once the book is past its front matter.
    top_level = [e for e in arabic_entries if e.get("level", 1) == 1]
    pool = top_level if len(top_level) >= 3 else arabic_entries
    n = len(pool)
    max_probes = 16
    if n <= max_probes:
        probes = pool
    else:
        step = n / max_probes
        idx = sorted({int(i * step) for i in range(max_probes)} | {n - 1})
        probes = [pool[i] for i in idx]

    offsets: list[int] = []
    for probe in probes:
        target = probe["title"]
        printed = probe["printed_page"]
        # Scan by distance from the predicted page so the closest match
        # wins, regardless of direction. Forward-biasing is wrong for
        # PDFs whose printed numbering runs ahead of PDF pagination
        # (e.g. covers/copyright counted in the printed numbers but
        # printed page 1 ≠ PDF page 1). A running header on a body page
        # will otherwise outrank the real chapter start.
        scan_pages: list[int] = []
        max_radius = max(printed, total_pages - printed)
        for d in range(0, max_radius + 1):
            for cand in (printed - d, printed + d) if d else (printed,):
                if 1 <= cand <= total_pages and cand not in exclude_pages \
                        and cand not in scan_pages:
                    scan_pages.append(cand)

        for pdf_page in scan_pages[:80]:  # cap effort per probe
            text = read_page_text(pdf_path, pdf_page,
                                  pages_dir=pages_dir, layout=False)[:1500]
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
                text = sanitize_title("".join(c.get("text", "") for c in line))
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


# --- Step 4b: Body-heading scan (third-tier fallback) ---


# Strict structural heading: "CHAPTER 3", "Part IV", "Appendix B",
# "Chapter 5: Sensitivities", "CHAPTER 1 NETWORK ANALYSIS".
#
# We deliberately require the trailing title (if present) to be ALL-CAPS
# (allowing digits, spaces, and safe punctuation). That rejects body
# prose like "Chapter 13. In order to solve…" or "Appendix D and other
# codes…" which the previous loose pattern accepted. Real chapter
# headings in OCR'd or scanned books almost always come out all-caps,
# whereas referential prose preserves sentence case.
BODY_STRUCTURAL_HEADING = re.compile(
    # Keyword is case-insensitive ("CHAPTER" / "Chapter" / "chapter"
    # are all valid heading openers). The optional trailing title is
    # NOT case-insensitive — it must be uppercase. Without that
    # constraint we match body prose like "Part II is dedicated to
    # architectural-level synthesis…" because IGNORECASE on the
    # whole pattern silently turned `[A-Z]` into `[A-Za-z]`.
    r"^\s*(?i:chapter|part|book|section|appendix|appendices)"
    r"\s+(?:\d+|[IVXLCDMivxlcdm]+|[A-Z])\b"
    r"(?:[\s:.\-—]+[A-Z][A-Z\s.\d&'\"\-—()]{1,80})?\s*$"
)

# Single-word front/back-matter headings that authors use as
# stand-alone chapter titles. Matched against a stripped first
# non-empty line.
BODY_SINGLETON_HEADINGS = {
    "foreword", "preface", "introduction", "acknowledgments",
    "acknowledgements", "conclusion", "epilogue", "afterword",
    "index", "bibliography", "references", "glossary",
    "nomenclature", "appendix", "appendices", "abstract",
}


def _collect_running_headers(pages_text: dict[int, str]) -> set[str]:
    """Lines repeating on >15% of pages — likely running headers, not chapters."""
    counter: collections.Counter = collections.Counter()
    n = len(pages_text)
    for txt in pages_text.values():
        seen_on_page: set[str] = set()
        for line in txt.splitlines()[:6]:
            stripped = line.strip()
            if not stripped or len(stripped) > 80:
                continue
            seen_on_page.add(stripped.lower())
        for s in seen_on_page:
            counter[s] += 1
    threshold = max(3, n * 0.15)
    return {s for s, c in counter.items() if c >= threshold}


def _looks_like_title_line(line: str) -> bool:
    """Short title-case phrase with no terminal punctuation.

    Used to catch chapter starts in books like rust-book where chapters
    open with `Getting Started` / `Common Programming Concepts` / etc.
    on the first line of the page, no chapter-number prefix.
    """
    stripped = line.strip()
    if not (3 <= len(stripped) <= 60):
        return False
    # Reject anything that ends like a sentence (continuation prose) or
    # a TOC entry (trailing page number).
    if stripped[-1] in ".,;:!?":
        return False
    if re.search(r"\d{1,4}\s*$", stripped):
        return False
    # Reject lines containing markdown / formatting noise.
    if any(c in stripped for c in "[](){}<>|`"):
        return False
    words = stripped.split()
    if not words:
        return False
    # First char must be an uppercase letter (or a quote/dash before one).
    head = stripped.lstrip("\"'“”‘’—–-")
    if not head or not head[0].isupper():
        return False
    # Title-case heuristic: among ≥4-letter words, most should start with
    # uppercase. This rejects sentence fragments like "Let's jump into
    # Rust by working through a hands-on project together" (only "Let's"
    # and "Rust" capitalized) while accepting "Common Programming
    # Concepts" / "Understanding Ownership".
    long_words = [w for w in words if len(w) >= 4]
    if not long_words:
        # Single short title like "Macros" — accept if it has only 1
        # word and that word is capitalized + alphabetic.
        return len(words) == 1 and words[0].isalpha() and words[0][0].isupper()
    capped = sum(1 for w in long_words if w[0].isupper())
    return capped / len(long_words) >= 0.6


def detect_body_headings(pdf_path: str, total_pages: int,
                         pages_dir: Path | None,
                         page_cache: dict[int, str] | None = None,
                         ) -> list[dict]:
    """Scan body pages for chapter-like headings.

    Third-tier fallback used when both TOC parsing and font analysis
    failed. Only runs when ``pages_dir`` is available, since otherwise
    a per-page ``pdftotext`` call across a 600-page book is too slow
    and rarely productive (text PDFs without bookmarks usually have a
    real TOC; books that lack one are typically web-rendered like the
    rust-book).
    """
    if pages_dir is None:
        return []

    if page_cache is None:
        page_cache = {}

    # First pass: load text for every page (cheap when reading from .md
    # files on disk).
    pages_text: dict[int, str] = {}
    for p in range(1, total_pages + 1):
        if p in page_cache:
            pages_text[p] = page_cache[p]
            continue
        text = read_page_text(pdf_path, p, pages_dir=pages_dir, layout=False)
        page_cache[p] = text
        pages_text[p] = text

    running = _collect_running_headers(pages_text)

    items: list[dict] = []
    seen_titles: set[str] = set()

    def add(title: str, page: int, level: int) -> None:
        title = sanitize_title(title)
        if not title:
            return
        key = title.lower()
        if key in seen_titles:
            return
        if key in running:
            return
        seen_titles.add(key)
        items.append({
            "title": title,
            "level": level,
            "page": page,
            "slug": slugify(title),
        })

    for page in range(1, total_pages + 1):
        text = pages_text.get(page, "")
        if not text:
            continue
        # First ~10 non-empty lines per page.
        lines = [l.rstrip() for l in text.splitlines() if l.strip()][:10]
        first_line = lines[0].strip() if lines else ""

        # 1. Strict structural heading anywhere in the first 10 lines.
        matched = False
        for line in lines:
            stripped = line.strip()
            if len(stripped) > 120:
                continue
            if BODY_STRUCTURAL_HEADING.match(stripped):
                add(stripped, page, level=1)
                matched = True
                break
            low = stripped.lower().rstrip(":.").strip()
            if low in BODY_SINGLETON_HEADINGS:
                add(stripped, page, level=1)
                matched = True
                break
        if matched:
            continue

        # 2. Chapter-start heuristic for books without numbered headings:
        # the first non-empty line of the page is a short title-case
        # phrase with no terminal punctuation, and the page has body
        # text below it (i.e. it's not a title-only spread).
        if first_line and _looks_like_title_line(first_line):
            if len(lines) >= 2:
                add(first_line, page, level=1)

    return items


# --- Step 5: Cross-validate ---


def refine_offset_via_body_scan(pdf_path: str, entries: list[dict],
                                total_pages: int,
                                exclude_pages: set[int] | None = None,
                                page_cache: dict[int, str] | None = None,
                                pages_dir: Path | None = None,
                                ) -> tuple[int, int]:
    """Recover from a wrong initial offset by scanning the whole body.

    For each entry, find every body page where the title fuzzy-matches
    (running headers repeat the title on every page of a chapter, so
    each entry typically yields many matches at the *true* offset and
    few at any wrong offset). Build a histogram of
    (actual_page - printed_page) across all (entry, page) match pairs;
    the mode is the true offset.

    Forward references ("see Chapter 14") in early chapters produce
    wildly negative offsets but only one match per reference, so they
    don't outvote the running-header consensus.

    Returns ``(offset, support_score)``. support_score is the histogram
    bucket size for the winning offset. 0 means nothing matched.
    """
    exclude_pages = exclude_pages or set()
    arabic = [e for e in entries if e["page_kind"] == "arabic"]
    if not arabic:
        return 0, 0

    body_pages = [p for p in range(1, total_pages + 1)
                  if p not in exclude_pages]
    body_texts = page_cache if page_cache is not None else {}

    # Build a histogram of (offset → count) across ALL matches.
    offset_counts: collections.Counter = collections.Counter()
    # Also remember per-entry support so we can report how many
    # *distinct* entries voted for the winning offset (a stronger
    # signal than raw match count, since one chatty chapter could
    # dominate the histogram otherwise).
    offset_entries: dict[int, set[int]] = collections.defaultdict(set)

    for e_idx, e in enumerate(arabic):
        for p in body_pages:
            if p not in body_texts:
                body_texts[p] = read_page_text(
                    pdf_path, p, pages_dir=pages_dir, layout=False
                )[:1500]
            if fuzzy_contains(body_texts[p], e["title"]):
                off = p - e["printed_page"]
                offset_counts[off] += 1
                offset_entries[off].add(e_idx)

    if not offset_counts:
        return 0, 0

    # Reject offsets that would push entries out of the valid page
    # range — those are nonsensical no matter how many entries vote
    # for them (forward references in early-book content can produce
    # large negative offsets that "validate" 8 chapters all at the
    # same impossible position).
    def offset_is_plausible(off: int) -> bool:
        out_of_range = sum(
            1 for e in arabic
            if not (1 <= e["printed_page"] + off <= total_pages)
        )
        return out_of_range / len(arabic) < 0.1

    plausible = {o: c for o, c in offset_counts.items()
                 if offset_is_plausible(o)}
    if not plausible:
        return 0, 0

    # Pick the offset that's supported by the most distinct entries
    # (tie-break by total match count). This rewards offsets that
    # multiple chapters agree on, not a single chapter that's mentioned
    # 50 times.
    best_offset = max(
        plausible,
        key=lambda o: (len(offset_entries[o]), offset_counts[o]),
    )
    return best_offset, len(offset_entries[best_offset])


def snap_entries_to_body_titles(pdf_path: str, items: list[dict],
                                total_pages: int,
                                exclude_pages: set[int] | None = None,
                                window: int = 50,
                                page_cache: dict[int, str] | None = None,
                                pages_dir: Path | None = None,
                                ) -> int:
    """Snap each L1 item's ``page`` to the nearest body page where its
    title actually appears. Mutates items in place. Returns moved count.

    The search starts at the item's predicted page and walks outward,
    but the *predicted page is itself adjusted* by the running median
    of prior snap deltas. Books with Part-separator pages drift the
    true offset away from the global estimate as you move through the
    book; carrying a running adjustment lets later chapters benefit
    from the corrections found for earlier chapters.

    A page-text cache (shared with prior body scans) avoids re-reading.
    """
    exclude_pages = exclude_pages or set()
    if page_cache is None:
        page_cache = {}

    def page_text(p: int) -> str:
        if p not in page_cache:
            page_cache[p] = read_page_text(
                pdf_path, p, pages_dir=pages_dir, layout=False
            )[:1500]
        return page_cache[p]

    moved = 0
    deltas: list[int] = []
    # Process in page order so the running adjustment grows monotonically.
    items_sorted = sorted(items, key=lambda x: x["page"])
    for it in items_sorted:
        if it.get("source") not in {"toc", "toc-no-offset", "font-analysis"}:
            continue
        if it.get("level", 1) > 1:
            continue
        # Apply running adjustment from prior snaps (median is robust to
        # one outlier; mean would let a single bad snap drag everything).
        if deltas:
            sorted_d = sorted(deltas[-5:])
            adj = sorted_d[len(sorted_d) // 2]
        else:
            adj = 0
        adjusted = it["page"] + adj
        candidates: list[int] = []
        for d in range(0, window + 1):
            for cand in (adjusted - d, adjusted + d) if d else (adjusted,):
                if 1 <= cand <= total_pages and cand not in exclude_pages \
                        and cand not in candidates:
                    candidates.append(cand)
        for cand in candidates:
            if fuzzy_contains(page_text(cand), it["title"]):
                if cand != it["page"]:
                    it["snapped_from"] = it["page"]
                    deltas.append(cand - it["page"])
                    it["page"] = cand
                    moved += 1
                break
    return moved


def cross_validate(pdf_path: str, entries: list[dict], offset: int,
                   total_pages: int,
                   exclude_pages: set[int] | None = None,
                   pages_dir: Path | None = None) -> list[dict]:
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
            text = read_page_text(pdf_path, p,
                                  pages_dir=pages_dir, layout=False)[:1500]
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
                      total_pages: int,
                      body_headings: list[dict] | None = None,
                      ) -> tuple[list[dict], dict]:
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

    # Path A: TOC parsed and offset is consistent.
    # Require >=3 probe matches; offset==0 with <4 matches is the
    # classic false-positive (a couple of early chapter titles fuzzy-
    # matched something before any real body text), so demand stronger
    # evidence in that specific case.
    strong_offset = offset_match_count >= 3 and not (
        offset == 0 and offset_match_count < 4
    )
    if toc_entries and strong_offset:
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
        if l1_bad_frac < 0.1 and offset_match_count >= 4:
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

    # Path C: Font analysis fallback. Only commit to font results if
    # there are at least 3 deduped headings AND the result has more
    # entries than the body-heading fallback would produce. Otherwise
    # fall through to Path D — a font-analysis pass with one or two
    # bogus matches (a stray figure caption, a page number rendered in
    # a slightly larger font) is worse than nothing.
    font_items: list[dict] = []
    if font_headings:
        candidate = [h for h in font_headings if h.get("level", 4) <= 2]
        seen_pages = set()
        for h in candidate:
            if h["page"] in seen_pages:
                continue
            font_items.append({
                "title": h["text"],
                "level": h["level"],
                "page": h["page"],
                "slug": slugify(h["text"]),
                "source": "font-analysis",
                "confidence": "medium",
            })
            seen_pages.add(h["page"])

    body_items_count = len(body_headings or [])
    use_font = font_items and len(font_items) >= 3 and \
        len(font_items) >= body_items_count
    if use_font:
        review["method"] = "font-analysis"
        review["confidence"] = "medium"
        review["needs_review"] = True
        review["summary"] = (
            f"No printed TOC found. Detected {len(font_items)} candidate "
            f"chapter heading(s) by font-size analysis. Review carefully "
            f"— this method has higher false-positive rates."
        )
        return font_items, review

    # Path D: Body-heading fallback (scanned/no-TOC books like rust-book).
    # Requires at least 3 distinct chapter-like headings to avoid
    # producing a near-degenerate outline.
    if body_headings and len(body_headings) >= 3:
        items = []
        for h in body_headings:
            items.append({
                "title": h["title"],
                "level": h.get("level", 1),
                "page": h["page"],
                "slug": h.get("slug") or slugify(h["title"]),
                "source": "body-headings",
                "confidence": "low",
            })
        review["method"] = "body-headings"
        review["confidence"] = "low"
        review["needs_review"] = True
        review["summary"] = (
            f"No printed TOC and no font-size signal. Detected "
            f"{len(items)} chapter-like heading(s) by scanning the first "
            f"few lines of every page. Review carefully — body-heading "
            f"detection has false positives, especially on books that "
            f"reuse 'Introduction'/'Conclusion' inside chapters."
        )
        return items, review

    # Path E: Nothing worked. Refuse to emit a single-chapter outline.
    # The caller will see has_outline:false plus exit-2 and must take
    # the vision-review path documented in SKILL.md §2c.
    review["method"] = "none"
    review["confidence"] = "none"
    review["summary"] = (
        "No bookmarks, no parseable TOC, no font-size signal, no body "
        "headings. Cannot infer chapter structure automatically. "
        "Rasterize the first ~25 pages and hand-write outline.json "
        "(see SKILL.md §2c)."
    )
    review["next_action"] = "vision-review"
    return [], review


# --- Self-test (TOC pattern smoke tests) ---


def run_self_test() -> None:
    """Smoke-test the TOC line patterns. Run with --self-test."""
    cases: list[tuple[str, str, int]] = [
        # (line, expected title, expected page)
        ("    1.1 Setup ......... 11", "1.1 Setup", 11),
        ("Chapter 10 Transferred-Electron Devices 510",
         "Chapter 10 Transferred-Electron Devices", 510),
        ("    Preface          vii", "Preface", 7),  # roman vii → 7
        # OCR'd separators (slash / comma stand in for right-aligned
        # page numbers that tesseract collapsed onto the title line).
        ("1. FUNDAMENTAL CONCEPTS / 1", "1. FUNDAMENTAL CONCEPTS", 1),
        ("Chapter 5 Sensitivities / 152", "Chapter 5 Sensitivities", 152),
        ("Frequency Domain Analysis , 234",
         "Frequency Domain Analysis", 234),
        # Section-numbered, single-space-separated trailing page —
        # the format `synthesis-and-optimization-of-digital-circuits`
        # OCR'd into.
        ("5.8 References 225", "5.8 References", 225),
        ("6 Resource Sharing and Binding 229",
         "6 Resource Sharing and Binding", 229),
        ("6.2.1 Resource Sharing in Non-Hierarchical Sequencing Graphs 233",
         "6.2.1 Resource Sharing in Non-Hierarchical Sequencing Graphs",
         233),
    ]
    failures: list[str] = []
    for line, expected_title, expected_page in cases:
        entries = parse_toc_lines([line])
        if len(entries) != 1:
            failures.append(
                f"{line!r}: expected 1 entry, got {len(entries)}"
            )
            continue
        e = entries[0]
        # Title comparison: parse_toc_lines normalizes whitespace and
        # strips trailing dots, so compare loosely.
        got_title = re.sub(r"\s+", " ", e["title"]).strip()
        want_title = re.sub(r"\s+", " ", expected_title).strip()
        if got_title != want_title:
            failures.append(
                f"{line!r}: title {got_title!r} != {want_title!r}"
            )
        if e["printed_page"] != expected_page:
            failures.append(
                f"{line!r}: page {e['printed_page']} != {expected_page}"
            )

    if failures:
        print("self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print(f"self-test passed ({len(cases)} cases)")


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
    ap.add_argument("--pages-dir", default=None,
                    help="Directory of page_NNNN.md files (from "
                         "extract_text_pages.py / ocr_pages.py). When given, "
                         "all text reads come from these files instead of "
                         "calling pdftotext on the PDF — required for scanned "
                         "PDFs whose text layer is empty.")
    ap.add_argument("--self-test", action="store_true",
                    help="Run TOC-pattern smoke tests and exit.")
    args = ap.parse_args()

    if args.self_test:
        run_self_test()
        return

    if not os.path.exists(args.pdf):
        print(f"ERROR: {args.pdf} not found", file=sys.stderr)
        sys.exit(1)

    pages_dir: Path | None = None
    if args.pages_dir:
        pages_dir = Path(args.pages_dir)
        if not pages_dir.is_dir():
            print(f"ERROR: --pages-dir {pages_dir} is not a directory",
                  file=sys.stderr)
            sys.exit(2)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    total_pages = get_page_count(args.pdf)
    print(f"Document: {total_pages} pages", file=sys.stderr)

    # Scanned-PDF early bail: if pdftotext returns ~nothing on the first
    # 3 pages and the caller did not provide pre-extracted pages, we
    # cannot do TOC scanning (no text to scan). Tell the caller to OCR
    # first instead of producing a degenerate outline.
    if pages_dir is None:
        sample_chars = sum(
            len(pdftotext_page(args.pdf, p, layout=False))
            for p in range(1, min(3, total_pages) + 1)
        )
        if sample_chars < 50:
            print(
                "detect_structure: this PDF appears to be scanned (no "
                "extractable text on first 3 pages).\n"
                "Run ocr_pages.py first, then re-invoke with "
                "--pages-dir <work>/pages.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Step 1: Detect TOC pages
    print("Scanning for printed table of contents...", file=sys.stderr)
    toc_pages = detect_toc_pages(args.pdf, total_pages,
                                 max_scan=args.max_scan,
                                 threshold=args.toc_threshold,
                                 pages_dir=pages_dir)
    if toc_pages:
        print(f"  candidate TOC pages: {toc_pages}", file=sys.stderr)
    else:
        print("  no TOC pages detected", file=sys.stderr)

    # Step 2: Parse TOC
    toc_entries: list[dict] = []
    if toc_pages:
        toc_text_blocks = [
            read_page_text(args.pdf, p, pages_dir=pages_dir, layout=True)
            for p in toc_pages
        ]
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
            pages_dir=pages_dir,
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
    # Shared body-text cache reused across body-scan, snap, and any
    # follow-up cross-validations so each page is read at most once.
    body_page_cache: dict[int, str] = {}
    issues: list[dict] = []
    if toc_entries and offset_count >= 1:
        issues = cross_validate(args.pdf, toc_entries, offset, total_pages,
                                exclude_pages=set(toc_pages),
                                pages_dir=pages_dir)
        if issues:
            print(f"  {len(issues)} cross-validation issue(s)", file=sys.stderr)

        # Step 5b: If most chapter-level entries failed to validate at the
        # estimated offset, the offset itself is probably wrong. Recover
        # by scanning the whole body for first-occurrences and re-deriving.
        l1_arabic = [e for e in toc_entries
                     if e["page_kind"] == "arabic" and e.get("level", 1) == 1]
        l1_critical = [
            i for i in issues
            if i["issue"] != "found-on-neighbor"
            and any(e["title"] == i["title"] and e.get("level", 1) == 1
                    for e in toc_entries)
        ]
        if l1_arabic and len(l1_critical) / len(l1_arabic) >= 0.5:
            print(f"  >=50% of chapter-level entries failed to validate at "
                  f"offset {offset:+d} — refining via full-body scan...",
                  file=sys.stderr)
            refined_offset, refined_count = refine_offset_via_body_scan(
                args.pdf, toc_entries, total_pages,
                exclude_pages=set(toc_pages),
                page_cache=body_page_cache,
                pages_dir=pages_dir,
            )
            print(f"    body-scan: offset={refined_offset:+d} from "
                  f"{refined_count} entry(ies)", file=sys.stderr)
            if refined_count >= max(3, offset_count) and refined_offset != offset:
                refined_issues = cross_validate(
                    args.pdf, toc_entries, refined_offset, total_pages,
                    exclude_pages=set(toc_pages),
                    pages_dir=pages_dir,
                )
                refined_l1_critical = [
                    i for i in refined_issues
                    if i["issue"] != "found-on-neighbor"
                    and any(e["title"] == i["title"] and e.get("level", 1) == 1
                            for e in toc_entries)
                ]
                if len(refined_l1_critical) < len(l1_critical):
                    print(f"  refined: offset {offset:+d} ({len(l1_critical)} "
                          f"L1 issues) → {refined_offset:+d} "
                          f"({len(refined_l1_critical)} L1 issues, "
                          f"{refined_count} entries agree)",
                          file=sys.stderr)
                    offset = refined_offset
                    offset_count = refined_count
                    offset_method = f"body-scan-refined-{refined_count}-entries"
                    issues = refined_issues

    # Step 6: Rasterize TOC pages for review
    toc_images: list[str] = []
    if toc_pages:
        toc_images = rasterize_pages(
            args.pdf, toc_pages, out_dir / "toc-images", dpi=150
        )
        if toc_images:
            print(f"  rasterized {len(toc_images)} TOC page(s) for review",
                  file=sys.stderr)

    # Step 6b: Body-heading scan — third-tier fallback used when no
    # strong TOC offset was established. We always run it (when
    # pages_dir is available) so reconcile_signals can fall back to
    # body-headings if font-analysis turns out to be weak. Cost is one
    # cached read per page.
    body_heading_items: list[dict] = []
    if pages_dir is not None and (not toc_entries or offset_count < 1):
        print("Scanning body for chapter-like headings...", file=sys.stderr)
        body_heading_items = detect_body_headings(
            args.pdf, total_pages, pages_dir,
            page_cache=body_page_cache,
        )
        print(f"  detected {len(body_heading_items)} body heading(s)",
              file=sys.stderr)

    # Step 7: Reconcile
    items, review = reconcile_signals(
        toc_entries, offset, offset_count,
        font_data.get("headings", []), issues, total_pages,
        body_headings=body_heading_items,
    )

    # Step 7b: Per-chapter anchoring. Books with Part separators have
    # varying offsets across chapters; a single global offset puts each
    # chapter slightly off. Snap each L1 entry to the nearest body page
    # whose text actually contains the title (within ±15 pages).
    if items and toc_entries:
        snapped = snap_entries_to_body_titles(
            args.pdf, items, total_pages,
            exclude_pages=set(toc_pages),
            page_cache=body_page_cache,
            pages_dir=pages_dir,
        )
        if snapped:
            print(f"  per-chapter anchoring snapped {snapped} entry(ies) "
                  f"to actual body positions", file=sys.stderr)
            # Re-run cross-validation against the snapped pages so the
            # review accurately reflects post-snap quality.
            snapped_issues = cross_validate(
                args.pdf,
                [{**e, "printed_page": next(
                    (it["page"] for it in items if it["title"] == e["title"]),
                    e["printed_page"] + offset,
                )} for e in toc_entries],
                0, total_pages, exclude_pages=set(toc_pages),
                pages_dir=pages_dir,
            )
            review["issues"] = snapped_issues
            l1_total = sum(1 for e in toc_entries if e.get("level", 1) == 1)
            l1_critical = sum(
                1 for i in snapped_issues
                if i["issue"] != "found-on-neighbor"
                and any(e["title"] == i["title"] and e.get("level", 1) == 1
                        for e in toc_entries)
            )
            review["summary"] = (
                f"Detected {len(items)} entries from printed TOC. "
                f"Page offset {offset:+d} ({offset_method}). "
                f"Per-chapter anchoring snapped {snapped} entry(ies). "
                f"Chapter-level issues after snap: {l1_critical}/{l1_total}."
            )
            # If anchoring resolved most issues, upgrade confidence.
            if l1_total and l1_critical / l1_total < 0.1:
                review["confidence"] = "high"
                review["needs_review"] = False
            elif l1_total and l1_critical / l1_total < 0.25:
                review["confidence"] = "medium"

    # Outputs
    outline = {
        "has_outline": len(items) > 0,
        "items": items,
        "source": review["method"],
        "page_offset": offset,
    }
    (out_dir / "outline.json").write_text(json.dumps(outline, indent=2))

    # If detection failed entirely, rasterize the first ~25 pages so the
    # caller can drop straight into the vision-review path.
    review_images: list[str] = list(toc_images)
    if not items:
        first_pages = list(range(1, min(25, total_pages) + 1))
        extra = rasterize_pages(
            args.pdf, first_pages, out_dir / "toc-images", dpi=150
        )
        if extra:
            print(f"  rasterized first {len(extra)} pages for vision review",
                  file=sys.stderr)
            review_images = sorted(set(review_images) | set(extra))

    review["toc_pages_pdf"] = toc_pages
    review["rasterized_toc_pages"] = review_images
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
    if review_images:
        print(f"  {len(review_images)} review image(s) in {out_dir / 'toc-images'}/")
    if not items:
        print(
            "\n✗ STRUCTURE DETECTION FAILED. No bookmarks, no usable TOC, "
            "no font signal, no body headings.",
            file=sys.stderr,
        )
        print(
            f"  → View the rasterized images in {out_dir / 'toc-images'}/ "
            "and hand-write outline.json (see SKILL.md §2c).",
            file=sys.stderr,
        )
        sys.exit(2)
    if review.get("needs_review"):
        print("\n⚠ NEEDS REVIEW. Open outline_review.json for details.")
        if review_images:
            print(f"  → View the TOC images in {out_dir / 'toc-images'}/")
            print("    and edit outline.json to reflect what you see.")
    else:
        print("\n✓ High confidence. Safe to proceed to assemble_chapters.py.")


if __name__ == "__main__":
    main()
