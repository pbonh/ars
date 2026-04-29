# split-textbooks fixtures

Three small PDFs for manually verifying the recipe end-to-end. Not run by CI; not consumed by the recipe at deploy time.

| Fixture            | Exercises                       | Expected `detection_method` |
|--------------------|--------------------------------|-----------------------------|
| `outline-text.pdf` | Embedded outline → path 2a      | `bookmarks`                |
| `toc-text.pdf`     | "Contents" page parsing → 2b    | `toc_parse`                |
| `scanned.pdf`      | OCR sidecar + 2b/2c on the OCR | `toc_parse` or `llm`        |

## Expected output (rough)

After `/split-textbooks <fixtures-dir>`:

- `outline-text/` — manifest with `is_scanned: false`, `detection_method: "bookmarks"`, ~4 sections (preface, chapter 1, chapter 2, glossary).
- `toc-text/` — manifest with `is_scanned: false`, `detection_method: "toc_parse"`, ~4 sections, `page_offset: 1` (the "Contents" page itself).
- `scanned/` — `scanned.ocr.pdf` exists alongside; manifest with `is_scanned: true`, `canonical_pdf: "scanned.ocr.pdf"`, `detection_method: "toc_parse"` or `"llm"` (depends on OCR quality).

## Regenerating

The fixtures were generated with `pdflatex` and ImageMagick (`magick`). See the implementation plan, Task 10, for the exact source files used.

## Status

The following fixtures could not be generated in the current environment:
- outline-text.pdf (pdflatex not available)
- toc-text.pdf (pdflatex not available)

Generate them later with the steps in the plan when on a host with the required tools.
