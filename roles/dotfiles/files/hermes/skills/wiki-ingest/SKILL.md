---
name: wiki-ingest
description: Use when the user says "ingest", adds files to raw/, or after wiki-collect has gathered sources — reads raw sources and creates/updates wiki pages. Prefers mdBook output from ingest-pipeline / pdf-to-mdbook when available, falls back to raw PDF/markdown/text otherwise.
---

# Wiki Ingest

Read raw source documents and populate the wiki with structured pages. This is the core engine of the wiki system.

**REQUIRED REFERENCE:** `references/page-formats.md` — detailed format specs for each page type.

## Pre-requisites

Wiki must exist (bootstrap). At least one source file must exist in `raw/`.

## Output mode — you write fragments, NOT canonical pages

This skill writes per-`(concept, book, chapter)` fragments under
`wiki/.fragments/...`. The canonical pages — `wiki/concepts/<slug>.md`,
`wiki/entities/<slug>.md`, `wiki/index.md`, `wiki/log.md` — are owned by
the `wiki-merge` skill and are **off-limits from here**.

The only canonical wiki path you may write is the per-source summary at
`wiki/summaries/<slug>.md`, which is per-book-private and never collides
across books.

### Hard rules under this mode

1. **Never read** `wiki/concepts/`, `wiki/entities/`, `wiki/index.md`, or
   `wiki/log.md`. You don't know what's in them, and you don't need to.
   Decoupling reads from writes is what makes parallel ingest correct: N
   workers running concurrently never observe each other's in-flight
   state, only their own fragments.
2. **Never edit** any file under `wiki/concepts/`, `wiki/entities/`,
   `wiki/index.md`, or `wiki/log.md`. The merger owns those.
3. **Always emit** one concept fragment per `(concept-slug, book-slug,
   chapter)` you discover, one entity fragment per `(entity-slug,
   book-slug, chapter)`, exactly one index-delta JSON per chapter, and
   exactly one log-fragment per chapter.
4. The "Files touched:" line you emit at the end (read by the
   orchestrator's scoped-lint pass) lists the **fragment paths** you
   wrote, not canonical paths.

### What's lost vs the old serial mode

You lose the ability to "look at the existing concept page and extend
it." That's deliberate — competing definitions across books are
reconciled by the merger when it sees all fragments for a concept at
once. In exchange you get a workflow that's safe to run in parallel
across books with no coordination.

You also lose Step 6's old behavior of comparing new claims against
existing wiki content. Cross-source contradictions are now flagged at
merge time (when the merger sees two conflicting fragments) and at lint
time. *Within-source* contradictions (the source itself is internally
inconsistent) you should still flag — see Step 6 below.

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

### Step 3 — Emit concept and entity fragments

Scan each chapter (or the source as a whole, for fallback modes) for:
- **Concepts**: abstract ideas, strategies, frameworks, methods, principles, theories
- **Entities**: people, tools, organizations, products, platforms, named things

For each concept/entity discovered, write **exactly one fragment file**:

- Concepts: `wiki/.fragments/concepts/<concept-slug>/<book-slug>__<flat-chapter-rel>.md`
- Entities: `wiki/.fragments/entities/<entity-slug>/<book-slug>__<flat-chapter-rel>.md`

Where:
- `<concept-slug>` / `<entity-slug>` is the lowercase-hyphenated canonical name (same scheme as canonical filenames).
- `<book-slug>` is the triage record's `slug` field (per-source).
- `<flat-chapter-rel>` is the chapter's `rel_path` with `/` → `__` and the trailing `.md` stripped (e.g., `src/6-generalized-two-graph-theory.md` → `src__6-generalized-two-graph-theory`). For non-mdbook sources where there's no chapter, use the literal `whole-source` (e.g., `book-slug__whole-source.md`).

Create the parent directory (`mkdir -p`) if it doesn't exist.

**Always create — never read existing canonical pages, never check for collision.** Two different chapters of the same book that both discuss "Python" each write their own fragment under different filenames; the merger combines them. Two different books that both introduce "Python" each write their own fragment under different filenames; the merger combines them.

**Fragment file format (concept):**

```yaml
---
fragment_type: concept
concept_slug: <slug>
canonical_title: "<Display Title>"
source_book: <book-slug>
source_chapter_title: "<chapter title from triage>"     # mdbook only; "" otherwise
source_chapter_path: <chapter rel_path>                  # mdbook only; "" otherwise
created_at: <ISO 8601 UTC, e.g. 2026-05-09T18:45:03Z>
confidence: high | medium | low
mentions:                          # other concepts/entities this fragment names
  - {concept: <slug>}
  - {entity: <slug>}
backlinks:                         # canonical wiki paths the merger should backlink from this concept page
  - summaries/<book-slug>.md       # always include the summary
  - summaries/<book-slug>.md#<chapter-anchor>   # mdbook only
internal_contradiction: false      # true iff the source itself is inconsistent on this concept
---

## Definition (per <book-slug>, ch. <chapter title or "whole source">)

<one paragraph in plain English; define jargon on first use>

## How It Works (in this source)

<mechanics, process, structure as described in this chapter>

## Notable claims in this chapter

- <bullet>
- <bullet>

## Examples (this source)

<concrete examples from the chapter, if any>
```

**Entity fragment** uses the same envelope but `fragment_type: entity` and an "Overview" / "Characteristics (this source)" body matching the Entity page format in `references/page-formats.md` — adapted for "this source's view of the entity" rather than canonical.

For mdBook sources, the chapter title comes from the `chapters[i].title` field; the anchor is the heading slug as written in the chapter `.md`.

### Step 4 — Backlinks (in fragment frontmatter only)

Do **not** edit any canonical page to add `[[links]]`. Instead, populate the fragment's `backlinks:` list with the wiki-relative paths the merger should add as inbound links on the canonical concept/entity page. At minimum every fragment lists `summaries/<book-slug>.md`; mdBook fragments also list `summaries/<book-slug>.md#<chapter-anchor>`.

The merger materializes these backlinks in the canonical pages' `## Sources` and `## Related Concepts` sections at merge time. Cross-concept links between fragments of *different* concepts are deferred to lint.

The summary page (`wiki/summaries/<slug>.md`) is yours to write — embed `[[concepts/<slug>]]` and `[[entities/<slug>]]` links freely; the merger creates the canonical concept/entity pages even if they don't exist yet, so the links resolve after the next merge tick.

### Step 5 — Emit an index delta (JSON)

Write **one** JSON file per chapter:

```
wiki/.fragments/index/<book-slug>__<flat-chapter-rel>.json
```

Schema:

```json
{
  "book":             "<book-slug>",
  "chapter_rel":      "<chapter rel_path>",
  "chapter_title":    "<chapter title>",
  "concepts_added":   ["<slug>", "<slug>"],
  "concepts_updated": ["<slug>"],
  "entities_added":   ["<slug>"],
  "entities_updated": [],
  "summary_anchor":   "<chapter heading slug in the summary>"
}
```

For non-mdbook sources, `chapter_rel: "-"` and `chapter_title: "(whole source)"`.

The merger uses this file as a hint for fast statistics updates, but always re-derives the authoritative count from a filesystem scan. It's cheap to be slightly wrong here.

### Step 6 — Internal contradictions

Cross-source contradictions are not your job (you can't read canonical state). What you *can* detect: the chapter you just read contradicts itself, or contradicts another chapter of the same book.

If you see one, do two things in the relevant fragment:
- Set `confidence: low` (or `medium` if the contradiction is minor).
- Set `internal_contradiction: true` in the frontmatter.
- Optionally include a `> ⚠️ Internal contradiction: ...` blockquote in the fragment body.

The merger surfaces these when consolidating; lint sweeps confirm.

### Step 7 — Emit a log fragment

Write **one** log fragment per chapter:

```
wiki/.fragments/log/<ISO-8601-UTC>__<book-slug>__<flat-chapter-rel>.md
```

The filename's leading ISO-8601 timestamp must use the `YYYYMMDDTHHMMSSZ` compact form (no colons or dashes inside the time portion if you prefer — only the leading lexicographic-sort property matters; use one form consistently). Example: `20260509T184503Z__vlsi-symbolic__src__6-generalized-two-graph-theory.md`.

Body is a single markdown bullet (one fragment = one log line):

```markdown
- 2026-05-09T18:45:03Z — <book-slug> — ch. <chapter title> — <N> concepts, <M> entities — confidence: <high|medium|low>[ — internal_contradiction]
```

The merger appends these in lexicographic-sorted-filename order (= chronological order) to `wiki/log.md`.

### Step 8 — Report summary and "Files touched:"

After processing, report:

```
Ingest complete: <source-filename> (kind: <mdbook|markdown|text|pdf>)
- Summary: wiki/summaries/<slug>.md
- Source: <mdbook_root or raw path>
- Chapters: <N>            # only for mdbook
- Concept fragments emitted: X (list slugs)
- Entity fragments emitted: Y (list slugs)
- Internal contradictions: none | Z flagged in fragments
```

Then on a final, separate line, emit:

```
Files touched: <comma-separated list of every wiki/* path you wrote this turn>
```

The orchestrator's scoped-lint pass parses this line. List the summary
file, every fragment file, and the index-delta JSON. Do **not** list any
canonical concept/entity/index/log path — you didn't touch those.

## Rules

- Never modify files in `raw/` — including the mdBook outputs that live
  inside `raw/`. The mdBook is read-only from this skill's perspective;
  if it needs to be regenerated, that is `ingest-pipeline`'s job.
- Never read or write the canonical wiki pages owned by `wiki-merge`:
  `wiki/concepts/`, `wiki/entities/`, `wiki/index.md`, `wiki/log.md`.
  See "Output mode" above. The only canonical wiki path you may write is
  `wiki/summaries/<slug>.md`.
- Always prefer `kind: "mdbook"` when triage offers it. Do not fall back
  to `kind: "pdf"` for the same source on the same run.
- One concept per fragment file — exactly one fragment per
  `(concept-slug, book-slug, chapter)`. The merger handles
  consolidation across chapters and books.
- Re-ingesting the same chapter must overwrite its own fragment files
  (same paths) — that is the resumability story for parallel orchestrators.
- All dates in ISO 8601 format: `YYYY-MM-DD` for date-only fields,
  `YYYY-MM-DDTHH:MM:SSZ` (UTC) for `created_at` timestamps.
- Use plain English — define jargon on first use.
- Include concrete examples when the source provides them.

## Tool Requirements

Requires `file` toolset (read raw/ + the mdBook tree, write
`wiki/summaries/` and `wiki/.fragments/`) and `terminal` toolset (run
the triage script and `mkdir -p` fragment subdirectories). If
unavailable, report: "Cannot ingest — need file + terminal access for
triage and reading."
