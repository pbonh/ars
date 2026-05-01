---
name: wiki-ingest
description: Use when the user says "ingest", adds files to raw/, or after wiki-collect has gathered sources — reads raw sources and creates/updates wiki pages
---

# Wiki Ingest

Read raw source documents and populate the wiki with structured pages. This is the core engine of the wiki system.

**REQUIRED REFERENCE:** `references/page-formats.md` — detailed format specs for each page type.

## Pre-requisites

Wiki must exist (bootstrap). At least one source file must exist in `raw/`.

## Ingest Workflow

Execute these steps for each unprocessed source in `raw/`:

### 1. Read the source completely

Load the full content of the raw source file. For large files, use progressive reading.

### 2. Create summary page

Create `wiki/summaries/<source-slug>.md` where `<source-slug>` is derived from the filename (lowercase, hyphens). Use the Summary page format from `references/page-formats.md`.

The summary must capture: all key claims, concrete examples, named concepts, named entities, and any quantitative claims or data.

### 3. Identify concepts and entities

Scan the source for:
- **Concepts**: abstract ideas, strategies, frameworks, methods, principles, theories
- **Entities**: people, tools, organizations, products, platforms, named things

For each concept/entity discovered:

- If a page already exists in `wiki/concepts/<slug>.md` or `wiki/entities/<slug>.md`: UPDATE it with new information from this source. Add the source to the `sources` array. If new information contradicts existing claims, flag it (see Step 6).
- If no page exists: CREATE it using the Concept or Entity page format from `references/page-formats.md`.

### 4. Cross-link bidirectionally

After creating/updating all pages:
- Add `[[wiki links]]` from the summary to each concept/entity page
- Add `[[wiki links]]` from each concept/entity to the summary
- Add `[[wiki links]]` between related concepts and related entities
- Every new page must link to at least one other page (no orphans)

### 5. Update index

Update `wiki/index.md`:
- Add new entries to the Concepts, Entities, Summaries tables
- Update the Statistics section with current counts

### 6. Check for contradictions

Compare new claims against existing wiki content. If a contradiction is found:
- Note it in the relevant page with a `> ⚠️` blockquote
- Lower the confidence level on the disputed claim
- Log the contradiction in `wiki/log.md`

### 7. Append to log

Add entry to `wiki/log.md`:

```markdown
### YYYY-MM-DD HH:MM — Ingest: <source-filename>

- **Source**: raw/<source-filename>
- **Pages created**: [[summaries/<slug>]], [[concepts/<slug>]], ...
- **Pages updated**: [[concepts/<slug>]], ...
- **Contradictions flagged**: none | describe contradiction
- **Notes**: any decisions made
```

### 8. Report summary

After processing, report:

```
Ingest complete: <source-filename>
- Summary: [[summaries/<slug>]]
- New concepts: X (list them)
- Updated concepts: Y (list them)
- New entities: X (list them)
- Updated entities: Y (list them)
- Contradictions: none | Z conflicts flagged
```

## Rules

- Never modify files in `raw/`
- One concept per page — split if a concept page gets too long
- Always update `wiki/index.md` and `wiki/log.md` after any change
- Prefer updating existing pages over creating duplicates
- All dates in ISO 8601 format: YYYY-MM-DD
- Use plain English — define jargon on first use
- Include concrete examples when the source provides them

## Tool Requirements

Requires `file` toolset. If unavailable, report: "Cannot ingest — need file access to read raw/ and write wiki/."