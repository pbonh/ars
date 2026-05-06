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


# PDFs use a wide range of hyphen-like glyphs. We treat all of them as
# soft-break candidates: ASCII '-', U+2010 HYPHEN, U+2011 NON-BREAKING
# HYPHEN, U+2212 MINUS SIGN, U+00AD SOFT HYPHEN.
_HYPHEN_CHARS = "-‐‑−­"
_HYPHEN_CLASS = f"[{_HYPHEN_CHARS}]"
_DEHYPHENATE_RE = re.compile(rf"(\w){_HYPHEN_CLASS}\n[ \t]*\n?[ \t]*([a-z])")
_INLINE_SOFT_HYPHEN_RE = re.compile(r"­")

# Leading section-number prefix in a title — '5.3', '2.2.1', etc.
# Used both for SUMMARY-level derivation and as a precise cut anchor
# when splitting a shared page between two chapters.
_SECTION_NUMBER_RE = re.compile(r"^(\d+(?:\.\d+)+)\b")


def dehyphenate(text: str) -> str:
    """Join 'compre-\\nhensive' → 'comprehensive'.

    Heuristic: a hyphen at end of line followed by a lowercase letter
    on the next line is almost always a soft break. We don't join when
    the second part starts with uppercase (likely a real compound or
    proper noun). Allow arbitrary intervening whitespace (including a
    blank line) so this catches both line-break and page-break splits.
    Recognizes ASCII and Unicode hyphens (U+2010, U+2011, U+2212) plus
    soft hyphens (U+00AD).
    """
    # Soft hyphens are non-printing by definition — strip mid-word
    # occurrences before any line-rejoin pass so 'pro­vide' doesn't
    # survive as 'pro vide'.
    text = _INLINE_SOFT_HYPHEN_RE.sub("", text)
    return _DEHYPHENATE_RE.sub(r"\1\2", text)


def collapse_blanklines(text: str) -> str:
    """3+ blank lines → 2 (single paragraph break)."""
    return re.sub(r"\n{3,}", "\n\n", text)


_EDGE_WINDOW = 6


def _header_fingerprint(line: str) -> str:
    """Hash key for header detection.

    Recto/verso pages alternate header position and page number, so
    ``44 BOOK TITLE`` and ``BOOK TITLE 45`` should hash to the same
    ``BOOK TITLE`` for the frequency tally. Strips leading/trailing
    page-number-likes and lowercases.
    """
    s = re.sub(r"\s+", " ", line).strip()
    s = re.sub(r"^\d+\s+", "", s)
    s = re.sub(r"\s+\d+$", "", s)
    return s.lower()


def strip_repeated_lines(pages_text: list[str], frac: float = 0.5) -> list[str]:
    """Find lines (top _EDGE_WINDOW + bottom _EDGE_WINDOW of each page) that
    recur on >frac of pages and remove them. Catches running headers and
    footers, including ones that share text but alternate page numbers."""
    if not pages_text:
        return pages_text

    candidates: collections.Counter = collections.Counter()
    page_count = len(pages_text)

    for page in pages_text:
        lines = page.splitlines()
        # Inspect the outer EDGE_WINDOW lines on each side. Many books
        # render a blank line + chapter banner + blank line at the top,
        # so a 3-line window misses the banner.
        top = [l.strip() for l in lines[:_EDGE_WINDOW] if l.strip()]
        bot = [l.strip() for l in lines[-_EDGE_WINDOW:] if l.strip()]
        seen: set[str] = set()
        for l in top + bot:
            if re.fullmatch(r"\d{1,4}", l):
                continue
            if not (3 <= len(l) <= 80):
                continue
            fp = _header_fingerprint(l)
            if not fp or fp in seen:
                continue
            seen.add(fp)
            candidates[fp] += 1

    # Require count ≥ 2 always: a "running header" must, by definition,
    # actually repeat. The `frac` knob only kicks in once the chapter
    # has enough pages for it to be meaningful (otherwise threshold=1
    # would strip every unique body line on a tiny chapter).
    threshold = max(2, frac * page_count)
    repeated_fps = {fp for fp, count in candidates.items() if count >= threshold}

    cleaned_pages = []
    for page in pages_text:
        lines = page.splitlines()
        new = []
        for i, l in enumerate(lines):
            stripped = l.strip()
            in_edge = i < _EDGE_WINDOW or i >= len(lines) - _EDGE_WINDOW
            if in_edge:
                if _header_fingerprint(stripped) in repeated_fps:
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


def _levenshtein(a: str, b: str, cap: int = 4) -> int:
    """Bounded edit distance. Returns ``cap`` once the threshold is exceeded.

    We only care about merging titles that are 'almost identical'
    (slugifier variants, stray whitespace), so capping at a small value
    keeps the cost flat for the long-prose case.
    """
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) >= cap:
        return cap
    if la > lb:
        a, b, la, lb = b, a, lb, la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * lb
        best = cur[0]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            cur[j] = min(ins, dele, sub)
            best = min(best, cur[j])
        if best >= cap:
            return cap
        prev = cur
    return min(prev[lb], cap)


def dedupe_outline(items: list[dict]) -> tuple[list[dict], list[dict]]:
    """Merge near-duplicate adjacent outline items.

    Returns ``(deduped_items, dropped_items)``. Two items are merged
    when their titles are within edit-distance 3 of each other OR they
    target the same start page. The survivor keeps the longer/cleaner
    title; the duplicate's slug is recorded under ``aliases`` so a
    later cross-check can detect orphan files written with the
    abandoned slug.
    """
    if not items:
        return [], []
    sorted_items = sorted(items, key=lambda x: (x.get("page") or 0,
                                                x.get("level", 1)))
    keep: list[dict] = []
    dropped: list[dict] = []
    for it in sorted_items:
        if not keep:
            keep.append(it)
            continue
        prev = keep[-1]
        same_page = it.get("page") == prev.get("page")
        title_a = (it.get("title") or "").strip().lower()
        title_b = (prev.get("title") or "").strip().lower()
        close = title_a and title_b and _levenshtein(title_a, title_b) < 3
        if close:
            # Pick the longer/cleaner title; merge slugs.
            survivor, loser = (prev, it) if len(prev["title"]) >= len(it["title"]) \
                else (it, prev)
            keep[-1] = survivor
            aliases = list(set(prev.get("aliases", [])
                               + it.get("aliases", [])
                               + [loser.get("slug")]))
            keep[-1]["aliases"] = [a for a in aliases if a]
            dropped.append(loser)
            continue
        keep.append(it)
    return keep, dropped


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
    # Mirrors detect_structure.BODY_STRUCTURAL_HEADING: tight pattern
    # that rejects body prose like ``Chapter 13. In order to solve…``
    # by requiring the optional title to be uppercase (typical of
    # OCR'd / scanned headings) and anchoring at end-of-line. The
    # previous loose ``.*$`` swallowed full sentences after the chapter
    # number, producing dozens of bogus chapters.
    chapter_re = re.compile(
        r"^\s*(?i:chapter|part|book|section|appendix|appendices)"
        r"\s+(?:\d+|[IVXLCDMivxlcdm]+|[A-Z])\b"
        r"(?:[\s:.\-—]+[A-Z][A-Z\s.\d&'\"\-—()]{1,80})?\s*$",
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


def _title_match_pattern(title: str) -> re.Pattern | None:
    """Build a forgiving line-anchored regex for cutting at a chapter title.

    Prefers an exact section-number prefix when present (e.g. ``5.3``
    or ``2.2.1``) since those are the most reliable signal. Otherwise
    matches the first 3-4 significant words of the title. Returns
    ``None`` when nothing usable can be derived.
    """
    title = (title or "").strip()
    if not title:
        return None
    sec_m = _SECTION_NUMBER_RE.match(title)
    if sec_m:
        prefix = sec_m.group(1)
        # Anchor with the first 1-2 words AFTER the section number so
        # we don't cut at `(see 5.1)`, a citation, or a stray TOC echo
        # in body text. Real headings have the title body on the same
        # line as the number.
        body_tokens = [t for t in re.split(r"\s+", title[len(prefix):].strip())
                       if t][:2]
        if body_tokens:
            body_pat = r"\s+".join(re.escape(t) for t in body_tokens)
            return re.compile(
                rf"(?m)^\s*{re.escape(prefix)}\s+{body_pat}\b",
                re.IGNORECASE,
            )
        return re.compile(rf"(?m)^\s*{re.escape(prefix)}\b")
    # Use the first 3-4 words; require ≥10 chars total to avoid
    # matching short stop-words like "the" alone.
    tokens = [t for t in re.split(r"\s+", title) if t]
    head = tokens[:4]
    if not head:
        return None
    head_str = " ".join(head)
    if len(head_str) < 10:
        head = tokens[:6]
        head_str = " ".join(head)
        if len(head_str) < 8:
            return None
    pat = r"\s+".join(re.escape(t) for t in head)
    return re.compile(rf"(?m)^\s*{pat}", re.IGNORECASE)


def _split_shared_page(page_text: str, next_item: dict) -> tuple[str, str] | None:
    """Cut a shared page at the next chapter's title.

    Returns ``(head_for_prev, tail_for_next)`` or ``None`` if no
    confident split point is found. We're conservative — if the title
    pattern doesn't match cleanly, we fall back to letting the caller
    keep the existing whole-page assignment.
    """
    pat = _title_match_pattern(next_item.get("title", ""))
    if pat is None:
        return None
    m = pat.search(page_text)
    if not m:
        return None
    cut = m.start()
    head = page_text[:cut]
    tail = page_text[cut:]
    # Refuse to split when the head is essentially empty — that means
    # the title is at the top of the page, so the whole page already
    # belongs to ``next_item`` (the existing behavior is correct).
    if not head.strip():
        return None
    return head, tail


_FIG_CAPTION_RE = re.compile(
    r"^(?P<prefix>\s*)Fig(?:ure)?\.?\s+(?P<num>\d+(?:\.\d+)?)\b.*$",
    re.MULTILINE,
)


def load_figures_manifest(pages_dir: Path) -> dict[int, list[dict]]:
    """Return a {page: [figure_record, ...]} map from figures_manifest.json.

    Looks alongside ``manifest.json`` in ``pages_dir``. Returns an
    empty mapping if the manifest is absent (figures step is optional).
    """
    path = pages_dir / "figures_manifest.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}
    by_page: dict[int, list[dict]] = {}
    for fig in data.get("figures", []):
        p = fig.get("page")
        if p is None:
            continue
        by_page.setdefault(p, []).append(fig)
    for figs in by_page.values():
        figs.sort(key=lambda f: f.get("index", 0))
    return by_page


def insert_figure_references(chapter_text: str, page_range: tuple[int, int],
                             figures_by_page: dict[int, list[dict]]) -> str:
    """Splice ``![](images/figure_pNNNN_M.ext)`` after caption lines.

    Strategy:
      1. For each caption line ``Figure 3.1 — ...`` matched in the
         chapter, attach the next unused figure record from the
         caption's page (or surrounding pages in the chapter range).
      2. Any unmatched figures from the chapter's page range are
         appended at the end of the chapter so they aren't lost.
    """
    if not figures_by_page:
        return chapter_text

    used: set[str] = set()

    def take_figure(page: int) -> dict | None:
        for fig in figures_by_page.get(page, []):
            if fig["file"] not in used:
                used.add(fig["file"])
                return fig
        return None

    def replacer(match: re.Match) -> str:
        # Caption page is unknown without a positional map; instead,
        # look at all pages in range in order, returning the first
        # unused figure. This is approximate but works for chapters
        # that have one figure per caption in reading order.
        for p in range(page_range[0], page_range[1] + 1):
            fig = take_figure(p)
            if fig is not None:
                return f"{match.group(0)}\n\n![](images/{fig['file']})"
        return match.group(0)

    new_text = _FIG_CAPTION_RE.sub(replacer, chapter_text)

    # Append leftovers — figures present on chapter pages that no
    # caption claimed. Better to surface them than lose them.
    leftovers: list[dict] = []
    for p in range(page_range[0], page_range[1] + 1):
        for fig in figures_by_page.get(p, []):
            if fig["file"] not in used:
                used.add(fig["file"])
                leftovers.append(fig)
    if leftovers:
        tail = "\n\n" + "\n\n".join(
            f"![](images/{f['file']})" for f in leftovers)
        new_text = new_text + tail
    return new_text


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

    # Pre-load page texts so we can rewrite shared pages in place.
    page_lookup: dict[int, str] = {}
    for entry in manifest["pages"]:
        page_lookup[entry["page"]] = (pages_dir / entry["file"]).read_text()

    # When two consecutive chapters share a PDF page (start_B == end_A,
    # i.e. chapter B begins mid-page), cut the shared page at B's
    # title. The head stays with A; the tail (heading + body) goes to
    # B. Falls back to the original whole-page behavior when the
    # title pattern doesn't match — better to leak a paragraph than to
    # mangle a chapter on a bad guess.
    chapter_text: dict[int, list[str]] = {i: [] for i in range(len(ranges))}
    for i, r in enumerate(ranges):
        for p in range(r["start"], r["end"] + 1):
            text = page_lookup.get(p, "")
            chapter_text[i].append(text)

    # Boundary cleanup. Bookmarks frequently point at the *page* a
    # chapter starts on, even when the chapter's heading appears
    # mid-page (preceded by the previous chapter's tail). Scan each
    # boundary: look at chapter B's first page for B's title, and if
    # any non-trivial content precedes the title, that content is
    # actually chapter A's tail — reassign it.
    #
    # Two range shapes are handled by the same code:
    #   1. Non-overlapping ranges (A.end == B.start - 1, the common
    #      case). A doesn't yet include B.start; the head is appended
    #      to A as an extra page slot.
    #   2. Same-bookmark ranges (A.end == B.start, e.g. parent + first
    #      child both point at the same page). A and B both have the
    #      page; the head replaces A's last slot and the tail replaces
    #      B's first slot.
    for i in range(1, len(ranges)):
        A = ranges[i - 1]
        B = ranges[i]
        b_first = B["start"]
        b_first_text = page_lookup.get(b_first, "")
        if not b_first_text:
            continue
        split = _split_shared_page(b_first_text, B["item"])
        if split is None:
            continue
        head, tail = split
        # Hand the head to chapter A.
        if A["end"] == b_first:
            # A already includes this page (same-bookmark case).
            if chapter_text[i - 1]:
                chapter_text[i - 1][-1] = head
            else:
                chapter_text[i - 1] = [head]
        else:
            # A's range stops before this page; extend A by appending
            # the head as an extra slot.
            chapter_text[i - 1].append(head)
        # Replace B's first page with the tail (heading + body).
        if chapter_text[i]:
            chapter_text[i][0] = tail
        else:
            chapter_text[i] = [tail]
        print(f"  reassigned mid-page tail at PDF page {b_first}: "
              f"{A['item'].get('slug')!r} ← head, "
              f"{B['item'].get('slug')!r} ← tail",
              file=sys.stderr)

    figures_by_page = load_figures_manifest(pages_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for i, r in enumerate(ranges):
        item = r["item"]
        page_texts = chapter_text.get(i, [])

        # Cleanup pipeline
        page_texts = strip_repeated_lines(page_texts, frac=header_strip_frac)
        joined = "\n\n".join(page_texts)
        joined = normalize_ligatures(joined)
        joined = dehyphenate(joined)
        joined = collapse_blanklines(joined)
        joined = normalize_chapter_heading(joined, item["title"])
        joined = insert_figure_references(joined, (r["start"], r["end"]),
                                          figures_by_page)

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


def _section_number_level(title: str) -> int | None:
    """Derive nesting level from a leading section number ('5.3' → 2).

    Bookmark levels frequently disagree with section numbering — the
    title prefix is the more trustworthy signal. Returns None when the
    title doesn't open with a multi-segment numeric prefix.
    """
    m = _SECTION_NUMBER_RE.match(title)
    if not m:
        return None
    return m.group(1).count(".") + 1


def derive_summary_levels(items: list[dict]) -> list[int]:
    """Return per-item display levels for SUMMARY indentation.

    For each item: prefer the level derived from a leading section
    number (e.g. ``5.3`` → 2) when more specific than the bookmark
    level. Then enforce monotone-with-siblings: if item N's title
    prefix is ``5.3`` and item N-1's prefix is ``5.2``, item N must be
    at the same level as N-1.
    """
    derived: list[int | None] = [_section_number_level(it["title"]) for it in items]
    levels: list[int] = []
    for i, it in enumerate(items):
        bm = max(1, int(it.get("level", 1) or 1))
        d = derived[i]
        lvl = bm if d is None else max(bm, d)
        # Match a sibling immediately above (same numeric depth) — if
        # the bookmark put us deeper or shallower than our sibling, the
        # section number wins.
        if d is not None and i > 0 and derived[i - 1] is not None:
            prev_d = derived[i - 1]
            if d == prev_d:
                lvl = levels[-1]
        levels.append(lvl)
    return levels


def write_summary(items: list[dict], out_path: Path, title: str):
    """Write a draft SUMMARY.md respecting mdBook's strict format."""
    lines = [f"# {title}", ""]

    levels = derive_summary_levels(items)
    for item, lvl in zip(items, levels):
        indent = "  " * (lvl - 1)
        lines.append(f"{indent}- [{item['title']}]({item['file']})")

    out_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_path}", file=sys.stderr)


# --- Self-test ---


def _assert(cond: bool, label: str, failures: list[str], detail: str = "") -> None:
    if not cond:
        msg = label
        if detail:
            msg += f" — {detail}"
        failures.append(msg)


def run_self_test() -> None:
    """Smoke-test the cleanup pipeline. Run with --self-test.

    These cases pin the most regression-prone behaviors:
      - mid-page boundary handling (the 5.1 defect)
      - inline-citation false-positive guard
      - Unicode / soft-hyphen dehyphenation
      - recto/verso header fingerprinting
      - section-number-aware SUMMARY levels
      - outline dedupe of slug-variant titles
      - strip_repeated_lines preserves unique body lines on small chapters
      - end-to-end assemble() on a synthetic 3-chapter book with the
        mid-page boundary shape we just had to fix
    """
    import json
    import shutil
    import tempfile

    failures: list[str] = []

    # 1. _split_shared_page — mid-page heading splits cleanly.
    page_with_spillover = (
        "graphs for a given determinant. One simple way to construct.\n\n"
        "5.1 Terms-Detecting Logic for a Determinant\n\n"
        "The DDD graph is introduced.\n"
    )
    split = _split_shared_page(
        page_with_spillover,
        {"title": "5.1 Terms-Detecting Logic for a Determinant"},
    )
    _assert(split is not None, "split_shared_page: mid-page heading", failures)
    if split is not None:
        head, tail = split
        _assert("graphs for a given determinant" in head,
                "split: head contains spillover prose", failures,
                detail=repr(head[:60]))
        _assert(tail.lstrip().startswith("5.1 Terms-Detecting"),
                "split: tail starts at heading", failures,
                detail=repr(tail[:40]))

    # 2. Title at top of page → no split (clean boundary).
    page_clean_top = (
        "5.1 Terms-Detecting Logic for a Determinant\n\n"
        "The DDD graph is introduced.\n"
    )
    _assert(
        _split_shared_page(page_clean_top,
                           {"title": "5.1 Terms-Detecting Logic for a Determinant"})
        is None,
        "split_shared_page: title at top → no split", failures,
    )

    # 3. Inline citation only ("see Section 5.1") → no split.
    page_citation_only = (
        "See section 5.1 for details, then continue.\n"
        "Body text continues here.\n"
    )
    _assert(
        _split_shared_page(
            page_citation_only,
            {"title": "5.1 Terms-Detecting Logic for a Determinant"},
        ) is None,
        "split_shared_page: inline citation does not trigger split",
        failures,
    )

    # 4. Plain (non-section-numbered) title splits when present mid-page.
    page_plain_split = (
        "End of previous section paragraph.\n\n"
        "Introduction to the New Topic\n\n"
        "Body of new topic.\n"
    )
    res = _split_shared_page(page_plain_split,
                             {"title": "Introduction to the New Topic"})
    _assert(res is not None, "split_shared_page: plain title mid-page", failures)
    if res is not None:
        _assert(res[1].lstrip().startswith("Introduction to the New Topic"),
                "split: plain-title tail starts at heading", failures)

    # 5. dehyphenate — Unicode hyphens + soft-hyphen pre-pass.
    cases = [
        ("pro‐\nvide later", "provide later"),       # U+2010 HYPHEN
        ("build‑\ning", "building"),                  # U+2011 NB-HYPHEN
        ("multi−\nple", "multiple"),                  # U+2212 MINUS
        ("pro­vide", "provide"),                      # U+00AD soft hyphen
        ("compre-\nhensive", "comprehensive"),             # ASCII (regression)
        ("Bob-\nGreen", "Bob-\nGreen"),                    # uppercase: keep
    ]
    for src, want in cases:
        got = dehyphenate(src)
        _assert(got == want, f"dehyphenate({src!r})", failures,
                detail=f"got {got!r}, want {want!r}")

    # 6. _header_fingerprint — recto/verso variants collapse.
    fp_a = _header_fingerprint("44 BOOK TITLE")
    fp_b = _header_fingerprint("BOOK TITLE 45")
    _assert(fp_a == fp_b, "header_fingerprint: recto/verso collapse",
            failures, detail=f"{fp_a!r} vs {fp_b!r}")

    # 7. derive_summary_levels — section number wins over bookmark level.
    items = [
        {"title": "5.1 Foo", "level": 2},
        {"title": "5.2 Bar", "level": 2},
        {"title": "5.3 Baz", "level": 6},   # bad bookmark level
        {"title": "Chapter 6", "level": 1},
    ]
    levels = derive_summary_levels(items)
    _assert(levels[:3] == [2, 2, 2],
            "derive_summary_levels: 5.1/5.2/5.3 share level 2",
            failures, detail=str(levels))
    _assert(levels[3] == 1, "derive_summary_levels: chapter 6 → level 1",
            failures, detail=str(levels))

    # 8. dedupe_outline — slugifier variants merge.
    deduped, dropped = dedupe_outline([
        {"title": "AHDLs and MS-HDLs", "page": 10, "level": 1,
         "slug": "ahdls-ms-hdls"},
        {"title": "AHDLs and MS HDLs", "page": 10, "level": 1,
         "slug": "ahdls-and-ms-hdls"},
        {"title": "Chapter 2", "page": 20, "level": 1, "slug": "chapter-2"},
    ])
    _assert(len(deduped) == 2 and len(dropped) == 1,
            "dedupe_outline: collapses near-duplicate adjacent items",
            failures,
            detail=f"keep={[i['slug'] for i in deduped]} "
                   f"drop={[i['slug'] for i in dropped]}")

    # 9. strip_repeated_lines — unique body lines on small chapter survive.
    pages = ["# Chapter 1\n\nFirst chapter body.\n",
             "More chapter 1 body.\n"]
    out = strip_repeated_lines(pages, frac=0.5)
    joined = "\n".join(out)
    _assert("First chapter body." in joined and "More chapter 1 body." in joined,
            "strip_repeated_lines: small-chapter unique lines preserved",
            failures, detail=repr(out))

    # 10. End-to-end assemble() on a synthetic 3-chapter book where
    #     section 5.1 starts mid-page on page 105 and section 5.2 starts
    #     mid-page on page 108. Both ends must come out clean.
    tmp = Path(tempfile.mkdtemp(prefix="assemble-self-test-"))
    try:
        pages_text = {
            100: "# Chapter 5\n\nChapter 5 introduction begins.\n",
            101: "More intro about DDDs.\n",
            102: "Continuation of intro.\n",
            103: "Approaching the section.\n",
            104: "Chapter 5 intro is wrapping up.\n",
            105: ("graphs for a given determinant. Spillover prose.\n\n"
                  "5.1 Terms-Detecting Logic for a Determinant\n\n"
                  "The DDD graph is introduced.\n"),
            106: "More 5.1 body.\n",
            107: "End of 5.1 page 107.\n",
            108: ("We simply compare the row/column index of the elements.\n"
                  "Final 5.1 prose ending here.\n\n"
                  "5.2 Implicit Symbolic Term Generation\n\n"
                  "5.2 body begins.\n"),
            109: "More 5.2 body.\n",
            110: "End of 5.2.\n",
        }
        pages_dir = tmp / "pages"
        pages_dir.mkdir()
        manifest = {"pages": []}
        for p, t in pages_text.items():
            (pages_dir / f"page_{p:04d}.md").write_text(t)
            manifest["pages"].append({"page": p, "file": f"page_{p:04d}.md",
                                      "chars": len(t)})
        (pages_dir / "manifest.json").write_text(json.dumps(manifest))
        outline = [
            {"title": "Chapter 5 Implicit Symbolic Generation",
             "level": 1, "page": 100, "slug": "chapter-5"},
            {"title": "5.1 Terms-Detecting Logic for a Determinant",
             "level": 2, "page": 105, "slug": "5-1-terms"},
            {"title": "5.2 Implicit Symbolic Term Generation",
             "level": 2, "page": 108, "slug": "5-2-implicit"},
        ]
        out_dir = tmp / "out"
        written = assemble(outline, pages_dir, manifest, out_dir,
                           header_strip_frac=0.5)
        files = {w["slug"]: (out_dir / w["file"]).read_text() for w in written}

        # chapter-5 must absorb the spillover head from page 105.
        ch5 = files.get("chapter-5", "")
        _assert("Spillover prose" in ch5,
                "assemble: chapter 5 absorbs page-105 head", failures,
                detail=repr(ch5[-80:]))
        _assert("5.1 Terms-Detecting" not in ch5,
                "assemble: 5.1 heading does NOT leak into chapter 5",
                failures)

        # 5.1 must NOT carry the chapter-5 spillover, AND must include
        # its own tail that spilled onto page 108 (before 5.2).
        s51 = files.get("5-1-terms", "")
        _assert("Spillover prose" not in s51,
                "assemble: 5.1 does NOT start with chapter-5 spillover",
                failures, detail=repr(s51[:120]))
        _assert("Final 5.1 prose ending here." in s51,
                "assemble: 5.1 reclaims its tail from page 108", failures,
                detail=repr(s51[-120:]))
        _assert("5.2 Implicit" not in s51,
                "assemble: 5.2 heading does NOT bleed into 5.1", failures)

        # 5.2 starts cleanly at its heading.
        s52 = files.get("5-2-implicit", "")
        _assert(s52.lstrip().startswith("# 5.2 Implicit"),
                "assemble: 5.2 starts at its heading", failures,
                detail=repr(s52[:80]))
        _assert("Final 5.1 prose" not in s52,
                "assemble: 5.1 tail does NOT leak into 5.2", failures)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print("self-test FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        sys.exit(1)
    print("self-test passed")


def main():
    # Handle --self-test before argparse so the user doesn't need to
    # invent dummy values for --pages / --out just to run the smoke
    # tests. Mirrors detect_structure's --self-test convention but
    # avoids that script's awkwardness of requiring placeholder args.
    if "--self-test" in sys.argv[1:]:
        run_self_test()
        return

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="Run the smoke tests and exit. Does not need "
                         "--pages or --out.")
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
    ap.add_argument("--allow-single-chapter", action="store_true",
                    help="Permit producing a one-chapter book when no "
                         "outline is available and heading detection finds "
                         "nothing. Only use for true single-essay PDFs — "
                         "the default refuses to emit a flat book silently.")
    ap.add_argument("--work",
                    help="Optional work directory. When provided, a "
                         "quality_warnings.json file is written here for "
                         "the orchestrator's output-quality gate.")
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
            print("  no chapters detected", file=sys.stderr)

    # Refuse to silently produce a one-chapter book. Either the caller
    # has an outline, --detect-headings produced ≥3 entries, or they
    # explicitly opted into single-chapter mode for a real single-essay
    # PDF. Otherwise we'd glue every page into one giant `Document`
    # chapter and the orchestrator would mark it complete.
    if len(outline) < 3 and not args.allow_single_chapter:
        print(
            "assemble_chapters: outline has "
            f"{len(outline)} chapter(s) and --detect-headings produced "
            "no usable structure. Refusing to write a single-chapter "
            "book. Re-run with --allow-single-chapter to override, or "
            "fix the outline (rerun extract_outline.py / "
            "detect_structure.py).",
            file=sys.stderr,
        )
        sys.exit(2)

    if not outline:
        print("WARNING: no outline; producing single-chapter book "
              "(--allow-single-chapter set).",
              file=sys.stderr)

    if outline:
        outline, dropped = dedupe_outline(outline)
        if dropped:
            print(f"Deduped outline: dropped {len(dropped)} near-duplicate "
                  f"item(s). Survivors: {len(outline)}",
                  file=sys.stderr)
            for d in dropped[:5]:
                print(f"  dropped: {d.get('slug')!r} (title={d.get('title')!r})",
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

    # Quality warnings: chapters that are predominantly OCR fallback
    # markers with very little real text. The orchestrator reads this
    # before flipping status: complete.
    quality_warnings: list[dict] = []
    for w in written:
        chapter_path = out_dir / w["file"]
        if not chapter_path.exists():
            continue
        text = chapter_path.read_text()
        fallback_count = text.count("<!-- ocr-fallback -->")
        if fallback_count == 0:
            continue
        # Words of real text — strip the fallback markers and any
        # heading line, then count whitespace-separated tokens.
        stripped = text.replace("<!-- ocr-fallback -->", "")
        readable_words = sum(1 for tok in stripped.split() if tok.strip())
        if readable_words < 200 * fallback_count:
            quality_warnings.append({
                "chapter": Path(w["file"]).stem,
                "file": w["file"],
                "issue": "predominantly OCR fallback",
                "fallback_count": fallback_count,
                "readable_words": readable_words,
            })

    if args.work:
        work_dir = Path(args.work)
        work_dir.mkdir(parents=True, exist_ok=True)
        warn_path = work_dir / "quality_warnings.json"
        warn_path.write_text(json.dumps(
            {"warnings": quality_warnings}, indent=2))
        if quality_warnings:
            print(f"Wrote {warn_path} with {len(quality_warnings)} warning(s)",
                  file=sys.stderr)

    summary_path = out_dir / "SUMMARY.md"
    write_summary(written, summary_path, args.title)

    # Sanity-check: every .md in chapters dir (except SUMMARY.md) must
    # be referenced in `written`. An orphan means dedupe disagreed with
    # the per-chapter writer or a previous run left stale files.
    written_files = {w["file"] for w in written}
    on_disk = {p.name for p in out_dir.glob("*.md") if p.name != "SUMMARY.md"}
    orphans = on_disk - written_files
    if orphans:
        print(f"\nERROR: {len(orphans)} orphan .md file(s) in {out_dir} "
              f"not referenced in SUMMARY.md: {sorted(orphans)[:5]}"
              f"{' ...' if len(orphans) > 5 else ''}",
              file=sys.stderr)
        print("  This usually means a previous run wrote different slugs. "
              "Delete the chapters directory and rerun.",
              file=sys.stderr)
        sys.exit(3)

    print(f"\nWrote {len(written)} chapter file(s) to {out_dir}")
    print(f"Draft SUMMARY: {summary_path}")
    print("Spot-check a chapter or two before running init_mdbook.py.")


if __name__ == "__main__":
    main()
