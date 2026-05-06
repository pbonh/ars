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
[2a] extract_outline.py  ─ Bookmarks → outline.json (preferred).
 │                          Sets has_outline: true|false in outline.json.
 │
 ▼
[3a] extract_text_pages.py    OR    [3b] ocr_pages.py
     (text PDFs)                         (scanned / mixed)
 │
 │  ── if (2a) wrote has_outline: true, skip (2b) ──
 │  ── else: ──────────────────────────────────────┐
 │                                                 ▼
 │           [2b] detect_structure.py --pages-dir <work>/pages
 │                ─ Multi-signal detection: TOC parse + offset
 │                  detection + cross-validation + font analysis,
 │                  plus a body-heading scan for books without
 │                  a printed TOC. Reads page text from the .md
 │                  files in --pages-dir, so it works on scanned
 │                  PDFs whose text layer is empty.
 │                  Exits non-zero (with rasterized first-25-page
 │                  images) when no signal yields ≥3 usable
 │                  entries, forcing vision review instead of
 │                  silently producing a 1-chapter book.
 │                                                 │
 │ ◄───────────────────────────────────────────────┘
 ▼
[3.5] extract_figures.py ─ Embedded raster + vector figures (optional but recommended)
 │
 ▼
[4] assemble_chapters.py ─ Group pages by outline → chapters/*.md + draft SUMMARY.md
 │                          + quality_warnings.json (when --work given)
 │
 ▼
[5] init_mdbook.py       ─ book.toml + src/ scaffold + outline.json carry-through
 │
 ▼
[6] mdbook build         ─ Serve locally via mdbook serve
```

**Why structure detection runs after page extraction now**: scanned PDFs
have no text layer, so `pdftotext` returns empty pages. `detect_structure.py`
needs page text to find the printed TOC; the OCR'd `.md` files produced by
`ocr_pages.py` are exactly that text. Running detection second (with
`--pages-dir`) lets the same code path handle text-PDFs and scanned PDFs
uniformly. If bookmarks already gave a usable outline (Step 2a), Step 2b
is skipped entirely.

All intermediates live under a working directory and the final mdBook lives in a sibling output directory. **Place both alongside the source PDF**, not in the current working directory:

```bash
PDF=/path/to/some/dir/MyBook.pdf
PDF_DIR=$(dirname "$PDF")
SLUG=my-book
WORK="$PDF_DIR/.pdf-to-mdbook-work-$SLUG"   # leading dot keeps it tidy
OUT="$PDF_DIR/$SLUG-book"
```

This way the mdBook ends up next to the PDF (so the user finds it where they expect) and re-running on a different PDF in a different directory doesn't collide with prior work. Use these variables for every script's `--out` / `--pages` / `--outline` arguments below.

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

**Order matters.** Try bookmarks (Step 2a) first. If they're usable, you
have your outline and you can skip ahead to Step 3 / Step 4. If bookmarks
fail or the PDF has none, **run page extraction (Step 3) before TOC
detection (Step 2b)** — Step 2b reads page text from the extracted `.md`
files via `--pages-dir`, which is the only way to find a printed TOC on a
scanned PDF.

### 2a. Try bookmarks first (cheap, authoritative when present)

```bash
python scripts/extract_outline.py path/to/input.pdf --out work/outline.json
```

If the PDF has *useful* bookmarks, this is the authoritative chapter
structure — use it as-is. The script also rejects auto-generated
"garbage" outlines (titles that look like filenames such as `01.pdf`
or `appG.pdf`, common in concatenated/scanned PDFs); when that
happens you'll see a message saying it fell back, and you should run
`detect_structure.py` next as in 2b. The output for a real outline
looks like:

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

### 2b. No bookmarks → run page extraction (Step 3) first, then multi-signal detection

```bash
# Run Step 3 (extract_text_pages.py or ocr_pages.py) first, then:
python scripts/detect_structure.py path/to/input.pdf \
    --out work/ \
    --pages-dir work/pages
```

The `--pages-dir` flag is **required** for scanned PDFs (where
`pdftotext` would return empty) and recommended for text PDFs too (it's
faster than re-running `pdftotext` per page). If you forget it on a
scanned PDF the script bails immediately with:

```
detect_structure: this PDF appears to be scanned (no extractable text on first 3 pages).
Run ocr_pages.py first, then re-invoke with --pages-dir <work>/pages.
```

This script combines several signals:

1. **Printed TOC detection** — scans the first 30 pages for layout
   patterns that look like a table of contents (lines ending in page
   numbers, dot leaders, hierarchical indent, or OCR'd
   slash/comma separators).
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
6. **Body-heading scan** — third-tier fallback for books with no
   printed TOC and a flat font hierarchy (e.g. web-rendered PDFs like
   the rust-book). Scans the first ~10 lines of every page for
   structural headings (`Chapter N`, `Part N`, `Appendix X`) and
   common stand-alone titles (`Foreword`, `Preface`, `Introduction`,
   `Conclusion`, `Index`, …). Only runs when `--pages-dir` was given.
7. **Rasterized TOC images** — written to `work/toc-images/` so you
   can verify with vision when confidence is low.

**Hard failure when nothing works.** If no signal yields ≥3 plausible
chapter entries the script writes `outline.json` with `has_outline:
false`, rasterizes the first ~25 pages into `work/toc-images/`, and
exits non-zero. The caller must then take the vision-review path
described in Step 2c — the script will not silently produce a
single-chapter book.

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

When `detect_structure.py` exits non-zero (or `outline_review.json`
reports `method: "none"` and `outline.json` has `has_outline: false`),
the only path forward is vision:

1. The script has already rasterized the first ~25 pages into
   `work/toc-images/` for you — view them directly. If you want
   higher-resolution renders, re-run `pdftoppm -jpeg -r 120 -f 1 -l 25
   input.pdf /tmp/scan`.
2. View the resulting images and look for a printed TOC manually.
3. Hand-write `work/outline.json` based on what you see; see
   **reference/structure.md** for the schema and tips on mapping
   printed page numbers to PDF page numbers.

This path also catches `method: "body-headings"` or `method:
"font-analysis"` results with low confidence — `outline.json` is
populated in those cases (so the script exits 0), but the entries are
flagged for review and you should still spot-check the rasterized images
before proceeding to assembly.

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

## Step 3.5 — Extract figures (optional but recommended)

```bash
python scripts/extract_figures.py path/to/input.pdf \
    --out work/pages/images
```

Combines `pdfimages -all` (poppler) for embedded raster art with PyMuPDF
for vector figures. Outputs `figure_pNNNN_M.{png,jpg,...}` plus
`work/pages/figures_manifest.json`. `assemble_chapters.py` looks for
this manifest and inserts `![](images/figure_pNNNN_M.ext)` after each
matched `Figure N.M` caption in chapter text; unmatched figures from
the chapter's page range are appended at the end of the chapter.

Skip this step only when you've confirmed the PDF has no figures of
interest (a pure-prose book). Skipping is non-destructive — chapters
will simply lack image references, matching the previous behavior.

## Step 4 — Assemble chapters

```bash
python scripts/assemble_chapters.py \
    --pages work/pages \
    --outline work/outline.json \
    --out work/chapters \
    --work work
```

For each outline item, the script concatenates the page-files spanning that chapter, runs cleanup (Unicode-aware de-hyphenation, fingerprint-based header/footer stripping, blank-line collapse, ligature normalization, figure insertion), and writes `work/chapters/<slug>.md`. It also writes a **draft `SUMMARY.md`** with the correct mdBook hierarchy (section-number prefixes like `5.3` are honored even when bookmark levels disagree).

`--work` is optional but enables `quality_warnings.json` (chapters that are predominantly OCR fallback markers), which `init_mdbook.py` carries into the final book root for the orchestrator's quality gate.

The script **refuses to silently produce a single-chapter book**. If `outline.json` has fewer than 3 entries and `--detect-headings` finds nothing, it exits with code 2 and asks you to fix the outline. Pass `--allow-single-chapter` only when you're sure the source is a real single-essay PDF.

After it runs, **spot-check**: open one or two chapter files and the SUMMARY.md. Fix obvious cleanup issues if needed (see **reference/markdown.md** for common artifacts and how to handle them). Don't read every chapter — that defeats the point.

## Step 5 — Initialize the mdBook

```bash
python scripts/init_mdbook.py \
    --title "Book Title" \
    --author "Author Name" \
    --chapters work/chapters \
    --summary work/chapters/SUMMARY.md \
    --pdf path/to/input.pdf \
    --slug my-book \
    --work work
```

When you pass `--pdf` and `--slug`, `--out` is auto-derived as `<dirname(--pdf)>/<slug>-book/`. You can pass `--out` explicitly instead — but the script **refuses** to write into a directory that contains PDFs, since that mixes source and output.

`--work` carries the artifact files (`outline.json`, `outline_review.json`, `quality_warnings.json`, `figures_manifest.json`) into the book root next to `book.toml`, so post-hoc inspection is possible without rerunning the pipeline.

The script writes `book.toml`, copies chapter Markdown into `src/`, places `SUMMARY.md` in `src/`, and configures sensible defaults (search on, MathJax on, copy code button on). See **reference/mdbook.md** for what gets configured and how to adjust it.

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

### Verification (run this before declaring the book complete)

After `mdbook build` succeeds, spot-check the book against the same
output-quality gates the orchestrator uses:

- No `‐ ` (U+2010 + space) anywhere in `src/*.md` — dehyphenation
  should have caught Unicode hyphens.
- No `ﬀ ﬁ ﬂ ﬃ ﬄ ﬅ ﬆ` ligatures in `src/SUMMARY.md` — title
  sanitization handles these.
- No `(cid:` substrings in any `src/*.md` — those signal font-mapping
  failures; rerun `extract_text_pages.py` to trigger PyMuPDF fallback,
  or fall back to `ocr_pages.py` for affected pages.
- No `\r` or trailing whitespace in chapter `# Title` headings.
- Median word length per chapter file ≤ 8 (eyeball or use
  `awk '{for(i=1;i<=NF;i++) print length($i)}' file.md | sort -n | …`).
  Higher signals space-collapse — re-extract those pages.
- `outline.json` exists at the book's root (carried over by
  `init_mdbook.py --work`).
- For books with bookmarked outlines, SUMMARY hierarchy matches
  section-number prefixes (e.g., `5.3` nests under `5`).
- `ls src/*.md | wc -l` equals the SUMMARY entry count exactly — no
  orphan files. `assemble_chapters.py` enforces this and exits 3 on
  mismatch, but rerun it after any manual edits.
- For figure-heavy books: `src/images/` exists with at least some
  `figure_*.png`; chapters reference them.
- `quality_warnings.json` (in the book root) is empty or absent.
  Non-empty means the orchestrator should mark `status: needs_review`
  rather than `complete`.

### Smoke test

Before shipping a change to the cleanup pipeline (especially anything
in `assemble_chapters.py`), run:

```bash
python scripts/assemble_chapters.py --self-test
python scripts/detect_structure.py /dev/null --out /tmp/_ds --self-test
```

`assemble_chapters.py --self-test` runs in-process unit checks plus
one end-to-end `assemble()` against a synthetic 3-chapter book whose
section 5.1 starts mid-page on page 105 and section 5.2 starts mid-
page on page 108 — the exact shape that produced the
`5-1-terms-detecting-logic-for-a-determinant.md` defect. It exits
non-zero (with specific assertion labels) on regression. Cheap
enough to wire into CI or a pre-commit hook.

## Working directory layout

Both the work tree and the final mdBook live alongside the source PDF (not in the agent's CWD):

```
<dir-containing-pdf>/
├── input.pdf
├── .pdf-to-mdbook-work-<slug>/   ← intermediates; safe to delete
│   ├── triage.json
│   ├── outline.json
│   ├── outline_review.json       ← only when detect_structure ran
│   ├── pages/
│   │   ├── manifest.json
│   │   ├── figures_manifest.json ← only when extract_figures.py ran
│   │   ├── page_0001.md
│   │   ├── page_0002.md
│   │   ├── images/               ← extracted figures + OCR fallback PNGs
│   │   └── ...
│   └── chapters/
│       ├── SUMMARY.md            ← draft
│       ├── preface.md
│       ├── chapter-1.md
│       ├── images/               ← carried through from pages/
│       └── ...
└── <slug>-book/                  ← final mdBook
    ├── book.toml
    ├── outline.json              ← carried over by init_mdbook --work
    ├── outline_review.json       ← when detect_structure ran
    ├── quality_warnings.json     ← when assemble_chapters --work was used
    ├── figures_manifest.json     ← when extract_figures.py ran
    ├── src/
    │   ├── SUMMARY.md
    │   ├── preface.md
    │   ├── images/               ← carried through; referenced by chapter MDs
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

- **Confirm the outline before assembling.** If you had to generate it heuristically (anything other than bookmarks), show the user the chapter list and pause for confirmation. Re-running step 4+ after the outline changes is cheap; re-running structure detection after assembly produced the wrong cuts is not.
- **For scanned PDFs (or any PDF without bookmarks), extract pages BEFORE running `detect_structure.py`** and pass `--pages-dir <work>/pages`. The script enforces this with a clear error if you forget.
- **Don't read extracted page files.** The manifest tells you everything you need to know about extraction quality. Open a page file only to diagnose a specific reported problem.
- **For long OCR jobs, run them in the background** and continue conversation. The OCR script is resumable and writes progress to `work/pages/manifest.json` as it goes.
- **Keep the work directory.** It's the difference between "fix one chapter" and "re-do the whole book."
- **Cleanup is iterative.** A first build will reveal the rough edges (a stray equation, a table that didn't survive, a chapter that got mis-split). Fix in the chapter file, rebuild, repeat. You don't need to perfect chapters before the first `mdbook build`.
