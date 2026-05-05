# Ingest Pipeline Test Fixtures

Each subdirectory is a fixture exercising a specific state or behavior of
`ingest-pipeline`.

| Fixture | State | Purpose |
|---------|-------|---------|
| `s0-empty/` | S0 | Empty directory; classifier must abort. |
| `s1-single-pdf/` | S1 | Single PDF; classifier dispatches to `pdf-to-mdbook`. |
| `s3-pre-split-md/` | S3 | Pre-split markdown; classifier scaffolds an mdBook inline. |
| `s4-partial-mdbook/` | S4 | `book.toml` and `src/SUMMARY.md` already present; classifier runs `mdbook build`. |
| `s5-complete/` | S5 | `pipeline.json` `status: complete` and `book-mdbook/` present; classifier returns "already complete". |
| `stale-pipeline-json/` | S1 | `pipeline.json` claims complete but no `book-mdbook/`; filesystem-truth rule reclassifies to S1. |
| `library/` | mixed | Three books for `ingest-pipeline-batch` — calculus (fresh), probability (complete), discrete-math (corrupt). |

`S2` is reserved/unused — see
`ingest-pipeline/references/state-detection.md`. The previous
`s2-pre-split-pdfs/` fixture was removed when the `split-textbooks` skill
was retired.

`pipeline.json` files contain `FIXTURE` placeholders for `book_root` and
`input_target`; the harness substitutes the real absolute path at test time so
fixtures are portable across machines.

## Regenerating PDFs

If you change a fixture spec or add a new one, regenerate the PDFs with:

```bash
./make-fixtures.sh
```

Requires `python3` with `reportlab` (`pip install reportlab`) or `pandoc`.

PDFs are committed as binaries so `run-tests.sh` does not require the
generator on every machine.
