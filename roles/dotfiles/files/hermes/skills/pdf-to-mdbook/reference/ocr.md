# OCR for scanned PDFs

Triage classifies a PDF as `scanned`, `text`, or `hybrid` based on
extractable text density across a sample of pages. This file covers
how to OCR well — quality matters more than speed for a book that's
about to be published.

## When triage says "scanned"

The PDF has little or no extractable text. Run `ocr_pages.py` for the
whole document, but **always sample first**:

```bash
# OCR a few representative pages first
python scripts/ocr_pages.py input.pdf \
    --out /tmp/ocr-sample \
    --pages 1,50,100,150 \
    --dpi 300 \
    --lang eng
```

View `/tmp/ocr-sample/page_0050.md`. If quality is good (paragraphs
read sensibly, few obvious garbles), run the full job. If not, try the
adjustments below before committing to a slow full run.

## Sample-quality troubleshooting

**Garbled or partial words, missing letters.** The DPI is too low.
Default is 300; try 400 or even 600 for small print. Cost: longer
runtime and more disk for intermediate images.

```bash
python scripts/ocr_pages.py input.pdf --out /tmp/ocr-sample \
    --pages 50 --dpi 600 --lang eng
```

**Skewed scans (text lines slope across the page).** Run `unpaper`
between rasterization and OCR. The script supports this with
`--preprocess unpaper` if `unpaper` is installed.

**Multi-column or complex layout coming out as wall of text.**
Tesseract's default page-segmentation mode assumes one block of text.
For two-column books, pass `--psm 1` (auto with OSD) or `--psm 3`
(default) — usually `--psm 1` is best for academic books. If it still
fails on a specific page, that page may benefit from vision OCR (see
"Vision-OCR escalation" below).

**Non-English text or mixed languages.** Install the Tesseract
language pack (`tesseract-ocr-deu` for German, etc.) and pass
`--lang deu` or `--lang eng+deu` for mixed content.

**Math equations.** Tesseract handles inline math poorly. For
math-heavy books, plan to either (a) keep the equation as an image —
extract the page region with `pdftoppm` and reference it from
Markdown — or (b) escalate to a vision model that can transcribe to
LaTeX.

## Hybrid mode (text PDF with some scanned pages)

Common in PDFs assembled from multiple sources, or text PDFs where the
scanned figures-and-tables pages were inserted as images.

After `extract_text_pages.py` runs, `manifest.json` flags low-text
pages with `"needs_ocr": true`. To OCR only those:

```bash
# Read the manifest's needs_ocr list, format as a page range expression
python scripts/ocr_pages.py input.pdf \
    --out work/pages \
    --from-manifest work/pages/manifest.json
```

The script reads `manifest.json`, OCRs only the flagged pages, and
overwrites those page-files in place. Existing well-extracted pages
stay untouched.

## Automatic image fallback

When Tesseract produces fewer than ~30 characters of recognizable
text on a page, `ocr_pages.py` automatically saves the rasterized
page to `<out>/images/page_NNNN.png` and writes the page Markdown as
an image reference. The page survives into the final mdBook as an
embedded figure instead of vanishing as an empty file. The manifest
records `"fallback": true` for those pages and the script prints a
summary count after the run so you can see how many used it. The
images directory is automatically copied through `assemble_chapters.py`
into the chapters tree, and from there `init_mdbook.py` carries it
into `src/`.

This is the right behaviour for decorative resume layouts,
infographics, or any page whose value is visual rather than textual.
For pages where you actually want the text searchable, escalate
manually to vision OCR (below).

## Vision-OCR escalation (rare, expensive, sometimes worth it)

Tesseract is good for body text but struggles with: handwritten
annotations, decorative fonts, equations, very low-quality scans,
historical typography, and column-mixed pages. For a small number of
critical pages where quality matters more than speed, escalate to
vision OCR.

The pattern:

1. Identify the problem pages from the OCR sample.
2. Rasterize them at high DPI: `pdftoppm -png -r 400 -f N -l N
   input.pdf /tmp/p`.
3. Use the `view` tool on the resulting PNG — this loads the image
   into your context as a vision input.
4. Transcribe the page yourself, write directly to
   `work/pages/page_NNNN.md`.

Don't do this for more than a handful of pages — the token cost is
~1,600 per page and the speed advantage is gone. For dozens of
problem pages, fix the Tesseract config instead.

## Output sanity checks (without reading every page)

After a full OCR run, before assembly:

```bash
# Are there pages that came out empty or near-empty?
python -c "
import json, sys
m = json.load(open('work/pages/manifest.json'))
short = [p for p in m['pages'] if p['chars'] < 200]
print(f'{len(short)} pages under 200 chars:')
for p in short[:20]:
    print(f'  page {p[\"page\"]:4d}: {p[\"chars\"]:4d} chars')
"
```

A handful of short pages is normal (chapter title pages, blanks
between sections). Many short pages clustered together suggests OCR
failure on a section — view a sample of those pages as images, decide
whether to re-OCR with different settings or vision-transcribe.

```bash
# Spot-check overall quality on three random pages from different parts
shuf -i 1-PAGECOUNT -n 3 | while read n; do
    printf "=== page %s ===\n" "$n"
    head -30 "work/pages/page_$(printf %04d $n).md"
done
```

If those three samples read like reasonable English (or whatever the
source language is), the run is good enough to assemble.

## Performance notes

- Tesseract: ~1–3 sec/page at 300 DPI on commodity CPU. A 500-page
  book is 10–25 minutes.
- 400 DPI roughly doubles time but materially improves quality on
  small print or low-quality scans.
- 600 DPI is rarely worth it unless the print is genuinely tiny.
- Run long jobs in the background. The script writes pages
  incrementally and is resumable — interrupt with Ctrl-C, re-run with
  the same args, it picks up where it left off.

## What about cloud OCR APIs?

`ocr_pages.py` uses Tesseract because it runs locally with no
credentials. If the user has access to Google Document AI, AWS Textract,
or Azure Document Intelligence, those produce better output on
difficult inputs — especially for tables, forms, and handwriting.
This skill doesn't bundle integration with them, but if the user
mentions one, you can write a one-off script to call it and produce
the same `pages/page_NNNN.md` layout, then continue with `assemble_chapters.py`
unchanged.
