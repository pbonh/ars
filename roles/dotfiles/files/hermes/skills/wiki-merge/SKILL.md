---
name: wiki-merge
description: Use after wiki-ingest has emitted fragments under wiki/.fragments/ — consolidates per-(concept, book, chapter) fragments into the canonical wiki pages (wiki/concepts/, wiki/entities/, wiki/index.md, wiki/log.md). Idempotent and crash-safe. The orchestrator wraps this in flock so only one merger runs at a time.
---

# Wiki Merge

Consolidate the staging area at `wiki/.fragments/` into the canonical
wiki pages. This skill is the **single writer** of:

- `wiki/concepts/<slug>.md`
- `wiki/entities/<slug>.md`
- `wiki/index.md`
- `wiki/log.md`

`wiki-ingest` (under fragment mode) is the **only** producer of inputs in
`wiki/.fragments/`. Lint and other skills are read-only against
`wiki/.fragments/`.

**REQUIRED REFERENCE:** `../wiki-ingest/references/page-formats.md` —
canonical page format you must produce when merging.

## When to run

The orchestrator calls this skill in three contexts:

1. **Periodic tick** — every `--merge-interval` (default 10 min) during
   a parallel ingest run, while workers continue producing fragments.
2. **End-of-batch** — once after all parallel workers finish, to drain
   any remaining fragments before the final lint sweep.
3. **On-demand** — the user runs `hermes -s wiki-merge` to flush manually.

You should not need to know which context you were called in. Behave
identically: triage, merge what's there, exit.

## Concurrency contract (flock)

The orchestrator wraps every call to this skill in `flock -x` on
`<wiki_root>/wiki/.merge.lock`. You assume that lock is already held
when you start. **You do not acquire the lock yourself.** If you
discover the lock is unheld (e.g., the user ran the skill manually), do
your best work anyway — fragments are written atomically by ingest, so
"merger sees an in-flight fragment" is not possible by construction
(ingest writes via tmp + rename when it can; otherwise an in-progress
fragment looks identical to a complete one because they're written by a
single Write call).

## Pre-requisites

- A wiki root containing `wiki/` and (if anything is to merge)
  `wiki/.fragments/`.
- Python 3 on PATH (for the helper scripts).

## Workflow

### Step 1 — Triage the fragment tree

Run the triage script:

```bash
python "$SKILL_DIR/scripts/triage_fragments.py" <wiki_root> --summary
```

Output is JSONL on stdout, one record per merge unit. Records appear in
this order: all concept records (sorted by slug), all entity records
(sorted by slug), then at most one log record, then at most one index
record. The `--summary` flag prints aggregate counts to stderr.

Empty stdout means nothing to merge. **If the plan is empty, jump
straight to Step 5 (rebuild index) — `wiki/concepts/`, `wiki/entities/`,
and `wiki/summaries/` may have changed even with no fragments,** for
example when a previous merger died after moving fragments but before
rebuilding the index. Then exit.

### Step 2 — Merge each concept

For each `kind: "concept"` record from triage:

```json
{
  "kind": "concept",
  "slug": "two-graph-method",
  "fragment_paths": ["wiki/.fragments/concepts/two-graph-method/<file>.md", ...],
  "canonical_path":  "wiki/concepts/two-graph-method.md",
  "canonical_exists": true|false,
  "fragment_count":   N
}
```

Do this:

1. **Read** every fragment in `fragment_paths`.
2. **Read** the canonical page at `canonical_path` if `canonical_exists`
   is true. Otherwise treat it as new.
3. **Synthesize** a merged canonical page. See "Concept merge rules"
   below — the prose-merge part is the whole point of this skill, do
   not skip it.
4. **Write** the merged page to `canonical_path`. Use Write — the
   filesystem rename it does is atomic. The canonical page must conform
   to the Concept page format in
   `../wiki-ingest/references/page-formats.md`. Update the `updated:`
   frontmatter field to today's date in `YYYY-MM-DD`.
5. **Archive consumed fragments**:

   ```bash
   python "$SKILL_DIR/scripts/archive_fragments.py" <wiki_root> --paths <each fragment_path>
   ```

   Pass them all in one command; the script handles many at once. This
   moves the files to `wiki/.fragments/.merged/concepts/<slug>/...`.

Do concepts one at a time, in the order triage emitted. Don't try to
parallelize within a single merger run — you're already serialized by
flock at the orchestrator level.

### Step 3 — Merge each entity

Identical to Step 2, with `kind: "entity"`, canonical path under
`wiki/entities/`, and the Entity page format. See "Entity merge rules"
below for the small format differences.

### Step 4 — Append the log batch

If the plan contained a `kind: "log"` record:

1. Read each `fragment_path` (each is a single markdown bullet line).
   They are already sorted in chronological order (by ISO-8601 timestamp
   in their filenames).
2. Append the lines verbatim to the end of `wiki/log.md`. If `log.md`
   doesn't exist, create it using the wiki-bootstrap log header, then
   append. Don't insert blank lines between fragments — they're already
   self-contained bullets.
3. Archive the consumed fragments via `archive_fragments.py`.

If the user has put a `## Format` or other static section in `log.md`,
preserve it; only append after the existing content.

### Step 5 — Rebuild the index

Run:

```bash
python "$SKILL_DIR/scripts/rebuild_index.py" <wiki_root>
```

This regenerates the Concepts, Entities, Summaries tables and the
Statistics section of `wiki/index.md` from a filesystem scan of
`wiki/concepts/`, `wiki/entities/`, `wiki/summaries/`. Other sections
(frontmatter, hand-written prose, the Syntheses table) are preserved.

The index-delta JSONs in the plan are advisory only — the rebuild is
authoritative because filesystem state is the ground truth. After
rebuild, archive the consumed deltas via `archive_fragments.py` if a
`kind: "index"` record was present.

### Step 6 — Report

Emit a final block of the form:

```
Merge complete.
- Concepts merged:   N (slugs: ...)
- Entities merged:   M (slugs: ...)
- Log lines appended: K
- Index deltas applied: P
- Orphan fragments left: 0     # report >0 if any path failed
- Lock: <held by orchestrator | manual>
```

Then on a final, separate line, list the canonical files you wrote so a
scoped lint can pick them up:

```
Files touched: wiki/concepts/<slug>.md, wiki/entities/<slug>.md, wiki/log.md, wiki/index.md
```

## Concept merge rules

This is the prose-merge part. When you have N fragments for one concept
plus possibly a pre-existing canonical page, produce **one** canonical
page that:

1. **Has a single canonical Definition section.** Each fragment carries
   its own "Definition (per source X, ch. Y)" section. Pick the most
   general, plain-English wording. If the sources genuinely disagree,
   open the Definition with the agreed-on parts and add a `## Variants`
   subsection (or `## Definitions across sources` if the variation is
   substantive) listing each source's view in turn. Do not silently
   pick one and drop the others.

2. **Unions the "How It Works", "Key Parameters", "When To Use",
   "Risks & Pitfalls" sections** across fragments, deduplicating
   identical-or-near-identical bullets and keeping per-source nuance.
   When a bullet only appears in one source and isn't corroborated, keep
   it but add a parenthetical citation: `(per [[summaries/<book-slug>]])`.

3. **`## Sources` aggregates** every source citation from every
   fragment plus any prior canonical-page citations. Format each as
   `[[summaries/<book-slug>]] — ch. <chapter title>` (or just
   `[[summaries/<book-slug>]]` for non-mdbook sources). Sort by source
   slug for stability across runs.

4. **`## Related Concepts`** unions:
   - The `mentions:` lists in every fragment's frontmatter.
   - Any `[[concepts/<slug>]]` or `[[entities/<slug>]]` already linked from
     the prior canonical page's body.
   Sort and deduplicate. Render as wiki links: `- [[concepts/<slug>]]`,
   one per line. Do NOT verify that the linked target exists — the next
   merge tick or a lint sweep handles dead links.

5. **Backlinks materialization**: the fragment frontmatter's
   `backlinks:` list names canonical paths that should link *to* this
   concept page. You don't need to edit the source pages — the lint pass
   does cross-graph integrity. Just make sure your `## Sources` section
   lists every backlink target that's a summary page, so no source is
   silently dropped.

6. **Confidence**: take the **highest** confidence across fragments and
   the prior canonical, with a one-step downgrade rule:
   - If two fragments contradict each other on the same claim
     (`internal_contradiction: true` or you observe a substantive
     disagreement during merge), downgrade by one level (high → medium,
     medium → low, low → low) and add a `> ⚠️ Sources disagree on X`
     blockquote at the relevant point in the body.
   - Otherwise the result is the max of the input confidences.

7. **Frontmatter**: produce valid frontmatter conforming to
   `page-formats.md`:
   ```yaml
   ---
   title: "<canonical_title from fragments — pick the best display form>"
   type: concept
   tags: [<union of tags from fragments and prior canonical, deduped>]
   created: <earliest created_at across fragments and prior, as YYYY-MM-DD>
   updated: <today, YYYY-MM-DD>
   sources: [<union of summary slugs as raw/<filename> if known, else summaries/<slug>>]
   confidence: <high|medium|low>
   ---
   ```
   The `sources` array uses the `raw/` form when the underlying source
   path is recoverable from the fragment's `source_book` field (i.e.,
   `raw/<book-slug>.pdf` or whatever format the wiki uses); when in
   doubt, use `summaries/<book-slug>.md` (canonical wiki path).

8. **Never read** any other concept or entity canonical page during
   this merge. Each canonical page is consolidated independently. The
   merger doesn't second-guess existing cross-links — lint does.

## Entity merge rules

Same as concept rules, with two adjustments:

- Required sections are `## Overview`, `## Characteristics`,
  `## Common Strategies`, `## Related Entities` (per the Entity page
  format). Map fragment content to those sections.
- `## Common Strategies` cross-links to *concept* pages, not other
  entities. Use the fragment's `mentions: [{concept: <slug>}]` entries
  for this.

## Idempotency and crash recovery

- Re-running this skill on a wiki with no fragments is a no-op past
  Step 5 (the index rebuild is always safe to run).
- If a previous merger died after writing a canonical page but before
  archiving the fragments, the next run sees the fragments again,
  re-merges them with the now-current canonical (which already includes
  their content), and produces an equivalent canonical. Some textual
  drift is possible if the LLM rewords; that's acceptable. The
  canonical never loses content this way.
- If a previous merger died after archiving fragments but before
  rebuilding the index, the next run still rebuilds the index — that's
  why Step 5 always runs.

## Rules

- Single writer of canonical concept/entity/index/log paths. No other
  skill writes there.
- Always update `created:` (don't change once set; carry forward) and
  `updated:` (set to today) frontmatter fields when writing canonical
  pages.
- Never read or modify `raw/` or any path outside `wiki/`.
- Never invoke `wiki-ingest` from this skill.
- All dates in ISO 8601 format: `YYYY-MM-DD` for date-only,
  `YYYY-MM-DDTHH:MM:SSZ` for timestamps.

## Tool Requirements

Requires the `file` toolset (read/write `wiki/`) and `terminal` toolset
(run `python` for the helper scripts and `flock` is supplied by the
orchestrator wrapper). If unavailable, report: "Cannot merge — need
file + terminal access."
