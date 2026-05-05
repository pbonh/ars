# Page Processing Reference

Rules for converting a single PDF page into clean markdown, used during both the text-rules pass and the vision LLM pass.

## When to use the vision LLM pass

Use vision processing when any of the following are true for a page:

1. **Scanned PDF** — `is_scanned == true` (any `scan_type`). This includes `scan_type: ocr_overlay` — PDFs that have a text layer but are actually scanned images with invisible OCR text. **These are extremely common** and the OCR text layer is unreliable.
2. **Complex layout** — Multi-column text, sidebars, or pull-quotes that `pdftotext -layout` jumbles.
3. **Tables** — Structured data with ≥3 rows and ≥2 columns. Text extraction renders them unreadable.
4. **Figures / images** — Pages containing photographs, diagrams, charts, or maps.
5. **Equations** — Mathematical notation that text extraction garbles.
6. **Garbled text** — `pdftotext` produces >30% non-ASCII artifacts on the page.

When `--vision always`, process every page with vision.
When `--vision never`, use text rules only (skip this document's vision-specific guidance).

**IMPORTANT**: When `scan_type: ocr_overlay`, vision processing is mandatory for ALL pages regardless of the `--vision` flag setting (unless `--vision never` is explicitly set by the user, in which case warn that output quality will be severely degraded). The OCR text layer in these PDFs produces word-internal spacing artifacts, garbled character sequences at line boundaries, jumbled multi-column text, and broken hyphenation. It is NOT a reliable source of content on its own.

## Per-page vision LLM rules

For each page image and its corresponding raw text:

### Source authority: IMAGE is primary for scanned PDFs

For scanned PDFs (`is_scanned == true`), **the page image is the ground truth**. The raw `pdftotext` output is merely a hint to aid transcription — it often contains word-internal spacing artifacts, garbled characters at line boundaries, and jumbled multi-column text. When the raw text and the image disagree, **trust the image**.

For text-layered PDFs, the raw text is generally reliable; use the image only to confirm layout, resolve ambiguous formatting, and catch missed elements.

### Preserve the MEANING, not the OCR formatting

- Do **not** paraphrase, summarize, or omit substantive content.
- Do **not** "fix" the author's actual words — preserve the author's phrasing, vocabulary, and intent.
- **DO fix OCR artifacts** — the broken spacing, garbled characters, jumbled columns, and stray headers described below are NOT the author's words; they are machine errors. Cleaning these up is not "editing" — it is accurate transcription from the image.

### Remove running headers, footers, and page numbers

Scanned books repeat the same text at the top and/or bottom of every page. These are NOT body content and must be removed entirely:

- **Page numbers** — standalone digits or roman numerals at top/bottom of page (e.g., "10", "52", "iv").
- **Book title or chapter title in header/footer** — often ALL CAPS, e.g., "KNOCK 'EM DEAD", "KNOCK 'EM DEAD 10".
- **Running heads with page number** — e.g., "YOUR RESUME—THE MOST FINANCIALLY IMPORTANT DOCUMENT YOU'LL EVER OWN 11".
- **Chapter/section decoration** — e.g., "CHAPTER 1", "CHAPTER 4" repeated as a page header.
- **Repeat header at top of page** — sometimes the chapter title is reprinted in large/decorative type at the top of a page; this is a running head, not a new heading.

**Detection rule**: If a line at the top or bottom of the page image is in ALL CAPS, uses a distinctly different typeface/size from body text, and especially if it includes a page number — it is a running header/footer. Remove it completely.

### Fix OCR word-internal spacing artifacts

Scanned PDF OCR frequently inserts spurious spaces within words, especially short common words. These MUST be corrected:

| OCR artifact | Correct form |
|-------------|-------------|
| `t o` | `to` |
| `i t` | `it` |
| `i s` | `is` |
| `o f` | `of` |
| `i n` | `in` |
| `o n` | `on` |
| `a n` | `an` |
| `b e` | `be` |
| `b y` | `by` |
| `h e` | `he` |
| `w e` | `we` |
| `a t` | `at` |
| `a s` | `as` |
| `o r` | `or` |
| `s o` | `so` |
| `d o` | `do` |
| `g o` | `go` |
| `n o` | `no` |
| `u p` | `up` |
| `m e` | `me` |
| `y o u` | `you` |
| `t h e` | `the` |
| `a n d` | `and` |
| `f o r` | `for` |
| `n o t` | `not` |
| `b u t` | `but` |
| `w i l l` | `will` |
| `w i t h` | `with` |
| `t h a t` | `that` |
| `t h i s` | `this` |
| `f r o m` | `from` |
| `h a v e` | `have` |
| `w h e n` | `when` |
| `w h o` | `who` |
| `w h a t` | `what` |
| `y o u r` | `your` |
| `c a n` | `can` |
| `a r e` | `are` |
| `w a s` | `was` |
| `h o w` | `how` |
| `o u t` | `out` |

**Rule**: Any word that appears in the image as a normal continuous word but is split by spaces in the OCR text must be re-joined. This especially affects short function words (2–4 letters) and common words. When reading the image, these words are clearly printed as one unit — render them as one word.

### Collapse excessive inter-word spacing

OCR from scanned PDFs often preserves the spatial layout of the original, inserting many spaces between words that were spread across a line. This is not meaningful formatting — it is a layout artifact.

**Rule**: Normalize all inter-word spacing to a single space. Never output two or more consecutive spaces between words within a paragraph. The only place multiple spaces belong is inside code blocks or pre-formatted table alignment.

### Fix garbled text at line/column boundaries

Scanned PDF OCR frequently produces garbled or jumbled text where lines break or columns are misread. Symptoms include:

- Nonsense character sequences at the start/end of lines (e.g., "cimkeranalts", "futredsi")
- Characters from two adjacent lines intermixed (e.g., "me es into aseayldi iv")
- Characters from an adjacent column bleeding in (e.g., "deniu profesionalrepuiroatnniu")
- Truncated words at the end of a line where the continuation on the next line was missed

**Rule**: Read the page IMAGE to determine what the text actually says. The OCR text is a broken hint — the image shows you the real words. Reconstruct the correct text from the image. If a section is too garbled to read from the image either, insert an HTML comment: `<!-- OCR garbled: unable to reconstruct this passage -->` and include your best approximation of the readable text.

### Reconstruct multi-column layouts

When the original page has two or more columns of text:

- Read each column separately from the image, top to bottom.
- Do NOT weave columns together line-by-line (this is what OCR does and it produces gibberish).
- Flow the text as it would be read: complete the first column, then the second, etc.
- If columns are visually independent (like a sidebar), consider using a blockquote or callout formatting.
- If columns are continuation of the same text flow, concatenate them in reading order.

### Rejoin broken hyphenation

OCR often captures hyphenated line breaks from the original. Rejoin these:

- `ch al-\nenges` → `challenges` (remove hyphen, join fragments)
- `profes-\nsional` → `professional`
- `recog-\nnize` → `recognize`

**Exception**: Keep legitimate compound-word hyphens (`well-known`, `self-aware`, `long-term`, `co-worker`, `problem-solving`). The image will show these as hyphens within a single line, not as line-ending hyphens.

### Reconstruct headings

- Identify headings by visual size, weight, or centering.
- Map to markdown heading levels:
  - Largest / chapter title → `# Heading`
  - Section header → `## Heading`
  - Subsection → `### Heading`
  - Smallest / paragraph header → `#### Heading`
- **Normalize ALL CAPS to Title Case or sentence case** as appropriate for the heading. A chapter title printed as "YOUR RESUME—THE MOST FINANCIALLY IMPORTANT DOCUMENT YOU'LL EVER OWN" in the original should become a heading like `# Your Resume—The Most Financially Important Document You'll Ever Own`. Body text set in small caps or ALL CAPS for emphasis in the original should be converted to normal case; use **bold** if the original used typographic emphasis.
- Do NOT create duplicate headings. If the chapter title was already emitted as the `#` heading at the top of the file, do not repeat it when it appears as a running header on a subsequent page.

### Reflow paragraphs into continuous prose

This is critical for scanned PDF output quality. The raw OCR preserves line breaks from the original typesetting, which breaks natural paragraph flow.

**Rules for reflow**:

1. Read the paragraph as a coherent block of text from the image.
2. Output it as a single continuous paragraph — one unbroken block of text with no internal line breaks.
3. Join lines with a single space.
4. Do NOT preserve the original line-breaking — it is a typesetting artifact, not semantic content.
5. A new paragraph begins where the image shows a clear paragraph break: indentation, extra vertical space, or a change in text style.
6. Separate paragraphs with a blank line (standard markdown).
7. Do NOT insert blank lines within a paragraph.

**Example of correct reflow**:

OCR raw text (BROKEN — do NOT output this way):
```
No one enjoys writing a resume, but i t has such a major impact on the money you
                                                                                   earn during
your       work      life,    and consequently              on the quality       of your       life outside     of work,       that you know            it
needs t o b e done right.
```

Correct output (CLEAN):
```
No one enjoys writing a resume, but it has such a major impact on the money you earn during your work life, and consequently on the quality of your life outside of work, that you know it needs to be done right.
```

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

### Handle lists and enumerated items

- Preserve the original's list structure: bulleted lists as `-` items, numbered lists as `1.`, `2.`, etc.
- If the OCR scrambles list items (common in scanned PDFs with indentation), reconstruct the list from the image.

### Drop all artifacts

- Remove running headers, footers, and page numbers (as detailed above).
- Remove watermarks or "draft" markings unless they are part of the original published content.
- Remove publisher decorations: decorative lines, ornaments, publisher logos on chapter openers, etc.
- Remove repeated chapter/section title banners that duplicate the actual heading.

### Code blocks

- Programming or pseudocode listings → fenced code blocks with language tag if identifiable.
- Terminal output or logs → ` ```text ` blocks.

### Per-page output quality checklist

Before finalizing the markdown for a page, verify ALL of the following:

- [ ] No running headers or footers remain (no ALL CAPS book/chapter title repeats, no standalone page numbers)
- [ ] No word-internal spacing artifacts (`t o`, `i t`, `o f`, `a n d`, etc. are all corrected)
- [ ] No excessive inter-word spacing (all words separated by exactly one space)
- [ ] No garbled or jumbled character sequences
- [ ] No broken hyphenation (legitimate compound-word hyphens preserved, line-break hyphens rejoined)
- [ ] Paragraphs are reflowed into continuous prose with no internal line breaks
- [ ] ALL CAPS body text has been normalized to proper case (with **bold** for original emphasis if appropriate)
- [ ] Headings use markdown `#` syntax and are in Title Case or sentence case
- [ ] No duplicate headings (chapter title not repeated from running header)
- [ ] Lists are properly formatted with `-` or `1.` syntax
- [ ] Tables are pipe tables or code blocks (not raw spaced text)

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

- No HTML tags (except `<!-- comments -->` for unrecoverable garbled passages). Use pure markdown.
- No inline styles.
- Front matter (YAML) in chapter files is **not** used by default mdBook; omit it unless a preprocessor is configured.
- Prefer reference-style links over inline URLs for readability.
- Every paragraph must be a single continuous block of text — no hard line wraps within paragraphs.
