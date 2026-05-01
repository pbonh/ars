# Page Processing Reference

Rules for converting a single PDF page into clean markdown, used during both the text-rules pass and the vision LLM pass.

## When to use the vision LLM pass

Use vision processing when any of the following are true for a page:

1. **Scanned PDF** — `is_scanned == true` (almost every page).
2. **Complex layout** — Multi-column text, sidebars, or pull-quotes that `pdftotext -layout` jumbles.
3. **Tables** — Structured data with ≥3 rows and ≥2 columns. Text extraction renders them unreadable.
4. **Figures / images** — Pages containing photographs, diagrams, charts, or maps.
5. **Equations** — Mathematical notation that text extraction garbles.
6. **Garbled text** — `pdftotext` produces >30% non-ASCII artifacts on the page.

When `--vision always`, process every page with vision.
When `--vision never`, use text rules only (skip this document's vision-specific guidance).

## Per-page vision LLM rules

For each page image and its corresponding raw text:

### Preserve all source text exactly
- Do **not** paraphrase, summarize, correct grammar, or "fix" apparent errors.
- The raw text from `pdftotext` is the contract; the image confirms layout.

### Reconstruct headings
- Identify headings by visual size, weight, or centering.
- Map to markdown heading levels:
  - Largest / chapter title → `# Heading`
  - Section header → `## Heading`
  - Subsection → `### Heading`
  - Smallest / paragraph header → `#### Heading`

### Reflow paragraphs
- Join broken lines and columns into single paragraphs.
- Preserve blank lines as paragraph breaks.

### Handle tables
- **Clean tables**: unambiguous rows and columns with clear headers → convert to pipe tables.
  ```markdown
  | Column A | Column B |
  |----------|----------|
  | Value 1  | Value 2  |
  ```
- **Messy tables**: partial lines, nested cells, or heavy formatting → use a fenced code block with fixed-width alignment, or describe the structure in prose if too degraded.
- **Wide tables**: if a table exceeds ~120 characters wide, use a code block instead of a pipe table to avoid wrapping issues.

### Handle images and figures
- If the page contains a photograph, diagram, chart, or illustration that conveys substantive information:
  1. Note its position in the text flow.
  2. Transcribe the caption exactly if present.
  3. In the markdown output, insert an image reference placeholder:
     ```markdown
     ![Figure 3.2: Exact caption text](assets/images/<slug>/page-NN.png)
     ```
     Use the `page-NN.png` file produced by `pdftoppm` for that specific page.
  4. If `pdfimages` extracted a cleaner figure file (`fig-NN.ext`), reference that instead.
- If the image is purely decorative (border, watermark, icon), omit it and do not create a placeholder.
- Do **not** invent `[Figure X]` placeholders for images you cannot see or describe. If there is no caption and the image is essential, describe it briefly in alt text.

### Handle equations
- Inline math: surround with `$...$`.
- Display math: use `$$...$$` on its own lines.
- If LaTeX is uncertain, preserve the raw text and wrap in a fenced block:
  ```markdown
  ```text
  <raw extracted equation>
  ```
  ```

### Drop artifacts
- Remove running headers, footers, and page numbers (same as text-rules pass).
- Remove watermarks or "draft" markings unless they are part of the original published content.

### Code blocks
- Programming or pseudocode listings → fenced code blocks with language tag if identifiable.
- Terminal output or logs → ` ```text ` blocks.

## Image extraction commands

### Render page images (for vision pass)

```bash
pdftoppm -png -r 200 -f <start> -l <end> <canonical> <out-prefix>/page
```

- `-r 200` gives sufficient resolution for text and table OCR without excessive size.
- Output files: `page-01.png`, `page-02.png`, …

### Extract embedded images (text-layered PDFs)

```bash
pdfimages -all -f <start> -l <end> <canonical> <out-prefix>/fig
```

- `-all` saves images in their native format (PNG/JPEG/etc.).
- Review outputs: discard images <10 KB (likely icons or bullet points).
- Rename significant images to `fig-01.png`, `fig-02.jpg`, … for clean referencing.

### Deduplicate extracted images

```bash
# Example: remove exact duplicates by hash
find <out-prefix> -type f -exec md5sum {} + | sort | uniq -w32 -dD
```

Keep only one copy of each duplicate and reference it from all locations.

## Text-rules pass details

Applied to pages flagged as "text-only" when `vision` is `auto` or `never`.

1. **Tokenize on form-feed** (`\f`) — `pdftotext` page boundary.
2. **Drop page numbers** — first/last non-blank lines matching `^\s*\d+\s*$` or `^\s*[ivxlcdm]+\s*$`.
3. **Strip running heads/footers** — exact text repeated as first/last line on ≥3 pages.
4. **De-hyphenate** — `-\n` + lowercase word → join. Preserve known prefixes (`well-`, `co-`, `non-`, `re-`, `self-`, `ex-`).
5. **Reflow paragraphs** — join lines unless prior line ends with `.!?` or `\"'\)\]`.
6. **Concatenate pages** with `\n\n` separators.
7. **Collapse whitespace** — 3+ blank lines → 2; strip trailing whitespace.
8. **Simple table conversion** — detect column-aligned blocks (≥3 rows, ≥2 columns, separated by 2+ spaces). Convert to pipe tables if unambiguous; otherwise wrap in ` ```text ` blocks.

## Markdown output constraints

- No HTML tags. Use pure markdown.
- No inline styles.
- Front matter (YAML) in chapter files is **not** used by default mdBook; omit it unless a preprocessor is configured.
- Prefer reference-style links over inline URLs for readability.
