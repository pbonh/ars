---
name: pdf-to-mdbook
description: Convert PDF research papers, textbooks, and documents into fully structured mdBooks. Handles scanned and text-layered PDFs, reconstructs table of contents and indices, converts tables to markdown, extracts images, and processes complex pages with a vision-capable LLM. Use when the user asks to turn a PDF into a book, build an mdBook from a PDF, convert a paper or textbook to markdown, or create a readable web book from a document.
compatibility: Requires poppler (pdfinfo, pdftotext, pdftoppm, pdfimages), qpdf, ocrmypdf, mdbook, and jq. macOS via Homebrew or Linux via devbox/nix.
---

# PDF to mdBook

Convert a single PDF into a complete, buildable mdBook. The skill handles both digitally-born PDFs and scanned books, using vision-based page analysis when layout extraction fails.

**Required references:**
- `references/mdbook-format.md` — mdBook anatomy and `SUMMARY.md` rules.
- `references/page-processing.md` — Vision pass criteria, image extraction, and table conversion rules.

## Inputs

The user provides one of:
- **A single PDF file** — absolute path. Existing path: Steps 1–7 below.
- **A directory of pre-split PDF slices** (from `split-textbooks`) —
  absolute path. New path: Step 0.5 detects this and skips Steps 1–2.

Optional flags:
- `--output-dir <path>` — mdBook root directory.
  - For PDF input, default: `<pdf-dir>/<stem>-mdbook/`.
  - For directory input, default: `<dir>/<dirname>-mdbook/`.
- `--vision <mode>` — `auto` (default), `always`, or `never`. Controls when the vision LLM pass runs.
- `--force` — Overwrite existing output directory.

## Step 0 — Environment self-check

Run:

```bash
command -v pdfinfo pdftotext pdftoppm pdfimages qpdf ocrmypdf mdbook jq
```

If any are missing, print install hints and abort:

- macOS: `brew install poppler qpdf ocrmypdf mdbook jq`
- Linux/devbox: `devbox add poppler qpdf ocrmypdf mdbook jq`

Re-run the relevant Ansible role (`just homebrew` or `just devbox`) afterwards.

## Step 0.5 — Detect input shape (single PDF vs. slice directory)

If the input path is a `.pdf` file, set `slice_mode: false` and proceed to
Step 1 unchanged.

If the input path is a **directory**, set `slice_mode: true` and:

1. **If `<dir>/manifest.json` exists with `schema_version: 2`** (a
   `split-textbooks` manifest), read its `sections` array and use it as the
   canonical section list for this run. Each entry yields:

   ```
   {
     index:           <from manifest>,
     title:           <from manifest>,
     slug:            <from manifest>,
     kind:            <from manifest>,
     start_page:      1,                                       # always 1 (the slice itself)
     end_page:        pdfinfo on <dir>/<filename>.pdf → "Pages"
     slice_filename:  "<filename>.pdf"                          # NEW field for slice mode
   }
   ```

   Skip Steps 1 (canonical resolution) and 2 (outline detection) — the
   slicing already did that work. Set `detection_method: "slice_manifest"`
   and `is_scanned`: copy from the slicing manifest's `is_scanned` field.

   Derive `scan_type` from the slicing manifest's `canonical_pdf` and
   `source_pdf` fields:
   - `is_scanned: false` → `scan_type: "native"`.
   - `is_scanned: true` AND `canonical_pdf != source_pdf` (e.g. `book.ocr.pdf`
     vs `book.pdf`) → `ocrmypdf` was run; the OCR text layer is reliable →
     `scan_type: "no_text"`.
   - `is_scanned: true` AND `canonical_pdf == source_pdf` → no OCR was added;
     the original PDF carries an OCR overlay that may be unreliable →
     `scan_type: "ocr_overlay"`.

   This mapping prevents over-use of the vision pass on `no_text` books
   where the OCR text layer is already trustworthy.

2. **Else if the directory contains slice PDFs** matching
   `^\d{2}-[a-z0-9-]+\.pdf$`, derive the section list from filenames:

   ```
   index           = <NN as int>
   slug            = <slug part>
   title           = title-case of slug with hyphens → spaces
   kind            = applied via the same regex used in Step 2's section-kind
                     classification (case-insensitive match on title)
   start_page      = 1
   end_page        = pdfinfo <slice>.pdf → "Pages"
   slice_filename  = "<NN-slug>.pdf"
   ```

   Set `detection_method: "slice_filenames"`. Run Step 1's scanned-PDF
   detection on the **first** slice as a representative; record `is_scanned`
   and `scan_type` once for the run.

3. **Else** the directory is unrecognized → write `manifest.json` with
   `failed_step: "detect_slices"` and stop.

When `slice_mode: true`, skip Step 1 and Step 2 entirely. Step 3 (scaffold)
proceeds normally; Step 4's per-section extraction loop runs over slices —
read `<dir>/<slice_filename>` instead of `pdftotext -f <start> -l <end>
<canonical>`. Use `pdftotext -layout <dir>/<slice_filename> -` (whole slice
at once) and `pdftoppm -png -r 200 <dir>/<slice_filename> <out>/src/assets/
images/<slug>/page` (every page of the slice). All other extraction logic is
unchanged.

## Step 1 — Resolve canonical PDF (scanned vs. text-layered)

Given input `<path>/book.pdf`:

### 1a — Check for no-text scanned PDF

1. Run `pdffonts <path>/book.pdf | tail -n +3`. Empty output → no embedded fonts.
2. AND `pdftotext -l 5 <path>/book.pdf -` produces empty/whitespace-only output.
3. → No-text scanned PDF. Run:

   ```bash
   ocrmypdf --skip-text --output-type pdf <path>/book.pdf <path>/book.ocr.pdf
   ```

   Canonical PDF = `<path>/book.ocr.pdf`. Record `is_scanned: true`, `scan_type: no_text`.

### 1b — Check for scanned PDF with OCR overlay (CRITICAL — many "text-layered" PDFs are actually this)

Many PDFs appear text-layered (they have embedded fonts and `pdftotext` produces output) but are actually scanned page images with an invisible OCR text overlay. The OCR text layer is often unreliable — it contains word-internal spacing artifacts, garbled characters, jumbled columns, and broken hyphenation. **These PDFs must be detected and flagged for vision processing.**

Run these checks:

```bash
# Count full-page images: one large image per page = scanned book
pdfimages -list -f 1 -l 20 <path>/book.pdf
```

If **every page has exactly one image** and the images are large (width ≥ 1500px or height ≥ 2000px, roughly letter/A4 at 150+ dpi), this is a scanned PDF with OCR overlay.

Also sample the text quality:

```bash
pdftotext -layout -f 1 -l 10 <path>/book.pdf -
```

Check the first 10 pages' extracted text for OCR artifact patterns:
- Word-internal spacing: `\b[a-zA-Z]\s[a-zA-Z]\s[a-zA-Z]` matching common words like `t o`, `i t`, `o f`, `a n d`, `t h e`, `y o u` — count occurrences per 1000 characters.
- Garbled sequences: lines containing 4+ consecutive consonants with no vowels (e.g., `futreds`, `prgdnaay`) — count per page.
- Excessive inter-word spacing: lines with 5+ consecutive spaces in paragraph-like text.

**Decision matrix:**

| Condition | Classification |
|-----------|---------------|
| No fonts AND no text (1a) | `is_scanned: true`, `scan_type: no_text` — run `ocrmypdf` |
| Full-page image on every page AND text layer exists | `is_scanned: true`, `scan_type: ocr_overlay` — canonical = original PDF (OCR already present), skip `ocrmypdf` |
| Text layer with ≥5 word-internal spacing artifacts per 1000 chars | `is_scanned: true`, `scan_type: ocr_overlay` — canonical = original |
| Text layer with ≥1 garbled sequence per 3 pages sampled | `is_scanned: true`, `scan_type: ocr_overlay` — canonical = original |
| Text layer appears clean (none of the above) | `is_scanned: false`, `scan_type: native` — canonical = original |

When `scan_type: ocr_overlay`, do NOT re-run `ocrmypdf` — the OCR layer already exists. Instead, the vision pass in Step 4c will read the page images directly and use the OCR text only as a hint.

### 1c — Default

If neither 1a nor 1b matched: canonical = original. Record `is_scanned: false`, `scan_type: native`.

If `ocrmypdf` fails (1a path only), write `manifest.json` with `status: failed`, `failed_step: ocr`, and abort this book.

## Step 2 — Detect document structure

Produce an ordered list of `{title, start_page, end_page, kind, slug}` using the **same cascade** as `split-textbooks`:

### 2a — Bookmarks (preferred)

```bash
pdfinfo -outline <canonical>
```

Accept if top-level outline has ≥3 entries matching section patterns (case-insensitive): `preface`, `intro`, `chapter`, `appendix`, `glossary`, `sources`, `bibliography`, `index`.

Set `detection_method: bookmarks`.

### 2b — TOC text parsing (fallback)

```bash
pdftotext -layout -l 30 <canonical> -
```

Find the first page containing "Contents" or "Table of Contents". Capture pages until dotted-leader pattern stops. Parse entries with:

```
^(.+?)\s*\.{2,}\s*(\d+|[ivxlcdm]+)$
```

Resolve **page-number offset**: locate the first chapter title in body text, compute `printed_page - pdf_page_index`, apply globally. Set `detection_method: toc_parse`.

### 2c — LLM fallback (last resort)

Read the front-matter text (first 30 pages) and emit the section list as JSON yourself. Resolve offset as in 2b. Set `detection_method: llm`.

### Section kind classification

| Pattern | `kind` |
|---------|--------|
| `^(preface\|foreword\|introduction\|prologue\|acknowledgments\|table of contents\|contents)$` | `front_matter` |
| `^(chapter\b\|^\d+\b\|^part\b\|^lesson\b\|^unit\b)` | `chapter` |
| `^(appendix\b\|appendix [a-z\d]+)` | `appendix` |
| `^(glossary\|bibliography\|references\|sources\|index\|about the author\|colophon)$` | `back_matter` |
| (no match) | `chapter` |

### End pages

`end_page = next.start_page - 1`; final section ends at `pdfinfo`-reported page count.

## Step 3 — Prepare mdBook scaffold

Create output directory `<out>` (default `<dir>/<stem>-mdbook/`). If it exists and `--force` is not set, abort with a message.

### 3a — `book.toml`

```toml
[book]
title = "<Title from pdfinfo Title field, or PDF stem>"
authors = ["<pdfinfo Author, or 'Unknown'>"]
language = "en"
multilingual = false
src = "src"

[build]
build-dir = "book"
create-missing = false

[preprocessor.index]

[preprocessor.links]
```

If `pdfinfo` does not provide a title, derive from the PDF filename ( Title Case the stem).

### 3b — `src/` directory

```
<out>/
├── book.toml
├── src/
│   ├── SUMMARY.md
│   ├── README.md          (copy of front-matter or generated intro)
│   ├── assets/
│   │   └── images/        (extracted page images and figures)
│   └── <chapter-files>.md
└── manifest.json
```

Create `src/assets/images/` now.

## Step 4 — Per-section content extraction

**Slice-mode substitution.** When `slice_mode: true`, the per-section
extraction loop iterates over slice files instead of page ranges of a
canonical PDF. Throughout this step, substitute the following:
- `<canonical>` → `<dir>/<slice_filename>` (the slice file for this section).
- `-f <start> -l <end>` → drop these flags entirely (the slice contains only
  this section's pages, and they are numbered 1..end_page within the slice).
- `<canonical>` references in `pdfimages -all -f <start> -l <end>` similarly
  drop the `-f`/`-l` flags and use the slice file as the input.

The Step 4 text below is written for `slice_mode: false`. Apply the
substitutions above when in slice mode.

For each section in the detected structure, in order:

### 4a — Decide extraction strategy

| `--vision` flag | Condition | Strategy |
|-----------------|-----------|----------|
| `always` | — | Vision pass every page |
| `never` | — | Text-only rules pass |
| `auto` (default) | `is_scanned == true` (any `scan_type`) | Vision pass every page |
| `auto` | `is_scanned == false` AND section contains tables/equations/complex layout | Vision pass for flagged pages, text for others |
| `auto` | `is_scanned == false` AND clean text layout | Text-only rules pass |

**IMPORTANT**: When `scan_type: ocr_overlay`, the vision pass MUST be used for all pages. The OCR text layer is unreliable and must not be the sole source of content. The page image is the ground truth; the OCR text serves only as a readability hint during the vision pass.

**Heuristic for auto-detection on text-layered PDFs (`scan_type: native`):**
Run `pdftotext -layout -f <start> -l <end> <canonical> -` on the section. If any page shows:
- More than 30% non-ASCII or garbled characters, OR
- Lines that look like table rows (≥3 column-aligned number/word groups separated by 2+ spaces), OR
- Known image placeholders like `[image]`, `Figure`, `Table` with no caption text nearby
→ Flag those pages for vision processing. Process the rest with text rules.

### 4b — Text-only rules pass

1. `pdftotext -layout -f <start> -l <end> <canonical> <tmp>.txt`
2. Tokenize on form-feed `\f` (page boundaries).
3. Drop page numbers: strip first/last non-blank lines that match `^\s*\d+\s*$` or `^\s*[ivxlcdm]+\s*$`.
4. Strip running headers/footers: exact text appearing as first or last non-blank line on ≥3 pages within the section.
5. De-hyphenate: `-\n` + lowercase word → join, except known prefixes (`well-`, `co-`, `non-`, `re-`, `self-`, `ex-`).
6. Reflow paragraphs: join consecutive non-blank lines with a space unless prior line ends with sentence-final punctuation (`.!?`) or closing quote/bracket.
7. Concatenate pages with `\n\n` separators.
8. Collapse whitespace: 3+ blank lines → 2; strip trailing whitespace.
9. Convert simple tables: detect column-aligned blocks (≥3 rows, ≥2 columns separated by 2+ spaces). Convert to pipe tables if alignment is unambiguous; otherwise leave as pre-formatted code blocks.
10. Write result to `src/<slug>.md`.

### 4c — Vision LLM pass

For sections or pages flagged for vision processing:

1. **Render page images** to scratch dir:

   ```bash
   mkdir -p <out>/src/assets/images/<slug>
   pdftoppm -png -r 200 -f <start> -l <end> <canonical> <out>/src/assets/images/<slug>/page
   ```

   Produces `page-01.png`, `page-02.png`, … for the section page range.

2. **Extract per-page raw text** for reference:

   ```bash
   for n in $(seq <start> <end>); do
     pdftotext -layout -f $n -l $n <canonical> <out>/src/assets/images/<slug>/page-$(printf "%02d" $((n-start+1))).txt
   done
   ```

3. **Per-page vision analysis.** For each page image `page-NN.png`:
   - Read the image via the image tool — **this is the primary source of truth** for scanned PDFs.
   - Read the corresponding `page-NN.txt` for raw text reference — this is a *hint only*; for scanned PDFs it contains OCR artifacts (word-internal spacing, garbled boundaries, jumbled columns) that must be corrected from the image.
   - Emit cleaned markdown for that page following the rules in `references/page-processing.md`. Critically:
     - **Remove all running headers, footers, and page numbers** (ALL CAPS book/chapter title repeats, standalone page numbers, combined header+page-number lines).
     - **Fix OCR word-internal spacing** (`t o` → `to`, `i t` → `it`, `o f` → `of`, `a n d` → `and`, `y o u` → `you`, etc.).
     - **Collapse excessive inter-word spacing** to single spaces.
     - **Reconstruct garbled text** from the image when the OCR produced nonsense character sequences.
     - **Reflow paragraphs** into continuous prose with no internal line breaks.
     - **Normalize ALL CAPS body text** to proper case (use **bold** for original emphasis).
     - **Rejoin broken hyphenation** (line-break hyphens → rejoin word; keep legitimate compound hyphens).
   - Append to a per-section accumulator, separated by `\n\n` between pages.

4. **Extract embedded images/figures** (text-layered PDFs only):

   ```bash
   pdfimages -all -f <start> -l <end> <canonical> <out>/src/assets/images/<slug>/fig
   ```

   Review extracted images. Discard tiny images (<10KB, likely icons) and duplicates. Rename significant ones to `fig-NN.ext` and reference them in the markdown as `![description](assets/images/<slug>/fig-NN.ext)` when the vision pass identifies a figure with a caption.

5. **Post-process the section accumulator.** Before writing the file, scan the accumulated markdown for remaining artifacts:
   - Residual running headers/footers (look for ALL CAPS lines that repeat the chapter title or book title, especially with trailing digits).
   - Any remaining word-internal spacing in common short words (` t o `, ` i t `, ` o f `, ` a n d `, ` t h e `, etc.).
   - Lines with excessive inter-word spacing (3+ consecutive spaces within a line that is not a table or code block).
   - Garbled character sequences (runs of 4+ consonants with no vowels, nonsensical word fragments).
   - Stray standalone page numbers on their own line.
   Remove or correct all of these. This is a safety net; most should have been caught per-page.

6. **Write `src/<slug>.md`** from the cleaned accumulator.

7. **Clean up scratch text files** but retain page images and extracted figures in `src/assets/images/` so the built book includes them.

### 4d — Front matter and back matter handling

- **Table of Contents** (`toc`): Convert the detected TOC pages into a clean markdown list linking to chapter files. Use relative mdBook links: `[Chapter Title](chapter-slug.md)`.
- **Index**: If an index section exists, convert to a markdown definition list or bulleted list preserving the alphabetical order. Link terms to their chapters if unambiguous.
- **Bibliography/References**: Convert citation lists to markdown; preserve DOIs/URLs as clickable links.
- **Glossary**: Convert to a markdown table or definition list.

## Step 5 — Write `src/SUMMARY.md`

Build the summary from the detected structure. See `references/mdbook-format.md` for exact syntax.

Template:

```markdown
# Summary

[Introduction](README.md)

<!-- front matter -->
- [Table of Contents](toc.md)
- [Preface](preface.md)

<!-- chapters -->
- [Chapter 1: Limits](01-chapter-01-limits.md)
- [Chapter 2: Derivatives](02-chapter-02-derivatives.md)

<!-- back matter -->
- [Appendix A: Formulas](appendix-a-formulas.md)
- [Bibliography](bibliography.md)
- [Index](index.md)
```

Rules:
- Every section with `kind == chapter` or `kind == appendix` becomes a top-level `-` entry.
- `front_matter` entries appear before chapters, nested under a `- [Front Matter](README.md)` grouping only if there are ≥2 front-matter sections; otherwise list flat.
- `back_matter` entries appear after chapters, grouped similarly.
- Do not nest chapters unless the outline explicitly showed nesting (use indentation).
- `README.md` must exist (create from first front-matter text or a one-line description).

## Step 6 — Write manifest and finalize

Write `<out>/manifest.json`:

```json
{
  "schema_version": 2,
  "slice_mode": false,
  "source_pdf": "book.pdf",
  "source_dir": null,
  "canonical_pdf": "book.ocr.pdf",
  "is_scanned": true,
  "scan_type": "no_text",
  "page_count": 612,
  "page_offset": 12,
  "detection_method": "bookmarks",
  "vision_mode": "auto",
  "mdbook_dir": "book-mdbook",
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "ocrmypdf": "16.10.4",
    "qpdf": "11.9.0",
    "pdftotext": "24.08.0",
    "mdbook": "0.4.40"
  },
  "sections": [
    {
      "index": 0,
      "kind": "front_matter",
      "title": "Table of Contents",
      "slug": "toc",
      "filename": "toc.md",
      "start_page": 5,
      "end_page": 11,
      "slice_filename": null,
      "strategy": "text"
    },
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1: Limits",
      "slug": "chapter-01-limits",
      "filename": "01-chapter-01-limits.md",
      "start_page": 19,
      "end_page": 56,
      "slice_filename": null,
      "strategy": "vision"
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

For a `slice_mode: true` run (input was a directory of pre-split PDFs), the manifest looks like:

```json
{
  "schema_version": 2,
  "slice_mode": true,
  "source_pdf": null,
  "source_dir": "/abs/path/to/book-slices",
  "canonical_pdf": null,
  "is_scanned": false,
  "scan_type": "native",
  "page_count": 0,
  "page_offset": 0,
  "detection_method": "slice_manifest",
  "vision_mode": "auto",
  "mdbook_dir": "book-slices-mdbook",
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "pdftotext": "24.08.0",
    "mdbook": "0.4.40"
  },
  "sections": [
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1: Limits",
      "slug": "chapter-01-limits",
      "filename": "01-chapter-01-limits.md",
      "start_page": 1,
      "end_page": 38,
      "slice_filename": "01-chapter-01-limits.pdf",
      "strategy": "text"
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

Field notes:
- `schema_version`: `2` for runs that follow this recipe (slice-mode aware). Manifests at `1` predate slice support.
- `slice_mode`: `true` when input was a directory of slices; `false` when input was a single PDF.
- `source_pdf`: present when `slice_mode: false`. Set to the input PDF filename.
- `source_dir`: present when `slice_mode: true`. Set to the input directory path.
- `canonical_pdf`: present when `slice_mode: false`. Same as `source_pdf` when not scanned.
- `scan_type`: `"no_text"` (no OCR layer, ocrmypdf was run), `"ocr_overlay"` (scanned images with invisible OCR text layer, vision pass required), or `"native"` (digitally-born PDF with reliable text layer).
- `detection_method`: `bookmarks` | `toc_parse` | `llm` | `slice_manifest` | `slice_filenames`.
- `strategy` per section: `"text"`, `"vision"`, or `"mixed"`.
- `vision_mode`: the effective mode used (`auto`/`always`/`never`).
- `slice_filename` per section: relative filename inside `source_dir` when `slice_mode: true`; `null` otherwise.
- `failed_step`: `ocr`, `detect_outline`, `detect_llm`, `detect_slices`, `scaffold`, `extract`, `build`.

## Step 7 — Validate build

Run:

```bash
cd <out> && mdbook build
```

If `mdbook build` fails:
1. Capture the error output.
2. Fix common issues:
   - Missing files referenced in `SUMMARY.md` → create stub files with `<!-- TODO: content -->`.
   - Broken markdown tables → reformat as code blocks.
   - Invalid image paths → correct relative paths to `assets/images/...`.
3. Re-run `mdbook build`.
4. If still failing, set `status: "failed"`, `failed_step: "build"`, record the error, and stop.

If successful, report:

```
mdBook built successfully at <out>/book/
- Source: <out>/src/
- Chapters: <N>
- Pages with vision processing: <N>
- Images extracted: <N>
- Open with: mdbook serve <out>
```

## Failure handling

Any step failure → write `manifest.json` with `status: "failed"`, populate `failed_step` and `error_message`. Do NOT abort the calling batch if multiple books are queued; continue to the next book. The user retries one book by invoking this skill with the same PDF path.

| Failure | Detected at | Behavior |
|---------|-------------|----------|
| Required tool missing | Step 0 | Print install hints; abort the run. No partial work. |
| Slice directory unrecognized | Step 0.5 | `failed_step: detect_slices`. No partial work. |
| Source PDF corrupt | `pdfinfo` non-zero | `failed_step: detect_outline`. Skip book; continue batch. |
| OCR fails | `ocrmypdf` non-zero | `failed_step: ocr`. Delete `*.ocr.pdf` if zero/missing. |
| All detection methods fail | After 2c | `failed_step: detect_llm`. Write empty `SUMMARY.md` with one entry linking to a single `full-text.md`. Continue. |
| Scaffold exists without `--force` | Step 3 | Abort with message; do not overwrite. |
| Extraction fails | Step 4 | `failed_step: extract`. Record offending section in `error_message`. Partial markdown may exist. |
| `mdbook build` fails | Step 7 | `failed_step: build`. Attempt one auto-fix round. If still failing, stop. |

## Notes

- The `split-textbooks` skill can be used as a pre-processing step to produce sliced PDFs and verify structure detection before running this skill.
- For very large textbooks (500+ pages), consider processing in batches by chapter to avoid context exhaustion. Resume by re-invoking the skill; it skips completed sections if `manifest.json` shows `status: complete`.
- When `manifest.json` exists with `status: complete` and `--force` is not passed, print: "mdBook already built. Use --force to rebuild."
- Images extracted via `pdfimages` or `pdftoppm` are kept in `src/assets/images/` so `mdbook build` bundles them into the output `book/` directory.
