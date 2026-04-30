# split-textbooks fixtures

Three small PDFs for manually verifying the recipe end-to-end. Not run by CI; not consumed by the recipe at deploy time.

| Fixture            | Exercises                       | Expected `detection_method` |
|--------------------|--------------------------------|-----------------------------|
| `outline-text.pdf` | Embedded outline → path 2a      | `bookmarks`                |
| `toc-text.pdf`     | "Contents" page parsing → 2b    | `toc_parse`                |
| `scanned.pdf`      | OCR sidecar + 2b/2c on the OCR | `toc_parse` or `llm`        |

## Expected output (rough)

### Without flags: `/split-textbooks <fixtures-dir>`

- Each book's output dir contains only `*.pdf` slices and `manifest.json`. **No `*.md` files.**
- Manifests report `markdown_generated: false`, `cleanup_method: "none"`.
- `outline-text/` — `is_scanned: false`, `detection_method: "bookmarks"`, ~4 sections.
- `toc-text/` — `is_scanned: false`, `detection_method: "toc_parse"`, ~4 sections, `page_offset: 1`.
- `scanned/` — `scanned.ocr.pdf` exists alongside; `is_scanned: true`, `canonical_pdf: "scanned.ocr.pdf"`, `detection_method: "toc_parse"` or `"llm"`.

### With `--markdown`: `/split-textbooks <fixtures-dir> --markdown`

- Same as above, plus `*.md` sidecars next to each `*.pdf` slice.
- Manifests report `markdown_generated: true`, `cleanup_method: "rules"`, `cleanup_fallbacks: []`.
- Sidecars should be visibly cleaner than `pdftotext -layout` raw output: page numbers stripped, paragraphs reflowed.

### With `--llm-cleanup`: `/split-textbook <fixtures-dir>/scanned.pdf --llm-cleanup`

- `scanned/` re-created. `scanned/.cleanup-tmp/` is gone after the run.
- Sidecars under `scanned/` are visibly cleaner than the rules-only output: headings reconstructed from page images, paragraphs reflowed.
- Manifest reports `markdown_generated: true`, `cleanup_method: "llm"`. `cleanup_fallbacks` may be non-empty if any page exhausted context — that's expected and not an error.

## Regenerating

The fixtures were generated with `pdflatex` and ImageMagick (`magick`). See the implementation plan, Task 10, for the exact source files used.

## Status

The following fixtures could not be generated in the current environment:
- outline-text.pdf (pdflatex not available)
- toc-text.pdf (pdflatex not available)

Generate them later with the steps in the plan when on a host with the required tools.
