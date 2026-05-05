---
name: pdf-to-mdbook
description: "Use this skill whenever the user wants to convert a PDF into an mdBook, a static HTML book, a browsable web version of a PDF, or anything described as 'turn this PDF into a book/site/wiki/Markdown collection'. Handles PDFs of any size, including scanned PDFs that need OCR, books with bookmarks, and books without. The skill is context-friendly: it never loads whole-document text into the conversation — bundled scripts read the PDF and write Markdown directly to disk. Use this for textbooks, manuals, reports, public-domain books, papers, or any long-form PDF the user wants to read or publish in mdBook form. Do NOT use this for one-off PDF reading tasks (use pdf-reading) or for creating a brand-new book from scratch with no source PDF."
---

# PDF → mdBook

Convert a PDF — text-based or scanned, small or thousands of pages — into a buildable mdBook source tree (`book.toml` + `src/SUMMARY.md` + chapter Markdown), then build it.

## Why this skill is structured the way it is

A naive approach reads the PDF page-by-page into context, asks Claude to write Markdown for each page, then assembles. For a 400-page book that's hundreds of thousands of tokens before any cleanup work happens — and most of those tokens are spent transcribing text that tools can extract deterministically.

This skill keeps Claude **supervisory for bulk work, decisive for structure**:

1. **Triage runs once on disk** and reports a few JSON facts (page count, scanned vs. text, has bookmarks).
2. **Bulk extraction is a script** — text or OCR — that writes per-page Markdown to disk. Claude never reads those pages in.
3. **Structure detection is deliberately heavy.** Bookmarks first; failing that, `detect_structure.py` runs TOC parsing, page-offset estimation, cross-validation, and font analysis as parallel signals. When confidence is low it produces rasterized TOC images and routes the decision to Claude's vision. Structure shows up in every URL, sidebar entry, and search result, so we spend tokens here rather than save them.
4. **Assembly is a script** that groups pages into chapters from the outline.
5. **Claude's job is to spot-check and fix** — verify SUMMARY.md, look at one or two chapter files, fix specific problems, then build.

If the agent finds itself about to read pages of extracted text "to understand the book," that's the wrong mode — re-read this section.

## Workflow at a glance

```
PDF
 │
 ▼
[1] triage.py            ─ ~30 lines of JSON. Decide pipeline.
 │
 ▼
[2a] extract_outline.py  ─ Bookmarks → outline.json (preferred)
     │
     │   if has_outline: false
     ▼
[2b] detect_structure.py ─ Multi-signal detection: TOC parse + offset
                           detection + cross-validation + font analysis.
                           Writes outline.json + outline_review.json
                           + rasterized TOC images for vision review.
 │
 ▼
[3a] extract_text_pages.py    OR    [3b] ocr_pages.py
     (text PDFs)                         (scanned / mixed)
 │                                        │
 ├────────────────┬───────────────────────┘
                  ▼
[4] assemble_chapters.py ─ Group pages by outline → chapters/*.md + draft SUMMARY.md
 │
 ▼
[5] init_mdbook.py       ─ book.toml + src/ scaffold
 │
 ▼
[6] mdbook build         ─ Serve locally via mdbook serve
```

All intermediates live under a working directory (default `./pdf-to-mdbook-work/`). Final mdBook is under `./<slug>-book/`.

## Step 1 — Triage (always do this first)

```bash
python scripts/triage.py path/to/input.pdf
```

Output is JSON like:

```json
{
  "pages": 412,
  "size_mb": 18.4,
  "has_bookmarks": true,
  "bookmark_count": 24,
  "sample_text_density": [12, 1843, 1992, 2104, 1876, 1991, 14],
  "scanned_estimate": "text",
  "recommended_pipeline": "text",
  "warnings": ["pages 1 and 412 look like covers (very low text)"]
}
```

Read it and decide:

- `recommended_pipeline: "text"` → step 3a only.
- `recommended_pipeline: "ocr"` → step 3b only.
- `recommended_pipeline: "hybrid"` → step 3a, then run 3b only on the page ranges flagged as low-text in the manifest. See **reference/ocr.md** for the hybrid pattern.
- `has_bookmarks: false` → after step 2, see **reference/structure.md**.

Do NOT skip triage. The cost is one tool call and ~30 lines of context, and it determines everything downstream.

## Step 2 — Determine the chapter structure

Structure is the spine of the book — it's referenced by every link,
URL, sidebar entry, and search result. This step gets careful attention.

### 2a. Try bookmarks first (cheap, authoritative when present)

```bash
python scripts/extract_outline.py path/to/input.pdf --out work/outline.json
```

If the PDF has bookmarks, this is the authoritative chapter structure
— use it as-is. The output looks like:

```json
{
  "has_outline": true,
  "items": [
    {"title": "Preface",   "level": 1, "page": 1,  "slug": "preface"},
    {"title": "Chapter 1", "level": 1, "page": 9,  "slug": "chapter-1"},
    {"title": "1.1 Setup", "level": 2, "page": 11, "slug": "1-1-setup"}
  ]
}
```

Skip to step 3.

### 2b. No bookmarks → run intelligent multi-signal detection

```bash
python scripts/detect_structure.py path/to/input.pdf --out work/
```

This script combines several signals:

1. **Printed TOC detection** — scans the first 30 pages for layout
   patterns that look like a table of contents (lines ending in page
   numbers, dot leaders, hierarchical indent).
2. **TOC parsing** — extracts entries with title, level, and *printed*
   page number.
3. **Page-offset estimation** — searches the body for the first
   several chapter titles to compute the offset between printed and
   PDF page numbers (excluding the TOC page itself, so the search
   doesn't match titles on the TOC).
4. **Cross-validation** — confirms each chapter title actually
   appears on its predicted PDF page.
5. **Font-size analysis** — fallback when no TOC exists; finds
   heading-sized text across the document.
6. **Rasterized TOC images** — written to `work/toc-images/` so you
   can verify with vision when confidence is low.

It writes `work/outline.json` (compatible with `assemble_chapters.py`)
plus `work/outline_review.json`:

```json
{
  "method": "toc-parse",
  "confidence": "high",
  "summary": "Detected 11 entries from printed TOC. Page offset +8 (confirmed by 4 probe matches). Chapter-level issues: 0/5. Section-level issues: 6 (often expected — sections may render differently in body).",
  "page_offset": 8,
  "page_offset_match_count": 4,
  "issues": [...],
  "needs_review": false,
  "toc_pages_pdf": [3],
  "rasterized_toc_pages": ["work/toc-images/toc_p003-03.png"]
}
```

**Read `outline_review.json` first** (small file, always). Then:

- **`confidence: high` and `needs_review: false`** → outline.json is
  trustworthy. Proceed to step 3.
- **`confidence: medium`** → spot-check by viewing one rasterized TOC
  image (`work/toc-images/`) and a couple of `outline.json` entries
  to confirm titles and pages look right.
- **`confidence: low` or `needs_review: true`** → view ALL the
  rasterized TOC images and edit `outline.json` directly. The script
  has done the heavy lifting (text extraction, pattern matching);
  your job is to verify against the visual TOC and correct anything
  it got wrong. This is exactly the kind of decision that the agent
  is better at than a script.

### 2c. No TOC and font-analysis is unreliable → vision-first

If `outline_review.json` reports `method: "none"` or `method:
"font-analysis"` with low confidence, fall back to vision:

1. Rasterize the first ~25 pages of the PDF: `pdftoppm -jpeg -r 120
   -f 1 -l 25 input.pdf /tmp/scan` (the script also does this for
   detected TOC pages — re-use them if they exist).
2. View the resulting images and look for a printed TOC manually.
3. Hand-write `work/outline.json` based on what you see; see
   **reference/structure.md** for the schema and tips on mapping
   printed page numbers to PDF page numbers.

### Always confirm with the user

If the structure was generated by anything other than bookmarks, show
the user the chapter list (titles + PDF page numbers) before running
step 4. Re-running steps 4+ after correcting an outline is cheap;
re-OCRing 600 pages because chapters were wrong is not.

## Step 3a — Extract text (text-based PDFs)

```bash
python scripts/extract_text_pages.py path/to/input.pdf \
    --out work/pages \
    --layout
```

Writes `work/pages/page_0001.md`, `page_0002.md`, … and `work/pages/manifest.json` with per-page character counts and a `needs_ocr` flag for any page below the threshold (default 100 chars).

Don't read the page files yourself. Read **manifest.json** to confirm extraction worked, then proceed. If `needs_ocr` flags some pages in an otherwise text-PDF, run step 3b on just those pages — the hybrid pattern.

## Step 3b — OCR (scanned PDFs or scanned pages)

```bash
# Whole document
python scripts/ocr_pages.py path/to/input.pdf \
    --out work/pages \
    --dpi 300 \
    --lang eng

# Specific page range (hybrid mode after 3a)
python scripts/ocr_pages.py path/to/input.pdf \
    --out work/pages \
    --pages 47-52,89,142-145
```

OCR is slow (~1–3 sec/page on Tesseract). The script streams progress and is resumable — if interrupted, re-run with the same args and it skips pages whose `.md` is already written. For long jobs, run it in the background and check on it.

**Sample first.** Before running on the whole book, run on 2–3 sample pages and view the output. If quality is poor, see **reference/ocr.md** for: better DPI, multi-language packs, deskewing with `unpaper`, or escalating to vision OCR for selected pages.

## Step 4 — Assemble chapters

```bash
python scripts/assemble_chapters.py \
    --pages work/pages \
    --outline work/outline.json \
    --out work/chapters
```

For each outline item, the script concatenates the page-files spanning that chapter, runs cleanup (de-hyphenation, header/footer stripping, blank-line collapse, heading normalization), and writes `work/chapters/<slug>.md`. It also writes a **draft `SUMMARY.md`** with the correct mdBook hierarchy.

After it runs, **spot-check**: open one or two chapter files and the SUMMARY.md. Fix obvious cleanup issues if needed (see **reference/markdown.md** for common artifacts and how to handle them). Don't read every chapter — that defeats the point.

## Step 5 — Initialize the mdBook

```bash
python scripts/init_mdbook.py \
    --title "Book Title" \
    --author "Author Name" \
    --chapters work/chapters \
    --summary work/chapters/SUMMARY.md \
    --out ./book-output
```

This writes `book.toml`, copies chapter Markdown into `src/`, places `SUMMARY.md` in `src/`, and configures sensible defaults (search on, MathJax on, copy code button on). See **reference/mdbook.md** for what gets configured and how to adjust it.

## Step 6 — Build

```bash
cd ./book-output && mdbook build
# or for live preview:
mdbook serve --open
```

If the build fails, the most common causes are:
- A SUMMARY.md link points to a chapter file that wasn't written → check chapter slugs match.
- A chapter has a stray ` ``` ` that wasn't closed → `assemble_chapters.py` already handles common cases but not all.
- A chapter has a malformed heading that mdBook rejects.

`scripts/build.sh ./book-output` wraps `mdbook build` and surfaces these errors with line-pointers.

## Working directory layout

```
./
├── input.pdf
├── pdf-to-mdbook-work/           ← intermediates; safe to delete
│   ├── triage.json
│   ├── outline.json
│   ├── pages/
│   │   ├── manifest.json
│   │   ├── page_0001.md
│   │   ├── page_0002.md
│   │   └── ...
│   └── chapters/
│       ├── SUMMARY.md            ← draft
│       ├── preface.md
│       ├── chapter-1.md
│       └── ...
└── <slug>-book/                  ← final mdBook
    ├── book.toml
    ├── src/
    │   ├── SUMMARY.md
    │   ├── preface.md
    │   └── ...
    └── book/                     ← built HTML (after `mdbook build`)
```

## Reference files

Read these only when their topic comes up in the workflow. None are needed for the happy path on a clean text PDF with bookmarks.

- **reference/structure.md** — Chapter detection when bookmarks are missing: TOC-page rasterization, heuristic detection, splitting strategies.
- **reference/ocr.md** — When and how to OCR: DPI choice, language packs, hybrid extraction, vision-OCR escalation, sanity-checking output without reading every page.
- **reference/markdown.md** — Cleaning extracted text into proper Markdown: de-hyphenation, repeated header/footer stripping, table extraction (and when to give up and use an image), figures, equations, footnotes.
- **reference/mdbook.md** — `book.toml` and `SUMMARY.md` formats, MathJax, search, custom themes, common build errors.

## Things to remember

- **Confirm the outline before extracting.** If you had to generate it heuristically, show the user the chapter list and pause for confirmation. Re-running step 4+ after the outline changes is cheap; re-OCRing a 600-page book because chapters were wrong is not.
- **Don't read extracted page files.** The manifest tells you everything you need to know about extraction quality. Open a page file only to diagnose a specific reported problem.
- **For long OCR jobs, run them in the background** and continue conversation. The OCR script is resumable and writes progress to `work/pages/manifest.json` as it goes.
- **Keep the work directory.** It's the difference between "fix one chapter" and "re-do the whole book."
- **Cleanup is iterative.** A first build will reveal the rough edges (a stray equation, a table that didn't survive, a chapter that got mis-split). Fix in the chapter file, rebuild, repeat. You don't need to perfect chapters before the first `mdbook build`.
