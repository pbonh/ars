---
name: split-textbooks
description: Use when the user asks to split a PDF textbook into chapters, slice a book by sections, or extract markdown from a textbook PDF. Handles scanned and text-layered PDFs, auto-detects table of contents, and produces sliced PDFs with optional markdown sidecars.
---

# Split Textbooks

You are processing a single PDF textbook. The skill is invoked when the user asks to split a textbook, slice a PDF by chapters, or extract markdown from a book.

The user supplies the absolute path to one PDF, whether to overwrite an existing output directory, and two optional flags:

- `markdown` (boolean) — when `true`, write a `.md` sidecar alongside each PDF slice. Default `false`: produce only PDF slices and the manifest.
- `llm_cleanup` (boolean) — when `true`, use the per-page LLM cleanup pass instead of the rules pass. Implies `markdown: true`. Default `false`.

## Output layout

Given input `<dir>/book.pdf`:

```
<dir>/
├── book.pdf                       (untouched original)
├── book.ocr.pdf                   (sidecar OCR — only if scanned)
└── book/                          (output subfolder, name matches stem)
    ├── manifest.json
    ├── toc.pdf  +  toc.md
    ├── 00-preface.pdf  +  00-preface.md
    ├── 01-chapter-01-limits.pdf  +  01-chapter-01-limits.md
    ├── ...
    ├── glossary.pdf  +  glossary.md
    └── sources.pdf  +  sources.md
```

- Chapters / appendices / front-matter use a numeric prefix `NN-<slug>` for order.
- Special files (`toc`, `glossary`, `sources`, `index`, `bibliography`) are unprefixed.

## Step 0 — Environment self-check (once per session)

Run:

```bash
command -v pdfinfo pdftotext pdffonts pdftoppm qpdf ocrmypdf
```

If any are missing, print install hints and abort:

- macOS (Homebrew): `brew install poppler qpdf ocrmypdf`
- Linux (devbox/nix): `devbox add poppler qpdf ocrmypdf`

Re-run the relevant Ansible role (`just homebrew` or `just devbox`) afterwards.

## Step 1 — Resolve canonical PDF (scanned vs. text-layered)

Given input `<path>/book.pdf`:

1. Run `pdffonts <path>/book.pdf | tail -n +3` — output past the 2-line header. Empty → no embedded fonts.
2. AND `pdftotext -l 5 <path>/book.pdf -` produces empty/whitespace-only output (no extractable text in first 5 pages).
3. → Scanned PDF. Run:

   ```bash
   ocrmypdf --skip-text --output-type pdf <path>/book.pdf <path>/book.ocr.pdf
   ```

   Canonical PDF for downstream steps is `<path>/book.ocr.pdf`. Set `is_scanned: true` in the manifest.
4. Otherwise canonical = original. Set `is_scanned: false`.

`--skip-text` makes `ocrmypdf` idempotent on mixed-content PDFs.

## Step 2 — Detect sections (cascade)

Each path produces an ordered list of `{title, start_page, kind}`. End pages are computed as `next.start_page - 1`; the final section ends at `pdfinfo`'s reported page count.

### 2a — Bookmarks (preferred)

```bash
pdfinfo -outline <canonical>
```

If the top-level outline has at least 3 entries that look like sections (matching: preface, intro, chapter, appendix, glossary, sources, bibliography, index — case-insensitive), accept and build the manifest from outline entries. Set `detection_method: "bookmarks"`.

### 2b — TOC text parsing (fallback)

```bash
pdftotext -layout -l 30 <canonical> -
```

Find the first page containing "Contents" or "Table of Contents" as a heading. Continue capturing pages until the dotted-leader pattern stops.

Parse entries with regex:

```
^(.+?)\s*\.{2,}\s*(\d+|[ivxlcdm]+)$
```

Resolve **page-number offset**: locate the first chapter title in the body text, compute the delta between the printed page number and the PDF page index, apply globally. Set `detection_method: "toc_parse"`.

### 2c — LLM fallback (last resort)

```bash
pdftotext -l 30 <canonical> -
```

Read the front matter and emit the section list as JSON yourself. Resolve offset the same way as 2b. Set `detection_method: "llm"`.

### Section-kind classification

Apply to each title (case-insensitive):

| Pattern                                                                                                          | `kind`         |
|------------------------------------------------------------------------------------------------------------------|----------------|
| `^(preface|foreword|introduction|prologue|acknowledgments|table of contents|contents)`                           | `front_matter` |
| `^(chapter\b|^\d+\b|^part\b|^lesson\b|^unit\b)`                                                                  | `chapter`      |
| `^(appendix\b|appendix [a-z\d]+)`                                                                                | `appendix`     |
| `^(glossary|bibliography|references|sources|index|about the author|colophon)`                                    | `back_matter` |
| (no match)                                                                                                        | `chapter`     |

## Step 3 — Slice

For each section:

```bash
qpdf --empty --pages <canonical> <start>-<end> -- <out>/<filename>.pdf
```

Filename rules:

- Chapters / appendices / front-matter (other than `toc`): `NN-<slug>.pdf` where `NN` is two-digit zero-padded section index, `<slug>` is the lowercased title with non-alphanumeric runs collapsed to `-`.
- Special files: `toc.pdf`, `glossary.pdf`, `sources.pdf`, `index.pdf`, `bibliography.pdf` — unprefixed.
- The `toc` slice uses the page range detected in 2b (or the outline's "Contents" entry range in 2a).

## Step 4 — Extract markdown (only when `markdown: true`)

If `markdown` is `false`, skip this entire step. Set `markdown_generated: false`, `cleanup_method: "none"` in the manifest and continue to Step 5.

Otherwise, for each section slice:

1. Run `pdftotext -layout <slice>.pdf <slice>.raw.txt` to capture raw extracted text.
2. Apply cleanup based on `llm_cleanup`:
   - `false` → **Step 4a (rules cleanup)** below.
   - `true` → **Step 4b (LLM cleanup)** below.
3. Write the cleaned result to `<slice>.md`.
4. Delete `<slice>.raw.txt`.

### Step 4a — Rules cleanup (default for `markdown: true`)

Operates on the raw text from `pdftotext -layout`. Apply in this order:

1. **Tokenize on form-feed (`\f`).** That's `pdftotext`'s page boundary marker. Process subsequent steps page-by-page.
2. **Drop page numbers.** A line that is whitespace plus only digits or only roman numerals (case-insensitive `^\s*[ivxlcdm]+\s*$` or `^\s*\d+\s*$`) is a page number. Strip it only if it is the first or last non-blank line on the page (avoid clobbering numbered list items in body text).
3. **Detect and strip running headers/footers.** A line is a running head if its exact text is the first non-blank line of ≥3 pages within the slice. Same rule for the last non-blank line (running foot). Strip every occurrence on every page.
4. **De-hyphenate across line breaks.** A line ending in `-\n` followed by a lowercase-starting word → join, dropping the hyphen. Skip when the prefix before the hyphen is a known compound prefix (`well-`, `co-`, `non-`, `re-`, `self-`, `ex-`); leave those alone.
5. **Reflow paragraphs within a page.** Consecutive non-blank lines join with a single space when the prior line does not end with sentence-final punctuation (`.!?:`) or a closing quote/bracket (`"'\)\]`). Blank lines preserve as paragraph breaks.
6. **Concatenate pages** with `\n\n` separators between pages.
7. **Collapse whitespace.** Runs of 3+ blank lines collapse to 2; trailing whitespace on each line is stripped.

The rules are conservative — they leave some artifacts (column splits, broken tables) rather than risk damaging the source. The promise is "better than `pdftotext -layout` alone, never worse."

Set `cleanup_method: "rules"` in the manifest.

### Step 4b — LLM cleanup (opt-in, `llm_cleanup: true`)

For each section slice, in sequence:

1. **Render per-page images** into a per-slice scratch dir:

   ```bash
   mkdir -p <out>/.cleanup-tmp/<slug>
   pdftoppm -png -r 150 <slice>.pdf <out>/.cleanup-tmp/<slug>/page
   ```

   Produces `page-1.png`, `page-2.png`, … one per slice page.

2. **Extract per-page raw text** into the same scratch dir, one file per page:

   ```bash
   for n in $(seq 1 <page_count_of_slice>); do
     pdftotext -layout -f $n -l $n <slice>.pdf <out>/.cleanup-tmp/<slug>/page-$n.txt
   done
   ```

3. **Per-page LLM pass.** For each page N from 1 to `<page_count_of_slice>`:
   - Read `page-N.png` via the image tool — gives you the visual structure.
   - Read `page-N.txt` — gives you the raw text.
   - Emit cleaned markdown for that page only, following the rules below.
   - Append to a per-slice accumulator separated by `\n\n` between pages.

4. **Write `<slice>.md`** from the accumulator.

5. **Remove `<out>/.cleanup-tmp/<slug>/`** after the slice's `.md` is written. Page images are large; do not leave them around.

When all slices for the book complete, remove `<out>/.cleanup-tmp/` entirely.

#### Per-page cleanup rules

When emitting cleaned markdown for a page, follow these rules strictly:

- **Preserve all source text exactly.** Do not paraphrase, summarize, correct grammar, expand abbreviations, or "fix" what looks like an error in the source. The raw text is the contract.
- **Reflow paragraphs** that are broken across lines or columns into single paragraphs.
- **Reconstruct headings** from visual structure: larger fonts, bold, centered text → `#`/`##`/`###`. Use the relative font sizes visible in the page image.
- **Preserve code blocks, equations, and tables** as fenced code blocks or pipe tables when the structure is unambiguous; leave as plain prose otherwise.
- **Drop running headers, footers, and page numbers** — same artifacts the rules pass strips.
- **Do not invent content.** No synthetic section headers, no inferred "see also" links, no bracketed `[figure]` placeholders for figures you cannot transcribe. If a figure has a caption, transcribe only the caption text.

#### LLM pass failure → graceful per-section fallback

If the LLM pass fails for a section (page image unreadable, context exhausted, tool error, etc.), do not abort the section. Instead:

1. Discard whatever was produced for that section.
2. Run the rules pass (Step 4a) on the slice's `.raw.txt`.
3. Write `<slice>.md` from the rules output.
4. In the manifest, append to a top-level `cleanup_fallbacks` array:

   ```json
   { "section_index": 3, "reason": "context_exhausted" }
   ```

5. Leave `cleanup_method: "llm"` for the book — at least one section did use the LLM pass. If *every* section fell back, set `cleanup_method: "rules"` instead.

If the LLM pass fails *before* any sections complete (e.g., `pdftoppm` is not installed), abort Step 4 entirely with `failed_step: "cleanup"`, `cleanup_method: "none"`, `markdown_generated: false`. Do not leave partial markdown behind.

Set `cleanup_method: "llm"` (or `"rules"` if every section fell back) in the manifest.

## Step 5 — Write manifest, mark complete

Write `<book>/manifest.json` with `status: "complete"` using the schema below. This is the marker `--force`-less batch reruns check.

### Manifest schema (single source of truth per book)

```json
{
  "schema_version": 2,
  "source_pdf": "calculus.pdf",
  "canonical_pdf": "calculus.ocr.pdf",
  "is_scanned": true,
  "page_count": 612,
  "page_offset": 12,
  "detection_method": "bookmarks",
  "markdown_generated": true,
  "cleanup_method": "llm",
  "cleanup_fallbacks": [],
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "ocrmypdf": "16.10.4",
    "qpdf": "11.9.0",
    "pdftotext": "24.08.0",
    "pdftoppm": "24.08.0"
  },
  "sections": [
    {
      "index": 0,
      "kind": "front_matter",
      "title": "Table of Contents",
      "slug": "toc",
      "filename": "toc",
      "start_page": 5,
      "end_page": 11
    },
    {
      "index": 1,
      "kind": "chapter",
      "title": "Chapter 1: Limits",
      "slug": "chapter-01-limits",
      "filename": "01-chapter-01-limits",
      "start_page": 19,
      "end_page": 56
    }
  ],
  "failed_step": null,
  "error_message": null
}
```

**Field notes:**

- `schema_version` is `2` for runs that use this recipe. Manifests at `1` were produced by the previous recipe; their `markdown_generated` and `cleanup_method` are implicitly absent.
- `canonical_pdf` — file actually used for slicing. Same as `source_pdf` when not scanned.
- `page_offset` — printed-page minus PDF-page index. `0` when outline-based detection didn't need it.
- `markdown_generated` — `true` when `.md` sidecars were produced this run; `false` when `markdown: false` was passed.
- `cleanup_method` — `"none"` when `markdown_generated: false`; otherwise `"rules"` or `"llm"` per the flags. If `llm_cleanup: true` was set but every section fell back to rules, this is `"rules"`.
- `cleanup_fallbacks` — array of `{section_index, reason}` entries recording sections where the LLM pass fell back to rules. Empty array when no fallbacks (or when `cleanup_method: "rules"` from the start).
- `kind` enum: `front_matter` | `chapter` | `appendix` | `back_matter`.
- `slug` is the title-derived identifier (`chapter-01-limits`); `filename` is what's on disk (`01-chapter-01-limits` with prefix, or unprefixed for special files).
- `tool_versions` — captured at run time. Get from `<tool> --version` output. Include `pdftoppm` only when `cleanup_method: "llm"`.
- `detection_method`: `bookmarks` | `toc_parse` | `llm`.
- `failed_step` (only when `status: "failed"`): `detect_outline` | `detect_llm` | `ocr` | `slice` | `extract` | `cleanup`.

## Manual override path

If the user has manually edited `manifest.json` to set `status: "failed"` and adjusted `page_offset`, respect the edited offset — skip the offset-resolution step in 2b/2c and use the manifest value directly.

## Failure handling

Any step failure → write `manifest.json` with `status: "failed"`, populate `failed_step` and `error_message`. Do NOT abort the calling batch — the user may process multiple books; continue to the next book. The user retries one book at a time by invoking this skill again with the specific PDF path.

| Failure                                | Detected at              | Behavior                                                                    |
|----------------------------------------|--------------------------|-----------------------------------------------------------------------------|
| Required tool missing                  | Step 0 self-check        | Print install instructions; abort the run. No partial work.                |
| Source PDF corrupt / not a PDF         | `pdfinfo` non-zero       | `failed_step: "detect_outline"`. Skip book; continue batch.                |
| OCR pass fails                         | `ocrmypdf` non-zero      | `failed_step: "ocr"`. If `*.ocr.pdf` is zero/missing, delete it.           |
| All three detection methods fail       | After 2c                 | `failed_step: "detect_llm"`. `sections: []`; include front-matter dump.    |
| `qpdf` slice fails for one section     | During slicing loop      | `failed_step: "slice"`; record offending index in `error_message`.         |
| `pdftotext` fails (e.g., disk full)    | During extraction        | `failed_step: "extract"`. Slices retained; markdown sidecars partial.      |
| LLM cleanup fails before any section completes | Step 4b first slice | `failed_step: "cleanup"`, `cleanup_method: "none"`, `markdown_generated: false`. No partial markdown. |
| LLM cleanup fails for one section      | Step 4b mid-loop         | Per-section fallback to rules; recorded in `cleanup_fallbacks`. Book still completes. |

**Guiding principle:** every failure is recorded in `manifest.json`; never abort the batch; the user has one command (invoke this skill with the PDF path) to retry one book.
