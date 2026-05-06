---
name: wiki-ingest
description: Use when the user says "ingest", adds files to raw/, or after wiki-collect has gathered sources — reads raw sources and creates/updates wiki pages. Prefers mdBook output from ingest-pipeline / pdf-to-mdbook when available, falls back to raw PDF/markdown/text otherwise.
---

# Wiki Ingest

Read raw source documents and populate the wiki with structured pages. This is the core engine of the wiki system.

**REQUIRED REFERENCE:** `references/page-formats.md` — detailed format specs for each page type.

## Pre-requisites

Wiki must exist (bootstrap). At least one source file must exist in `raw/`.

## Source preference: mdBook over raw PDF

When a source has been processed by `ingest-pipeline` / `pdf-to-mdbook`, an
mdBook output exists alongside the raw PDF. **Always prefer the mdBook**:
its TOC was vetted by the structure-detection pass (bookmarks → font
analysis → vision review of rasterized TOC images), text is already
extracted/OCR'd into per-chapter `.md` files, and `book.toml` carries
verified title/authors metadata. Reading the chapters individually is
cheaper in tokens and gives chapter-anchored links you can use as
provenance for concept and entity pages.

The fallback (raw PDF, native markdown, plain text) only kicks in when no
mdBook stage has run.

## Ingest Workflow

### Step 0 — Triage all sources

Run the triage script once at the start of an ingest session:

```bash
python "$SKILL_DIR/scripts/triage_source.py" <wiki_root>
```

It walks `<wiki_root>/raw/`, classifies each entry, and prints one JSON
record per source. The `kind` field tells you exactly what to read:

| kind | meaning | what to read |
|---|---|---|
| `mdbook` | An mdBook output is available (sibling `<stem>-mdbook/` directory, or `pipeline.json` with `status:complete`). Use this. | `book.toml` (title/authors) + each chapter `.md` from the `chapters` array |
| `markdown` | Native markdown source. | The `.md` file directly |
| `text` | Plain text source. | The `.txt` file directly |
| `pdf` | PDF with no mdBook output. **Fallback path.** Recommend the user run `ingest-pipeline` first; if they decline, proceed with progressive PDF read. | The PDF, page by page |
| `mdbook-output` | This entry IS the mdBook output of a sibling PDF in `raw/`. Skip — the sibling PDF entry already references it. | (skip) |
| `other` | Unknown extension. | (skip with a warning to the user) |

Iterate over entries with `processed: false`. The `processed` flag is set
when `wiki/summaries/<slug>.md` already exists; `--force` semantics aren't
defined here — the user should delete the summary if they want to re-ingest.

### Step 1 — Read the source

Branch on `kind`:

**`kind: "mdbook"`** — the preferred path. The triage record gives you:
- `mdbook_root` — absolute path to the mdBook directory
- `title`, `authors`, `language` — from `book.toml`
- `chapters` — ordered list of `{title, path, rel_path, exists}` entries
- `missing_chapters` — chapter files referenced by SUMMARY.md but absent on
  disk (treat these as "skip with note", not "fail")

Read each chapter `.md` file individually. Do not load all chapters into a
single context blob — process them in order, accumulate notes per chapter,
and synthesize the summary from the notes. For very long books, the
chapter-at-a-time pattern keeps each turn cheap.

**`kind: "markdown"` or `"text"`** — read the file directly. Apply
progressive reading if the file is large.

**`kind: "pdf"`** (fallback) — surface this to the user with a one-line
note that no mdBook exists yet ("`<source>` has no mdBook — running
`ingest-pipeline` first will produce a cleaner ingest"). If the user
proceeds, do progressive PDF reading as before. The summary will be less
precise about chapter structure.

**`kind: "other"` or `"mdbook-output"`** — skip; do not create a summary.
Log a one-line note in the run report.

### Step 2 — Create summary page

Create `wiki/summaries/<slug>.md` (the slug field on the triage record is
authoritative). Use the Summary page format from `references/page-formats.md`.

The summary must capture: all key claims, concrete examples, named
concepts, named entities, and any quantitative claims or data.

For mdBook sources, the summary's structure should mirror the chapter
outline. Add one short paragraph per chapter, then a "Key concepts" and
"Key entities" section. Include the book title and authors verbatim from
the triage record's `title` / `authors`.

### Step 3 — Identify concepts and entities

Scan each chapter (or the source as a whole, for fallback modes) for:
- **Concepts**: abstract ideas, strategies, frameworks, methods, principles, theories
- **Entities**: people, tools, organizations, products, platforms, named things

For each concept/entity discovered:

- If a page already exists in `wiki/concepts/<slug>.md` or `wiki/entities/<slug>.md`: UPDATE it with new information from this source. Add the source to the `sources` array. If new information contradicts existing claims, flag it (see Step 6).
- If no page exists: CREATE it using the Concept or Entity page format from `references/page-formats.md`.

For mdBook sources, record the chapter where each concept/entity was first
introduced. Include it as a sub-bullet under the source citation:
`raw/calculus.pdf → Chapter "Limits"`. The chapter title comes from the
`chapters[i].title` field.

### Step 4 — Cross-link bidirectionally

After creating/updating all pages:
- Add `[[wiki links]]` from the summary to each concept/entity page
- Add `[[wiki links]]` from each concept/entity to the summary
- Add `[[wiki links]]` between related concepts and related entities
- Every new page must link to at least one other page (no orphans)

### Step 5 — Update index

Update `wiki/index.md`:
- Add new entries to the Concepts, Entities, Summaries tables
- Update the Statistics section with current counts

### Step 6 — Check for contradictions

Compare new claims against existing wiki content. If a contradiction is found:
- Note it in the relevant page with a `> ⚠️` blockquote
- Lower the confidence level on the disputed claim
- Log the contradiction in `wiki/log.md`

### Step 7 — Append to log

Add entry to `wiki/log.md`:

```markdown
### YYYY-MM-DD HH:MM — Ingest: <source-filename>

- **Source kind**: mdbook | markdown | text | pdf
- **Source path**: raw/<source-filename>
- **mdBook root**: <abs path>             # only when kind = mdbook
- **Chapters ingested**: N (titles)       # only when kind = mdbook
- **Pages created**: [[summaries/<slug>]], [[concepts/<slug>]], ...
- **Pages updated**: [[concepts/<slug>]], ...
- **Contradictions flagged**: none | describe contradiction
- **Notes**: any decisions made
```

### Step 8 — Report summary

After processing, report:

```
Ingest complete: <source-filename> (kind: <mdbook|markdown|text|pdf>)
- Summary: [[summaries/<slug>]]
- Source: <mdbook_root or raw path>
- Chapters: <N>            # only for mdbook
- New concepts: X (list them)
- Updated concepts: Y (list them)
- New entities: X (list them)
- Updated entities: Y (list them)
- Contradictions: none | Z conflicts flagged
```

## Rules

- Never modify files in `raw/` — including the mdBook outputs that live
  inside `raw/`. The mdBook is read-only from this skill's perspective;
  if it needs to be regenerated, that is `ingest-pipeline`'s job.
- Always prefer `kind: "mdbook"` when triage offers it. Do not fall back
  to `kind: "pdf"` for the same source on the same run.
- One concept per page — split if a concept page gets too long.
- Always update `wiki/index.md` and `wiki/log.md` after any change.
- Prefer updating existing pages over creating duplicates.
- All dates in ISO 8601 format: YYYY-MM-DD.
- Use plain English — define jargon on first use.
- Include concrete examples when the source provides them.

## Tool Requirements

Requires `file` toolset (read raw/ + the mdBook tree, write wiki/) and
`terminal` toolset (run the triage script). If unavailable, report:
"Cannot ingest — need file + terminal access for triage and reading."
