# Textbook Markdown Cleanup & Optional Generation

**Date:** 2026-04-29
**Scope:** `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md`, `roles/dotfiles/files/claude/commands/split-textbook{,s}.md`, `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md`, `roles/node/defaults/main/claude.yml` (argument hints only)
**Branch:** `main`
**Builds on:** `docs/superpowers/specs/2026-04-29-pdf-textbook-split-workflow-design.md`

## Goal

Two enhancements to the existing `split-textbooks` workflow:

1. **Make markdown sidecars optional**, defaulting to off. Without `--markdown`, the workflow produces only PDF slices and a manifest.
2. **Replace the current "minimal cleanup" with a real cleanup pass** when markdown is generated. Two tiers:
   - **Rules cleanup** (default whenever `--markdown` is on) — deterministic post-processing of `pdftotext` output.
   - **LLM cleanup** (`--llm-cleanup`, opt-in) — per-page reformat using rendered page images alongside raw extracted text. Especially recommended for OCR'd books, but cost-significant on long books, so it's never auto-enabled.

## Non-goals

- Auto-enabling `--llm-cleanup` on scanned PDFs. Cost surprise; user must opt in explicitly.
- Caching, streaming, or resumability of the LLM cleanup pass.
- Heading inference, table reconstruction, or figure captioning beyond what the per-page LLM pass naturally produces.
- Cross-section coherence (footnote chains, "see chapter 3" link rewriting, etc.).
- New CLI tools — `pdftoppm` is already part of `poppler` and ships with the existing package set.

## Design

### CLI surface

`/split-textbooks <directory> [--force] [--markdown] [--llm-cleanup]`
`/split-textbook <path-to-pdf> [--markdown] [--llm-cleanup]`

| Flag | Default | Effect |
|------|---------|--------|
| `--markdown` | off | Produce `.md` sidecars next to each `.pdf` slice. Without this, Step 4 is skipped entirely. |
| `--llm-cleanup` | off | Use the per-page LLM pass for cleanup. **Implies `--markdown`** — passing `--llm-cleanup` alone is treated as `--markdown --llm-cleanup`. |

`--force` semantics on `/split-textbooks` are unchanged: a book with `status: "complete"` is skipped regardless of whether the prior run included markdown. To upgrade an existing book from "PDFs only" to "PDFs + markdown", either pass `--force` to the batch or use `/split-textbook <pdf> --markdown` for one book.

`/split-textbook` always wipes prior output (per existing semantics), so flag changes take effect on the next run with no extra work.

### Manifest schema additions

Two new fields, both required as of `schema_version: 2`:

```json
{
  "schema_version": 2,
  "...": "...",
  "markdown_generated": true,
  "cleanup_method": "rules"
}
```

- `markdown_generated`: `true` when sidecars were produced this run; `false` when `--markdown` was absent.
- `cleanup_method`: `"none" | "rules" | "llm"`. `"none"` exactly when `markdown_generated: false`. `"llm"` when `--llm-cleanup` was used and the pass succeeded; `"rules"` otherwise (including LLM fallback — see below).

`failed_step` enum gains a new value: `"cleanup"` (only fires from the LLM pass; the rules pass is in-process Python-style text munging that won't fail).

`schema_version` bumps from `1` to `2`. Manifests at `schema_version: 1` are read-compatible (skip-if-done only checks `status`); they're treated as if `markdown_generated` and `cleanup_method` were absent. No migration tool — re-run with `--force` to refresh.

### Step 4 reorganization

The current Step 4 ("Extract markdown") is replaced with the following structure. Steps 0–3 and Step 5 are unchanged.

#### Step 4 — Extract markdown (only when `--markdown` is set)

If `--markdown` is absent, skip directly to Step 5 with `markdown_generated: false`, `cleanup_method: "none"`.

Otherwise, for each section slice:

1. Run `pdftotext -layout <slice>.pdf <slice>.raw.txt` to capture raw extracted text. Keep `.raw.txt` alongside the `.pdf` until the run completes; delete it as the final step before the manifest write.
2. Apply the cleanup pass selected by the flags:
   - `--llm-cleanup` absent → **Step 4a (rules cleanup)**.
   - `--llm-cleanup` present → **Step 4b (LLM cleanup)**.
3. Write the result to `<slice>.md`.

#### Step 4a — Rules cleanup (default for `--markdown`)

Operates on the raw text from `pdftotext -layout`. Order matters; apply in this sequence:

1. **Split into pages.** Form-feed (`\f`) is `pdftotext`'s page boundary marker. Tokenize the text into pages on `\f`.
2. **Drop page numbers.** A line that contains only digits or only roman numerals (`^\s*[ivxlcdmIVXLCDM]+\s*$` or `^\s*\d+\s*$`) is a page number; remove it. Apply only to the first or last non-blank line of each page (avoid clobbering numbered list items in body text).
3. **Detect and strip running headers/footers.** A line is a running head if its exact text appears as the first non-blank line of ≥3 pages within the slice. Same rule for the last non-blank line (running foot). Strip on every page where it appears.
4. **De-hyphenate across line breaks.** Lines ending in `-\n` followed by a lowercase-starting word → join, dropping the hyphen. Skip if the word before the hyphen is a known compound prefix (e.g., `well-`, `co-`, `non-`, `re-`); leave those alone.
5. **Reflow paragraphs.** Within a page, consecutive non-blank lines are joined with a single space when the prior line does not end in sentence-final punctuation (`.!?:`) or a closing quote/bracket. Blank lines are preserved as paragraph breaks.
6. **Concatenate pages** with `\n\n` separators.
7. **Collapse whitespace.** Runs of 3+ blank lines collapse to 2; trailing whitespace on each line is stripped.

The rules are conservative — they will leave some artifacts (orphan column splits, broken tables) rather than risk damaging the source. The promise is "better than `pdftotext -layout` alone, never worse."

#### Step 4b — LLM cleanup (opt-in, `--llm-cleanup`)

For each section slice, in sequence:

1. **Render per-page images** into a per-slice scratch dir:
   ```bash
   mkdir -p <out>/.cleanup-tmp/<slug>
   pdftoppm -png -r 150 <slice>.pdf <out>/.cleanup-tmp/<slug>/page
   ```
   Produces `page-1.png`, `page-2.png`, … one per slice page.
2. **Extract per-page raw text** into the same scratch dir:
   ```bash
   for n in $(seq 1 <page_count>); do
     pdftotext -layout -f $n -l $n <slice>.pdf <out>/.cleanup-tmp/<slug>/page-$n.txt
   done
   ```
3. **Per-page LLM pass.** For each page N:
   - Read `page-N.png` (visual structure) and `page-N.txt` (raw text).
   - Emit cleaned markdown for that page only, following the rules in the next subsection.
   - Append to a per-slice accumulator with `\n\n` between pages.
4. **Write `<slice>.md`** from the accumulator.
5. **Remove `.cleanup-tmp/<slug>/`** after the slice's `.md` is written (page images are large; don't leave them around).
6. **Final cleanup:** when all slices complete, remove `<out>/.cleanup-tmp/` entirely.

##### Per-page LLM prompt rules (followed by Claude as it processes each page)

- **Preserve all source text exactly.** Do not paraphrase, summarize, correct grammar, expand abbreviations, or "fix" what looks like an error in the source. The raw text is the contract.
- **Reflow paragraphs** broken across lines or columns.
- **Reconstruct headings** from visual structure: larger fonts, bold, centered text → `#`/`##`/`###`. Use the relative font sizes visible in the page image.
- **Preserve code blocks, equations, and tables** as plain text using fenced code blocks or pipe tables when the structure is unambiguous; leave as plain prose otherwise.
- **Drop running headers, footers, and page numbers** (the same artifacts the rules pass strips).
- **Do not add content** that isn't on the page — no synthetic section headers, no inferred "see also" links, no bracketed `[figure]` placeholders.

##### LLM pass failure → graceful fallback

If the LLM pass fails for a section (e.g., a page image is unreadable, context exhausted, tool error), do not abort the section. Instead:

1. Discard whatever the LLM produced for that section.
2. Run the rules pass (Step 4a) on the slice's raw text.
3. Write `<slice>.md` from the rules pass output.
4. In the manifest, leave `cleanup_method: "rules"` for the whole book and add a per-section `cleanup_fallback: { reason: "<short string>", section_index: N }` to a new top-level `cleanup_fallbacks: []` array.

This means a partial failure on one section doesn't prevent the book from being marked `complete` — but the manifest records what happened so the user can decide whether to retry.

If the LLM pass fails before any sections complete (e.g., `pdftoppm` is missing), the book fails with `failed_step: "cleanup"` and `cleanup_method: "none"`. No partial markdown is left behind for that book.

### Failure handling additions

| Failure | Detected at | Behavior |
|---|---|---|
| `pdftoppm` non-zero (LLM path) | Start of Step 4b for a section | If first section: `failed_step: "cleanup"`, no markdown written. If a later section: per-section fallback to rules; recorded in `cleanup_fallbacks`. |
| LLM pass exhausts context per page | During Step 4b | Per-section fallback to rules; recorded in `cleanup_fallbacks` with `reason: "context_exhausted"`. |
| `pdftotext -f N -l N` non-zero | Step 4b page-text extraction | Per-section fallback to rules. |
| Rules cleanup itself fails | Never expected | If it does, `failed_step: "extract"` (matches existing extract-failure behavior). |

The `--markdown`-absent path inherits the existing failure modes unchanged.

### Tooling impact

`pdftoppm` is shipped by `poppler` and was already added to `dev_packages` in the original plan (Task 9). The Step 0 self-check in the SKILL is extended to include `pdftoppm` so a missing binary surfaces before Step 4b runs:

```bash
command -v pdfinfo pdftotext pdffonts pdftoppm qpdf ocrmypdf
```

No new packages, no Brewfile changes, no `dev_packages` changes.

### Argument hint updates

`roles/node/defaults/main/claude.yml`:

- `argument_hint: "<directory> [--force]"` → `"<directory> [--force] [--markdown] [--llm-cleanup]"`
- `argument_hint: "<path-to-pdf>"` → `"<path-to-pdf> [--markdown] [--llm-cleanup]"`

No other Ansible plumbing changes — the existing `command.md.j2` template, the existing tasks block, and the existing defaults all carry through unchanged.

### Backward compatibility

- **Existing manifests at `schema_version: 1`** — `/split-textbooks` skip-if-done only reads `status`, so they continue to be skipped on rerun. Reading them won't crash anything.
- **Existing fixtures and SKILL.md tests** — the rules cleanup is a strict superset of the old "minimal cleanup" (form-feed strip + 3+ blank line collapse are both still applied at step 7). No fixture should produce qualitatively worse markdown.
- **Existing slash command argument hints** — adding flags to the hint is a documentation update; the slash commands accept extra arguments today.

## Testing

### Smoke test additions

Three new manual scenarios on the existing fixtures:

1. **`/split-textbooks <fixtures>` (no flags)** — confirm output dirs contain only `*.pdf` slices and `manifest.json`. No `*.md` files. Manifest reports `markdown_generated: false`, `cleanup_method: "none"`.
2. **`/split-textbooks <fixtures> --markdown`** — confirm `*.md` sidecars present. Manifest reports `markdown_generated: true`, `cleanup_method: "rules"`. Spot-check that page numbers and running headers (where present in fixtures) have been stripped.
3. **`/split-textbook <fixtures>/scanned.pdf --llm-cleanup`** — confirm `scanned/.cleanup-tmp/` is gone after the run, `scanned.ocr.pdf` exists, and the markdown sidecars look visibly cleaner than the rules-only output (paragraphs reflowed, headings present). Manifest reports `cleanup_method: "llm"`.

The fixtures themselves do not change; only the recipe and command bodies do.

### Skip-if-done sanity

Run `/split-textbooks <fixtures>` (no flags), then run `/split-textbooks <fixtures> --markdown` and confirm books are skipped (their prior run is `complete`). Then `/split-textbooks <fixtures> --markdown --force` should regenerate with markdown.

This is the documented escape valve for upgrading existing output, so verifying it works ratifies the design choice.

## Implementation order (non-binding hint)

1. Update `SKILL.md` with the Step 4 reorganization (4a + 4b), Step 0 binary list, manifest schema bump, and new failure rows.
2. Update `/split-textbooks` command body to parse `--markdown` / `--llm-cleanup` and pass them through to the skill.
3. Update `/split-textbook` command body for the same flags.
4. Update `roles/node/defaults/main/claude.yml` argument hints.
5. Update `fixtures/README.md` "Expected output" rows to mention the new flags and what changes per fixture.
6. Manual smoke run on fixtures (the three scenarios above plus skip-if-done sanity).
