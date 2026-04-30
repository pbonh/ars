# Textbook Markdown Cleanup & Optional Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two enhancements to the existing `split-textbooks` workflow: (1) make markdown sidecar generation opt-in via `--markdown` (default off), and (2) replace the current "minimal cleanup" with a rules-based cleanup pass, plus an opt-in per-page LLM cleanup pass via `--llm-cleanup`.

**Architecture:** All changes are content-only — the recipe (`SKILL.md`) and the two slash command bodies. Ansible plumbing (`command.md.j2`, the tasks block, the role defaults schema) is untouched; only the `argument_hint` strings in `roles/node/defaults/main/claude.yml` change. No new packages — `pdftoppm` is already in `poppler`.

**Tech Stack:** Markdown skill recipe + slash command bodies, deployed via the existing `dotfiles` role templating loop. No code is executed at deploy time; the recipe is prose Claude follows at runtime via `Bash`.

**Reference spec:** `docs/superpowers/specs/2026-04-29-textbook-markdown-cleanup-design.md`

**Builds on:** `docs/superpowers/plans/2026-04-29-pdf-textbook-split-workflow.md` (already merged on `main`).

---

## File Structure

**Modified files:**

- `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md` — replace Step 4 section, add `pdftoppm` to Step 0 self-check, bump manifest `schema_version`, add `markdown_generated` / `cleanup_method` / `cleanup_fallbacks` fields, add `cleanup` to `failed_step` enum and to the failure table.
- `roles/dotfiles/files/claude/commands/split-textbooks.md` — parse `--markdown` and `--llm-cleanup`, pass through to the skill, surface them in the run summary.
- `roles/dotfiles/files/claude/commands/split-textbook.md` — parse `--markdown` and `--llm-cleanup`, pass through to the skill.
- `roles/node/defaults/main/claude.yml` — extend the two `argument_hint` strings for the new flags.
- `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md` — extend "Expected output" with what the new flags produce per fixture.

**Unchanged but referenced:**

- `roles/dotfiles/templates/claude/command.md.j2` — already supports the frontmatter we need.
- `roles/dotfiles/tasks/configure_claude_code.yml` — already deploys commands.
- `group_vars/all.yml` — `poppler` already in `dev_packages`; `pdftoppm` ships with it.

---

## Notes on the codebase that the engineer will need

- The slash commands and skill are pure Markdown — there is no code to test. Verification is fixture-based and manual (in Claude Code, after deploying the role).
- `pdftoppm -png -r 150 <pdf> <prefix>` produces `<prefix>-1.png`, `<prefix>-2.png`, … numbered from 1. 150 DPI is a reasonable default — sharp enough for OCR'd page images, small enough to keep PNGs ~150 KB each.
- `pdftotext -f N -l N <pdf> <out>.txt` extracts page N only. The `-f` (first) and `-l` (last) flags are inclusive 1-based.
- The `dotfiles` role templates these files into `~/.claude/skills/...` and `~/.claude/commands/...` at deploy time. After editing the source files, run `ansible-playbook node.yml --tags claude` (or `just install-node-packages`) to redeploy before testing.
- Existing manifests on disk (from the original feature) are at `schema_version: 1`. They will continue to be skipped on rerun via the existing `status: "complete"` check; no migration is required.
- The skill is invoked by Claude itself via `Bash`, so "Step 4b" instructions like "Claude reads page-N.png" mean the runtime Claude session reads each PNG via `Read` and emits the cleaned markdown via `Write`. There is no separate API call.

---

## Task 1: Extend SKILL.md with optional markdown + cleanup tiers

**Purpose:** Reorganize Step 4 of the recipe to (a) skip entirely when `--markdown` is absent, (b) run rules cleanup by default, (c) run per-page LLM cleanup when `--llm-cleanup` is set. Bump manifest schema. Add `pdftoppm` to the binary self-check.

**Files:**
- Modify: `roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md`

- [ ] **Step 1: Update the opening paragraph to mention the new flags**

Find the current opening paragraph:

```markdown
You are processing a single PDF textbook. The slash command driving you (`/split-textbooks` or `/split-textbook`) supplies the absolute path to one PDF and tells you whether to overwrite an existing output directory.
```

Replace with:

```markdown
You are processing a single PDF textbook. The slash command driving you (`/split-textbooks` or `/split-textbook`) supplies the absolute path to one PDF, whether to overwrite an existing output directory, and two optional flags:

- `markdown` (boolean) — when `true`, write a `.md` sidecar alongside each PDF slice. Default `false`: produce only PDF slices and the manifest.
- `llm_cleanup` (boolean) — when `true`, use the per-page LLM cleanup pass instead of the rules pass. Implies `markdown: true`. Default `false`.
```

- [ ] **Step 2: Add `pdftoppm` to the Step 0 environment self-check**

Find:

```bash
command -v pdfinfo pdftotext pdffonts qpdf ocrmypdf
```

Replace with:

```bash
command -v pdfinfo pdftotext pdffonts pdftoppm qpdf ocrmypdf
```

The install-hint lines below it (`brew install poppler qpdf ocrmypdf` and `devbox add poppler qpdf ocrmypdf`) are unchanged — `pdftoppm` ships with `poppler`.

- [ ] **Step 3: Replace Step 4 with the new structure**

Find the entire current Step 4 block — from the heading `## Step 4 — Extract markdown` through the closing line `Nothing more. The raw extracted text is the contract; for OCR'd books, quality is whatever Tesseract produced.` (inclusive).

Replace with the following:

````markdown
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
   - Read `page-N.png` via the `Read` tool — gives you the visual structure.
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
````

- [ ] **Step 4: Bump manifest schema and add the new fields**

Find the JSON example block starting `"schema_version": 1,` through the closing `}` of the example.

Replace with:

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

- [ ] **Step 5: Update field-notes block under the schema**

Find the `**Field notes:**` list. Replace the entire list with:

```markdown
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
```

- [ ] **Step 6: Add a row to the failure table for `cleanup`**

Find the failure table at the bottom of the file. Append a new row before the closing `**Guiding principle:**` line:

```markdown
| LLM cleanup fails before any section completes | Step 4b first slice | `failed_step: "cleanup"`, `cleanup_method: "none"`, `markdown_generated: false`. No partial markdown. |
| LLM cleanup fails for one section              | Step 4b mid-loop     | Per-section fallback to rules; recorded in `cleanup_fallbacks`. Book still completes.            |
```

- [ ] **Step 7: Verify the file is well-formed**

Run:

```bash
wc -l roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
grep -c '^## Step' roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
```

Expected: line count grew from ~210 to ~310; the `^## Step` count is 6 (Step 0, 1, 2, 3, 4, 5).

- [ ] **Step 8: Commit**

```bash
git add roles/dotfiles/files/claude/skills/split-textbooks/SKILL.md
git commit -m "[Claude] split-textbooks: optional markdown + cleanup tiers"
```

---

## Task 2: Update `/split-textbooks` batch command

**Purpose:** Parse `--markdown` and `--llm-cleanup` from `$ARGUMENTS` and pass them through to the skill on each book. Surface them in the per-book log and final summary.

**Files:**
- Modify: `roles/dotfiles/files/claude/commands/split-textbooks.md`

- [ ] **Step 1: Replace the `## Arguments` section**

Find:

```markdown
## Arguments

`$ARGUMENTS` is `<directory> [--force]`.

- The first non-flag argument is the directory containing PDFs.
- `--force` (optional) means re-process books whose `<book>/manifest.json` reports `status: "complete"`.
```

Replace with:

```markdown
## Arguments

`$ARGUMENTS` is `<directory> [--force] [--markdown] [--llm-cleanup]`.

- The first non-flag argument is the directory containing PDFs.
- `--force` (optional) — re-process books whose `<book>/manifest.json` reports `status: "complete"`.
- `--markdown` (optional, default off) — produce `.md` sidecars alongside each PDF slice. Without this flag, only PDF slices and the manifest are written.
- `--llm-cleanup` (optional, default off) — use the per-page LLM cleanup pass for markdown. **Implies `--markdown`** (treat `--llm-cleanup` alone as if `--markdown --llm-cleanup` were passed). Cost-significant on long books — only set when the user explicitly asked.
```

- [ ] **Step 2: Update the "What to do" step that dispatches to the skill**

Find:

```markdown
   - Otherwise, dispatch to the **`split-textbooks`** skill with the path to this PDF. The skill writes its own manifest and handles its own failures.
```

Replace with:

```markdown
   - Otherwise, dispatch to the **`split-textbooks`** skill with the path to this PDF, plus `markdown` and `llm_cleanup` booleans derived from the command-line flags (`--llm-cleanup` implies `markdown: true`). The skill writes its own manifest and handles its own failures.
```

- [ ] **Step 3: Extend the run summary**

Find the `## Constraints` heading. Just above it, find:

```markdown
4. After all PDFs are processed, print a summary:
   - Number processed, number skipped, number failed.
   - For each failed book, name the `failed_step` from its manifest.
```

Replace with:

```markdown
4. After all PDFs are processed, print a summary:
   - Number processed, number skipped, number failed.
   - The cleanup mode used for the run (`none` | `rules` | `llm`).
   - For each failed book, name the `failed_step` from its manifest.
   - If any book had non-empty `cleanup_fallbacks`, list them (book name + section index + reason) so the user knows which sections fell back from LLM to rules.
```

- [ ] **Step 4: Verify**

Run: `wc -l roles/dotfiles/files/claude/commands/split-textbooks.md`

Expected: line count grew modestly (~33 → ~40).

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/files/claude/commands/split-textbooks.md
git commit -m "[Claude] /split-textbooks: --markdown and --llm-cleanup flags"
```

---

## Task 3: Update `/split-textbook` retry command

**Purpose:** Same flag pass-through for the single-book retry.

**Files:**
- Modify: `roles/dotfiles/files/claude/commands/split-textbook.md`

- [ ] **Step 1: Replace the `## Arguments` section**

Find:

```markdown
## Arguments

`$ARGUMENTS` is `<path-to-pdf>`.

The user opted in to overwrite by invoking the retry, so do **not** prompt before deleting prior output.
```

Replace with:

```markdown
## Arguments

`$ARGUMENTS` is `<path-to-pdf> [--markdown] [--llm-cleanup]`.

- The first non-flag argument is the path to one PDF.
- `--markdown` (optional, default off) — produce `.md` sidecars alongside each PDF slice.
- `--llm-cleanup` (optional, default off) — per-page LLM cleanup. **Implies `--markdown`.**

The user opted in to overwrite by invoking the retry, so do **not** prompt before deleting prior output.
```

- [ ] **Step 2: Update the dispatch step**

Find:

```markdown
4. Dispatch to the `split-textbooks` skill on this single PDF.
```

Replace with:

```markdown
4. Dispatch to the `split-textbooks` skill on this single PDF, with `markdown` and `llm_cleanup` booleans derived from the flags (`--llm-cleanup` implies `markdown: true`).
```

- [ ] **Step 3: Update the post-run print step**

Find:

```markdown
5. Print the resulting manifest's `status` and (if failed) `failed_step` + `error_message`.
```

Replace with:

```markdown
5. Print the resulting manifest's `status`, `markdown_generated`, and `cleanup_method`. If `status: "failed"`, also print `failed_step` and `error_message`. If `cleanup_fallbacks` is non-empty, list them.
```

- [ ] **Step 4: Verify**

Run: `wc -l roles/dotfiles/files/claude/commands/split-textbook.md`

Expected: line count grew modestly.

- [ ] **Step 5: Commit**

```bash
git add roles/dotfiles/files/claude/commands/split-textbook.md
git commit -m "[Claude] /split-textbook: --markdown and --llm-cleanup flags"
```

---

## Task 4: Update argument hints in node role defaults

**Purpose:** Surface the new flags in the slash-command argument hints. This is the only Ansible-side change required.

**Files:**
- Modify: `roles/node/defaults/main/claude.yml`

- [ ] **Step 1: Update the batch command's argument hint**

Find:

```yaml
  - name: "split-textbooks"
    description: "Batch-process a directory of PDF textbooks"
    allowed_tools: "Bash,Read,Write,Glob"
    argument_hint: "<directory> [--force]"
    model: "opus"
    content_file: "claude/commands/split-textbooks.md"
```

Replace the `argument_hint` line with:

```yaml
    argument_hint: "<directory> [--force] [--markdown] [--llm-cleanup]"
```

- [ ] **Step 2: Update the retry command's argument hint**

Find:

```yaml
  - name: "split-textbook"
    description: "Reprocess a single PDF textbook (overwrites prior output)"
    allowed_tools: "Bash,Read,Write,Glob"
    argument_hint: "<path-to-pdf>"
    model: "opus"
    content_file: "claude/commands/split-textbook.md"
```

Replace the `argument_hint` line with:

```yaml
    argument_hint: "<path-to-pdf> [--markdown] [--llm-cleanup]"
```

- [ ] **Step 3: Syntax-check the node playbook**

Run:

```bash
ansible-playbook node.yml --syntax-check
```

Expected: no errors.

- [ ] **Step 4: Render-test in `--check --diff` mode**

Run:

```bash
ansible-playbook node.yml --tags claude --check --diff 2>&1 | tail -40
```

Expected: diffs for the two `~/.claude/commands/split-textbook{,s}.md` files, showing the updated `argument-hint:` lines in their frontmatter.

- [ ] **Step 5: Commit**

```bash
git add roles/node/defaults/main/claude.yml
git commit -m "[Claude] split-textbooks: extend argument hints with new flags"
```

---

## Task 5: Update fixtures README expected-output rows

**Purpose:** Tell future readers what each fixture should produce under each flag combination.

**Files:**
- Modify: `roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md`

- [ ] **Step 1: Replace the "Expected output (rough)" section**

Find the `## Expected output (rough)` heading and the bullet list under it.

Replace with:

````markdown
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
````

- [ ] **Step 2: Verify**

Run: `wc -l roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md`

Expected: line count roughly doubled.

- [ ] **Step 3: Commit**

```bash
git add roles/dotfiles/files/claude/skills/split-textbooks/fixtures/README.md
git commit -m "[Claude] split-textbooks fixtures README: document new flags"
```

---

## Task 6: End-to-end manual verification

**Purpose:** Deploy the updated assets and run the three flag combinations against the fixtures. Confirm the recipe produces what the spec promises.

- [ ] **Step 1: Deploy the updated assets**

Run:

```bash
just install-node-packages
```

Or directly: `ansible-playbook node.yml --tags claude`.

Expected: tasks complete without errors. The `Template skill files` and `Template command files` tasks should both report changes.

- [ ] **Step 2: Spot-check the deployed files**

Run:

```bash
grep -c "Step 4a\|Step 4b" ~/.claude/skills/split-textbooks/SKILL.md
head -10 ~/.claude/commands/split-textbooks.md
head -10 ~/.claude/commands/split-textbook.md
```

Expected: the `Step 4a`/`Step 4b` count is ≥4 (each appears in heading and body); the command frontmatters carry the updated `argument-hint:` strings.

- [ ] **Step 3: Run scenario 1 — no flags**

In Claude Code:

```bash
cp -r roles/dotfiles/files/claude/skills/split-textbooks/fixtures /tmp/textbooks-smoke-1
```

Then invoke `/split-textbooks /tmp/textbooks-smoke-1`.

Expected per fixture: a `<book>/` dir with `*.pdf` slices and `manifest.json` only — **no `*.md` files**. `manifest.json` reports `markdown_generated: false`, `cleanup_method: "none"`.

Verify:

```bash
find /tmp/textbooks-smoke-1 -name '*.md' ! -name 'README.md'
```

Expected: empty output (no markdown sidecars).

- [ ] **Step 4: Run scenario 2 — `--markdown`**

```bash
cp -r roles/dotfiles/files/claude/skills/split-textbooks/fixtures /tmp/textbooks-smoke-2
```

Invoke `/split-textbooks /tmp/textbooks-smoke-2 --markdown`.

Expected: same PDF slices as scenario 1, plus `*.md` sidecars. Manifests report `markdown_generated: true`, `cleanup_method: "rules"`. Open one `.md` and confirm: no isolated page-number lines, no obvious running headers, paragraphs reflowed.

- [ ] **Step 5: Run scenario 3 — `--llm-cleanup` on the scanned fixture**

```bash
cp roles/dotfiles/files/claude/skills/split-textbooks/fixtures/scanned.pdf /tmp/scanned-smoke.pdf
```

Invoke `/split-textbook /tmp/scanned-smoke.pdf --llm-cleanup`.

Expected: `/tmp/scanned-smoke/` contains slices and `.md` sidecars. `/tmp/scanned-smoke/.cleanup-tmp/` does **not** exist (cleaned up). `manifest.json` reports `cleanup_method: "llm"`. The markdown should look noticeably cleaner than scenario 2's rules-only output for the OCR'd content.

- [ ] **Step 6: Skip-if-done sanity check**

Re-run `/split-textbooks /tmp/textbooks-smoke-1 --markdown` against the *same* directory from Step 3.

Expected: every book is logged as "skip: already complete" (because `status: "complete"` was set in Step 3's run, even though that run didn't produce markdown). The user is expected to use `--force` or `/split-textbook` to upgrade.

Then run `/split-textbooks /tmp/textbooks-smoke-1 --markdown --force`.

Expected: books are reprocessed and now have `.md` sidecars; manifests report `cleanup_method: "rules"`.

- [ ] **Step 7: Clean up scratch dirs**

```bash
rm -rf /tmp/textbooks-smoke-1 /tmp/textbooks-smoke-2 /tmp/scanned-smoke /tmp/scanned-smoke.pdf
```

- [ ] **Step 8: Final commit (if any tweaks were needed)**

If Steps 3–6 surfaced bugs and you edited the recipe or commands, commit those fixes now:

```bash
git status
git add <changed-files>
git commit -m "[Claude] Fix recipe issues found during cleanup-flag smoke run"
```

If nothing changed, skip this step.

---

## Self-review notes

The plan was checked against the spec on these dimensions:

- **Spec coverage:** every numbered item in the spec's "Implementation order" hint maps to one of Tasks 1–5; Task 6 picks up the manual verification described in the spec's "Testing" section.
- **Backward compatibility:** the manifest schema bump (`1` → `2`) is read-compatible — `/split-textbooks` skip-if-done only checks `status`, which existed at `schema_version: 1`. No migration tool needed.
- **Tool footprint:** `pdftoppm` is added to the Step 0 self-check but not to `dev_packages` because it ships with `poppler` (already present). If a future host installs only a stripped-down `poppler` variant lacking `pdftoppm`, the self-check catches it before Step 4b runs.
- **Failure path symmetry:** the `cleanup` failed-step value is added to the recipe's enum, the manifest schema field-notes, AND the failure table — three places must agree on the enum.
- **Fallback semantics:** "every section fell back to rules" demotes `cleanup_method` from `"llm"` to `"rules"`, so the field always reflects what is actually on disk. `cleanup_fallbacks` carries the per-section detail.
