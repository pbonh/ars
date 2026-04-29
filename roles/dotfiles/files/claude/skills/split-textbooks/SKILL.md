# split-textbooks

You are processing a single PDF textbook. The slash command driving you (`/split-textbooks` or `/split-textbook`) supplies the absolute path to one PDF and tells you whether to overwrite an existing output directory.

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
command -v pdfinfo pdftotext pdffonts qpdf ocrmypdf
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

## Step 4 — Extract markdown

For each sliced PDF:

```bash
pdftotext -layout <slice>.pdf - | <minimal cleanup> > <slice>.md
```

Minimal cleanup only:

- Collapse runs of 3+ blank lines to 2.
- Strip form-feed (`\f`) characters.

Nothing more. The raw extracted text is the contract; for OCR'd books, quality is whatever Tesseract produced.

## Step 5 — Write manifest, mark complete

Write `<book>/manifest.json` with `status: "complete"` using the schema below. This is the marker `--force`-less batch reruns check.

### Manifest schema (single source of truth per book)

```json
{
  "schema_version": 1,
  "source_pdf": "calculus.pdf",
  "canonical_pdf": "calculus.ocr.pdf",
  "is_scanned": true,
  "page_count": 612,
  "page_offset": 12,
  "detection_method": "bookmarks",
  "status": "complete",
  "generated_at": "2026-04-29T14:33:00Z",
  "tool_versions": {
    "ocrmypdf": "16.10.4",
    "qpdf": "11.9.0",
    "pdftotext": "24.08.0"
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

- `canonical_pdf` — file actually used for slicing. Same as `source_pdf` when not scanned.
- `page_offset` — printed-page minus PDF-page index. `0` when outline-based detection didn't need it.
- `kind` enum: `front_matter` | `chapter` | `appendix` | `back_matter`.
- `slug` is the title-derived identifier (`chapter-01-limits`); `filename` is what's on disk (`01-chapter-01-limits` with prefix, or unprefixed for special files).
- `tool_versions` — captured at run time. Get from `<tool> --version` output.
- `detection_method`: `bookmarks` | `toc_parse` | `llm`.
- `failed_step` (only when `status: "failed"`): `detect_outline` | `detect_toc` | `detect_llm` | `ocr` | `slice` | `extract`.

## Manual override path

If the user has manually edited `manifest.json` to set `status: "failed"` and adjusted `page_offset`, respect the edited offset — skip the offset-resolution step in 2b/2c and use the manifest value directly.

## Failure handling

Any step failure → write `manifest.json` with `status: "failed"`, populate `failed_step` and `error_message`. Do NOT abort the calling batch — `/split-textbooks` will continue to the next book. The user retries one book at a time via `/split-textbook <pdf>`.

| Failure                                | Detected at              | Behavior                                                                    |
|----------------------------------------|--------------------------|-----------------------------------------------------------------------------|
| Required tool missing                  | Step 0 self-check        | Print install instructions; abort the run. No partial work.                |
| Source PDF corrupt / not a PDF         | `pdfinfo` non-zero       | `failed_step: "detect_outline"`. Skip book; continue batch.                |
| OCR pass fails                         | `ocrmypdf` non-zero      | `failed_step: "ocr"`. If `*.ocr.pdf` is zero/missing, delete it.           |
| All three detection methods fail       | After 2c                 | `failed_step: "detect_llm"`. `sections: []`; include front-matter dump.    |
| `qpdf` slice fails for one section     | During slicing loop      | `failed_step: "slice"`; record offending index in `error_message`.         |
| `pdftotext` fails (e.g., disk full)    | During extraction        | `failed_step: "extract"`. Slices retained; markdown sidecars partial.      |

**Guiding principle:** every failure is recorded in `manifest.json`; never abort the batch; the user has one command (`/split-textbook`) to retry one book.
