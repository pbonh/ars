# Cleaning extracted text into proper Markdown

`assemble_chapters.py` runs cleanup automatically. This file documents
what it does, what it doesn't, and what to do about the leftovers.
Open it when the user reports a chapter looking off, or when you spot-
check a chapter and see one of the artifacts below.

## What the cleanup does automatically

**De-hyphenation across line breaks.** PDFs break words at line ends
with hyphens that aren't real hyphens. The script joins
`compre-\nhensive` into `comprehensive`. It uses a small dictionary
check to avoid joining real hyphenated compounds (`well-\nknown` stays
`well-known`, not `wellknown`).

**Repeated header/footer stripping.** It scans the first and last 3
lines of every page in a chapter, finds substrings that appear on more
than 60% of pages, and strips them. Catches running headers ("Chapter
3 — Foundations") and page numbers.

**Blank-line collapse.** Sequences of 3+ blank lines collapse to 2
(paragraph break). This fixes the "everything is double-spaced after
extraction" problem.

**Heading normalization.** Lines that look like headings (short, all-
caps or title-case, no terminal punctuation, vertical whitespace
around them) get prefixed with `##` or `###` based on relative
prominence within the chapter.

**Smart-quote and ligature cleanup.** Curly quotes stay (they look
nice), but `ﬁ` and `ﬂ` ligatures get expanded to `fi`/`fl` (mdBook's
search index handles them better unsplit).

## Common artifacts the cleanup misses

### Hyphenated breaks at end of paragraphs

Sometimes a paragraph ends mid-word at a page break. The de-hyphenator
tries to join across pages but fails when the broken word is followed
by a chapter-title page or other discontinuity. If you see
`...compre-` at the end of a paragraph, that's the symptom. Search
the chapter for `-$` (line ending in hyphen) to find them.

### Tables that became wall-of-text

`pdftotext --layout` preserves spaces but Markdown doesn't render them
as a table. Three options, in order of effort:

1. **Keep the page as an image.** Rasterize the page region containing
   the table, save as PNG under `src/figures/`, replace the garbled
   text in the chapter with `![Table 3.1](figures/table-3-1.png)`.
   Easy and lossless.
2. **Hand-rebuild the table** as a Markdown pipe table. Worth doing
   for tables the reader needs to use, not for tables they just need
   to see.
3. **Use `pdfplumber` to extract the table structurally** and convert
   to Markdown. See the snippet at the bottom of this file. Worth it
   only if there are many tables in similar formats.

### Footnotes mixed into body text

PDFs render footnotes at the bottom of each page, which extraction
pulls in inline. mdBook's footnote syntax is:

```markdown
Some claim with a footnote.[^1]

[^1]: The footnote text.
```

For a few footnotes, fix by hand. For many, write a small post-
processing pass that recognizes the footnote pattern (numbered or
asterisked line at the end of the page text, often after a small
horizontal rule or run of dashes) and rewrites them. There's no
bundled script for this — the patterns are too book-specific.

### Math and equations

Markdown doesn't natively render math. mdBook supports MathJax when
you set `output.html.mathjax-support = true` in `book.toml`
(`init_mdbook.py` enables this by default). Then write LaTeX inside
`$...$` (inline) or `$$...$$` (display).

For equations OCR mangled, three escalation steps:
1. Look at the original PDF page (rasterize it) and rewrite the
   equation in LaTeX yourself for inline math.
2. For complex equations, screenshot the equation region and embed it
   as an image — `![](figures/eq-3-4.png)`. Clean lossless display
   without LaTeX skill required.
3. Vision-OCR the page and ask for LaTeX output, then paste in.

### Figures and images

`extract_text_pages.py` does NOT extract images. When a chapter
references a figure ("see Figure 3.1 below"), there's nothing visual
in the Markdown.

To pull figures from the original PDF:

```bash
# Extract all images from the chapter's page range
pdfimages -png -f START_PAGE -l END_PAGE input.pdf book-output/src/figures/img

# List them with sizes — small ones are usually decorative
ls -la book-output/src/figures/
```

Then edit the chapter Markdown to reference them at the right spots:
`![Figure 3.1: System overview](figures/img-042.png)`. Yes, this is
manual — the relationship between extracted images and where they
should appear in the prose isn't recoverable from text alone.

For PDFs where vector graphics matter (diagrams drawn natively, not
embedded raster images), `pdfimages` will miss them. Rasterize the
whole page region with `pdftoppm`, crop to the figure with
ImageMagick, save as a PNG.

### Code blocks

Code in PDFs is usually set in a fixed-width font with consistent
indentation. After extraction, it looks like indented prose with weird
line breaks. mdBook treats indented or fenced blocks as code:

````markdown
```python
def hello():
    print("hi")
```
````

If you see a chapter with code that needs fencing, look for clusters
of lines starting with consistent indentation or `>>>` (REPL output)
and wrap them. Worth the effort for any technical book.

### Page-number lines that snuck through

The cleanup strips repeated headers/footers but a stray `42` on its
own line sometimes survives. Search for `^\d+$` lines in chapter files
and remove if they're page numbers (not list items).

## Programmatic table extraction with pdfplumber

When a book has many similar tables and hand-rebuilding is too much
work:

```python
import pdfplumber

with pdfplumber.open("input.pdf") as pdf:
    page = pdf.pages[42]  # zero-indexed
    tables = page.extract_tables()
    for tbl in tables:
        # tbl is list-of-lists. Render as a Markdown pipe table.
        if not tbl or not tbl[0]:
            continue
        header = tbl[0]
        rows = tbl[1:]
        print("| " + " | ".join(c or "" for c in header) + " |")
        print("|" + "|".join("---" for _ in header) + "|")
        for row in rows:
            print("| " + " | ".join(c or "" for c in row) + " |")
```

Use `extract_tables(table_settings={...})` to fine-tune detection if
the defaults don't find your tables. See pdfplumber docs.

## When to stop cleaning

A book with 80% clean chapters and 20% rough edges is much more useful
than a book that's 100% clean but never got built. After
`mdbook build` succeeds, ship the rough draft, then iterate on
specific chapters that need work. Each cleanup pass is `edit chapter
file → mdbook build → reload browser` — fast, no re-extraction needed.
