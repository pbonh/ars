# Detecting chapter structure

Structure is the spine of an mdBook. The chapter list shows up in
the sidebar, in URLs, in search results, in cross-references — every
reader hits it constantly. Getting it wrong cascades through the
whole book, so this is the one place in the pipeline where Claude
intentionally spends tokens rather than save them.

This document covers what the detection scripts do, what the agent
should do when they hit ambiguity, and the edge cases that aren't
fully automated.

## The decision tree

```
Does the PDF have bookmarks/outline?
├── YES → extract_outline.py → done. Bookmarks are authoritative.
└── NO
    │
    └── detect_structure.py (multi-signal)
        ├── Found a printed TOC?
        │   ├── YES → parse it, compute page offset,
        │   │         cross-validate against body
        │   │         ├── high confidence → done.
        │   │         ├── medium → spot-check one TOC image.
        │   │         └── low → view ALL TOC images,
        │   │                   edit outline.json by hand.
        │   └── NO  → font-size analysis fallback
        │            ├── reliable headings? → propose; agent confirms.
        │            └── nothing usable → vision-first fallback.
        └── Vision-first fallback
            ├── Rasterize first ~25 pages.
            ├── Agent views them, finds the TOC manually.
            └── Hand-write outline.json.
```

## Inside `detect_structure.py`

The script combines **five signals** and writes `outline.json` plus
`outline_review.json` (a small audit trail describing what it did and
why).

### Signal 1: TOC page detection

For each of the first ~30 pages, run `pdftotext -layout` and score
how TOC-shaped it looks:

- A line is "TOC-like" if it ends with a page number (arabic 1-4
  digits OR roman numerals) AND has either a long dot-leader run or
  a multi-space gap before the number.
- A page is a TOC candidate if ≥ 35% of its non-empty lines look
  TOC-like and it has ≥ 8 lines total (avoids triggering on short
  reference pages with one or two numeric entries).

Then the script picks the longest contiguous run of candidate pages.
Multi-page TOCs are common in long books; the run is treated as one
unit.

### Signal 2: TOC parsing

Each line on a TOC page is parsed as `(indent, title, page_number)`
using two regex patterns: dot-leader format (`Title ... 23`) and
no-dots multi-space format (`Title    23`). Trailing dots/spaces
after the page number are tolerated (real-world dot leaders sometimes
overflow past the number). Page numbers are accepted as either arabic
or roman numerals.

Indents are clustered into integer levels (1-4) using the distinct
indent values in the page's leftmost text positions. Two-space indent
becomes level 2, four-space becomes level 3, etc. — but the actual
mapping is whatever the document uses.

### Signal 3: Page-offset estimation

The TOC entries' page numbers are *printed* page numbers (what's at
the bottom of each chapter page). Those don't match PDF page numbers
because of front matter (title page, copyright, the TOC itself,
maybe a foreword). The offset is constant across the body of a
typical book.

The script picks up to 8 level-1 entries spread through the document
and searches the body text for each title. The search:

- **Excludes the TOC pages themselves** so a chapter title like
  "Chapter 1: Beginnings" doesn't match against its own TOC entry,
  giving a bogus offset.
- **Biases forward** from the printed page (front matter typically
  produces a positive offset).
- **Caps effort** at 80 pages per probe.

The offset that matches the most probes wins. The probe match count
goes into `outline_review.json` as a confidence signal.

### Signal 4: Cross-validation

For each TOC entry, check that the title actually appears on or near
its predicted PDF page. "Near" means within ±2 pages. Excludes TOC
pages from the check.

Two kinds of issues are reported:

- `title-not-found-near-predicted-page` — could indicate a wrong
  offset, a section title that renders differently in body than in
  the TOC, or an OCR'd PDF where text doesn't match exactly.
- `found-on-neighbor` — title appeared one page off; usually
  harmless (the actual chapter often spans a page break, or the page
  count includes a chapter-title spread).

Issues are weighted by level when computing confidence: chapter-level
mismatches are critical, sub-section mismatches are common and
expected (a section heading like "1.1 Setup" often appears as just
"Setup" in body text, or doesn't visually mark a page boundary).

### Signal 5: Font-size analysis

Always run, regardless of TOC presence. Uses pdfplumber to:

1. Sample pages (every Nth page, up to 60) for a font-size
   distribution. The most common size is the body text size.
2. On every page, find lines with average font ≥ 1.25× body. These
   are heading candidates.
3. Cluster heading sizes into level 1 / level 2 / etc.

When TOC parsing succeeds, font analysis is a sanity check. When TOC
parsing fails, font analysis is the primary signal — but its
false-positive rate is higher. Pull-quotes, emphasized lines, drop
caps, and figure captions can all be larger than body text.

## Reading `outline_review.json`

```json
{
  "method": "toc-parse",
  "confidence": "high",
  "summary": "Detected 11 entries from printed TOC. Page offset +8 (confirmed by 4 probe matches). Chapter-level issues: 0/5. Section-level issues: 6 (often expected — sections may render differently in body).",
  "page_offset": 8,
  "page_offset_match_count": 4,
  "issues": [
    {"title": "1.1 The Setup", "issue": "title-not-found-near-predicted-page", "predicted_pdf_page": 11}
  ],
  "needs_review": false,
  "toc_pages_pdf": [3],
  "rasterized_toc_pages": ["work/toc-images/toc_p003-03.png"],
  "font_body_size": 11.0,
  "items_count": 11
}
```

Fields the agent acts on:

- **`confidence`**: `high`, `medium`, `low`, or `none`. Combines
  probe-match count, chapter-level cross-validation, and method.
- **`needs_review`**: when `true`, view the rasterized TOC images
  before continuing.
- **`method`**: `toc-parse` (TOC found and parsed cleanly),
  `toc-parse-no-offset` (TOC parsed but offset couldn't be confirmed
  — page numbers in `outline.json` are PRINTED, not PDF, and need
  manual correction), `font-analysis` (fallback), or `none`.
- **`issues`**: list of cross-validation problems. If
  `confidence: high` you can ignore this list; if `low` or `medium`,
  scan it for chapter-level entries (sub-section issues are usually
  noise).

The agent's decision tree on review output:

```
confidence: high && needs_review: false
  → Trust outline.json, proceed to assemble_chapters.py.

confidence: medium
  → View one rasterized TOC image (cheap), spot-check 2-3
    outline.json entries against it, then proceed.

confidence: low
  → View all rasterized TOC images.
  → Edit outline.json directly to fix titles, levels, or pages.
  → If method is "toc-parse-no-offset", you must add the offset to
    each arabic page number manually after determining it from the
    TOC images plus the body.

confidence: none / method: none
  → Fall back to vision-first.
```

## Vision-first fallback (when no TOC exists)

Some PDFs genuinely have no TOC: short reports, modern blog-style
PDFs, scanned materials where the TOC was lost. After
`detect_structure.py` reports `method: none` or `font-analysis` with
low confidence:

```bash
# Rasterize the first 25 pages so you can see what's there
pdftoppm -jpeg -r 120 -f 1 -l 25 input.pdf /tmp/scan
ls /tmp/scan-*.jpg
```

View those images. Look for:

- A printed TOC the script missed (it happens with unusual
  layouts).
- Chapter title pages with distinctive typography.
- Numbered or named sections.

Hand-write `outline.json` based on what you see:

```json
{
  "has_outline": true,
  "items": [
    {"title": "Foreword",      "level": 1, "page": 5,   "slug": "foreword"},
    {"title": "Introduction",  "level": 1, "page": 11,  "slug": "introduction"},
    {"title": "1. Beginnings", "level": 1, "page": 19,  "slug": "01-beginnings"},
    {"title": "1.1 The Before","level": 2, "page": 21,  "slug": "01-1-the-before"},
    {"title": "Index",         "level": 1, "page": 387, "slug": "index"}
  ],
  "source": "manual",
  "page_offset": 0
}
```

`page` here is always a PDF page number (1-indexed). To map a
printed TOC's page numbers to PDF pages, find the first chapter in
the body (rasterize a few candidate pages near the front), determine
its PDF page, compute `offset = pdf_page - printed_page`, and apply
to all subsequent entries.

## Edge cases the script doesn't fully handle

**Multiple TOCs.** Some books have a main TOC, a list of figures,
and a list of tables. The script picks one (the longest run).
Usually that's the main TOC, but verify when the rasterized image
isn't what you expected.

**TOC spanning non-contiguous pages.** Rare but possible (e.g., main
TOC on pages 5-7, then a continuation on page 22). The script will
only catch the longest run; the rest is on you.

**Page numbers in non-Arabic non-Roman scripts.** The pattern matchers
only handle ASCII digits and basic Roman numerals. Documents using
Arabic-Indic, Devanagari, or East Asian numerals need manual entry.

**Books where chapters share a page.** Anthologies and collections
of short pieces often have multiple "chapters" starting on the same
PDF page. The current outline schema assumes one start page per
entry. Handle by giving each its own page number anyway and editing
the assembled chapters manually.

**Chapter title differs in TOC vs. body.** If the TOC says "Chapter
1: The Beginning" but the body page heading says just "The
Beginning", cross-validation reports it as not-found. The structure
is still correct; the title in `outline.json` will be the TOC
version, which is usually what readers want anyway.

## Slugs

`detect_structure.py` and `assemble_chapters.py` accept slugs you
provide; otherwise they generate one from `title` (lowercase,
ASCII-fold, hyphenate non-word characters). If you write
`outline.json` by hand:

- Lowercase, ASCII-only, hyphens (no spaces or underscores).
- Numeric prefix optional but useful for ordering: `01-introduction`,
  `02-foundations`. Otherwise alphabetical order is the tie-breaker
  for files at the same nesting level.
- Match what you'd want in URLs — they become path components under
  `book/`.
- Avoid `index`, `summary`, or anything else that conflicts with
  mdBook's reserved names.

## Splitting strategies for very long chapters

mdBook handles long chapters fine but they're awkward to read. After
assembly, if any chapter is over ~80 KB of Markdown (~30,000 words),
consider splitting at sub-headings:

```bash
ls -la work/chapters/*.md | awk '{print $5, $9}' | sort -n
```

For a too-long chapter, identify natural break points (section
headings) and add `level: 2` entries to `outline.json` pointing at the
right PDF pages, then re-run `assemble_chapters.py`. Cleaner than
splitting assembled Markdown.
