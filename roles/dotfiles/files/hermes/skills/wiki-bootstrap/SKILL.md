---
name: wiki-bootstrap
description: Use when the user asks to create or start a new wiki, knowledge base, or when wiki detection finds no existing wiki
---

# Wiki Bootstrap

Initialize a new LLM-maintained wiki from scratch using the templates below.

## Process

### 1. Initialize git repository

If not already in a git repo:

```bash
git init
```

### 2. Scaffold directory structure

Create all required directories with `.gitkeep` files:

```bash
mkdir -p raw
mkdir -p wiki/summaries wiki/concepts wiki/entities wiki/syntheses wiki/journal wiki/presentations
touch raw/.gitkeep
touch wiki/summaries/.gitkeep wiki/concepts/.gitkeep wiki/entities/.gitkeep
touch wiki/syntheses/.gitkeep wiki/journal/.gitkeep wiki/presentations/.gitkeep
```

### 3. Generate AGENTS.md

If no `AGENTS.md` or `CLAUDE.md` exists, create a domain-agnostic schema file. If one exists, respect it — don't overwrite. The schema must contain:

```yaml
---
name: [domain-name] Knowledge Base — Schema
---
```

With sections for: Purpose, Directory Layout, File Naming, Page Format, Required Sections (by page type), Linking Conventions, Tagging Taxonomy, Confidence Levels, Workflows (Ingest, Query, Lint), and Rules.

Use the following template as a starting point. Customize placeholders if the user provides domain-specific information. Ask the user: "What domain is this knowledge base for? (e.g., 'machine learning research', 'competitive SaaS landscape')"

````markdown
---
name: [domain-name] Knowledge Base — Schema
---

# [Your Domain] Knowledge Base — Schema

## Purpose

<!-- CUSTOMIZE: Replace this with a one-paragraph description of your knowledge domain. -->
<!-- Examples: "machine learning research", "19th-century literature", "competitive landscape for SaaS tools" -->
This is an LLM-maintained knowledge base on [YOUR TOPIC]. The LLM writes and maintains all files under `wiki/`. The human curates raw sources and directs queries. The human never edits wiki files directly.

## Directory Layout

- `raw/` — Immutable source documents (transcripts, articles, notes). Never modify these.
- `wiki/index.md` — Master catalog. Every wiki page must appear here.
- `wiki/log.md` — Append-only activity log.
- `wiki/summaries/` — One summary page per raw source document.
- `wiki/concepts/` — Concept, strategy, and framework pages.
- `wiki/entities/` — Entity pages (people, tools, organizations, products — whatever "things" exist in your domain).
- `wiki/syntheses/` — Comparison tables, decision frameworks, cross-cutting analyses.
- `wiki/journal/` — Research or session journal entries.
- `wiki/presentations/` — Marp slide decks generated from wiki content.

## File Naming

- All lowercase, hyphens for word separation: `concept-name.md`
- No spaces, no special characters, no uppercase
- Name should match the page title slug

## Page Format

Every wiki page uses this frontmatter and structure:

```yaml
---
title: "Page Title"
type: concept | entity | summary | synthesis
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["raw/filename.txt"]
confidence: high | medium | low
---
```

### Required Sections by Page Type

**Summary pages** (`wiki/summaries/`):
- `## Key Points` — Bulleted list of main claims/ideas
- `## Relevant Concepts` — Links to concept pages this source touches
- `## Source Metadata` — Type of source, author/speaker, date, URL or identifier

**Concept pages** (`wiki/concepts/`):
- `## Definition` — One-paragraph plain-English definition
- `## How It Works` — Mechanics, process, or structure of the concept
- `## Key Parameters` — Important variables, dimensions, or factors
- `## When To Use` — Situations and contexts where this concept applies
- `## Risks & Pitfalls` — Known failure modes, common mistakes, limitations
- `## Related Concepts` — Wiki links to related pages
- `## Sources` — Which raw sources inform this page

**Entity pages** (`wiki/entities/`):
- `## Overview` — What this entity is
- `## Characteristics` — Key properties, attributes, structure
- `## Common Strategies` — Links to concept pages for strategies or methods associated with this entity
- `## Related Entities` — Links to related entity pages

**Synthesis pages** (`wiki/syntheses/`):
- `## Comparison` — Table or structured comparison
- `## Analysis` — Cross-cutting insights
- `## Recommendations` — When to prefer which approach
- `## Pages Compared` — Links to all pages involved

## Linking Conventions

- Use Obsidian-style wiki links: `[[concepts/concept-name]]`
- Always use relative paths from wiki root
- Every page must link to at least one other page (no orphans)
- When mentioning a concept that has a page, always link it

## Tagging Taxonomy

<!-- CUSTOMIZE: Replace these placeholder categories with tags relevant to your domain. -->
<!-- Each category should have 3-8 specific tags. -->
<!-- Example for a cooking KB: -->
<!--   Cuisine: italian, japanese, french, mexican -->
<!--   Technique: braising, fermenting, sous-vide, grilling -->
<!--   Ingredient: protein, vegetable, grain, dairy -->

- **Category-A**: `tag-1`, `tag-2`, `tag-3`
- **Category-B**: `tag-4`, `tag-5`, `tag-6`
- **Category-C**: `tag-7`, `tag-8`, `tag-9`
- **Scope**: `foundational`, `advanced`, `experimental`
- **Status**: `well-established`, `emerging`, `speculative`

## Confidence Levels

- **high** — Well-established idea, multiple corroborating sources, demonstrated with concrete examples
- **medium** — Supported by sources but limited examples or single-source
- **low** — Single mention, anecdotal, or speculative

## Workflows

### Ingest

When the user says "ingest [source]" or adds a file to `raw/`:

1. Read the raw source completely
2. Create `wiki/summaries/<source-slug>.md` with full summary
3. Identify all concepts, entities, and strategies mentioned
4. For each concept/entity: create the page if it doesn't exist, or update it with new information if it does
5. Add cross-links in both directions between all touched pages
6. Update `wiki/index.md` — add new entries, update summaries of changed pages
7. Append to `wiki/log.md` with timestamp, source name, pages created/updated
8. Flag any contradictions with existing wiki content

### Query

When the user asks a question:

1. Read `wiki/index.md` to find relevant pages
2. Read those pages
3. Synthesize an answer citing specific pages with wiki links
4. If the answer reveals new insight worth preserving:
   - Create a synthesis page in `wiki/syntheses/`
   - Update index and log

### Lint

When the user says "lint" or "health check":

1. Read all wiki pages
2. Check for: orphan pages (no inbound links), stale claims, contradictions between pages, missing cross-links, incomplete sections, low-confidence pages that could be strengthened
3. Fix what can be fixed automatically
4. Report issues that need human judgment
5. Suggest new sources or topics to investigate
6. Update log

## Rules

- Never modify files in `raw/`
- Always update `index.md` and `log.md` after any wiki change
- Prefer updating existing pages over creating duplicates
- When in doubt about a claim, set confidence to "low" and note the uncertainty
- Keep pages focused — one concept per page, split if a page gets too long
- Use plain English — define jargon on first use in each page
- All dates in ISO 8601 format: YYYY-MM-DD
- When a source provides specific examples, include them with concrete details
````

### 4. Write core wiki files

Create these files using the templates below:

- **wiki/index.md** — Master catalog with empty tables for Concepts, Entities, Summaries, Syntheses, and a Statistics section. All counts start at 0.

````markdown
---
title: "Knowledge Base Index"
type: index
updated: 2026-04-08
---

# Knowledge Base Index

Master catalog of all wiki pages. Every page in the wiki must have an entry here.

## Concepts

| Page | Tags | Confidence | Updated |
|------|------|------------|---------|
| <!-- entries added by LLM during ingest --> | | | |

## Entities

| Page | Tags | Updated |
|------|------|---------|
| <!-- entries added by LLM during ingest --> | | |

## Summaries

| Page | Source | Key Topics | Created |
|------|--------|------------|---------|
| <!-- entries added by LLM during ingest --> | | | |

## Syntheses

| Page | Pages Compared | Created |
|------|----------------|---------|
| <!-- entries added by LLM during ingest --> | | |

## Statistics

- **Total pages**: 0
- **Concepts**: 0
- **Entities**: 0
- **Summaries**: 0
- **Syntheses**: 0
- **Sources ingested**: 0
- **High confidence**: 0
- **Medium confidence**: 0
- **Low confidence**: 0
````

- **wiki/log.md** — Append-only activity log. Start with a "Setup" entry recording the initialization.

````markdown
---
title: "Activity Log"
type: log
---

# Activity Log

Append-only record of all wiki changes.

## Format

Each entry follows this format:
```
### YYYY-MM-DD HH:MM — [Action Type]
- **Source/Trigger**: what initiated the action
- **Pages created**: list of new pages
- **Pages updated**: list of updated pages
- **Notes**: any contradictions flagged, decisions made
```

---

### 2026-04-08 00:00 — Setup

- **Source/Trigger**: Repository initialized
- **Pages created**: index.md, log.md, dashboard.md, analytics.md, flashcards.md
- **Pages updated**: none
- **Notes**: Empty knowledge base ready for first source ingestion
````

- **wiki/dashboard.md** — Obsidian Dataview queries for low-confidence pages, recently updated, orphans.

````markdown
---
title: "Dashboard"
type: dashboard
tags: [meta]
updated: 2026-04-08
---

# Dashboard

Live queries powered by the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) Obsidian plugin.

## Low Confidence Pages

Pages that need more sources or evidence to strengthen.

```dataview
TABLE confidence, sources, updated
FROM "wiki/concepts" OR "wiki/entities"
WHERE confidence = "low"
SORT updated DESC
```

## All Concepts by Tag

```dataview
TABLE tags, confidence, updated
FROM "wiki/concepts"
SORT file.name ASC
```

## Recently Updated Pages

The 15 most recently modified wiki pages.

```dataview
TABLE type, tags, updated
FROM "wiki/"
SORT updated DESC
LIMIT 15
```

## Pages with Most Sources

Pages informed by the greatest number of raw sources.

```dataview
TABLE length(sources) AS "Source Count", confidence, updated
FROM "wiki/concepts" OR "wiki/entities"
WHERE sources
SORT length(sources) DESC
LIMIT 10
```

## Orphan Check

Pages that may lack inbound links (review manually — Dataview cannot check incoming links directly).

```dataview
TABLE type, tags, updated
FROM "wiki/concepts" OR "wiki/entities"
WHERE length(file.inlinks) = 0
SORT updated ASC
```

## Entity Overview

```dataview
TABLE tags, updated
FROM "wiki/entities"
SORT file.name ASC
```
````

- **wiki/analytics.md** — Obsidian ChartsView visualizations (pie, bar, wordcloud). All values start at 0 with placeholder tags.

````markdown
---
title: "Analytics"
type: dashboard
tags: [meta]
updated: 2026-04-08
---

# Analytics

Visual analytics powered by the [Charts View](https://github.com/caronchen/obsidian-chartsview-plugin) Obsidian plugin.

## Page Distribution by Type

<!-- CUSTOMIZE: Update these numbers as your wiki grows. -->
<!-- The LLM can update this page during lint operations. -->

```chartsview
type: pie
options:
  legend:
    display: true
    position: right
data:
  - label: Concepts
    value: 0
  - label: Entities
    value: 0
  - label: Summaries
    value: 0
  - label: Syntheses
    value: 0
```

## Confidence Distribution

```chartsview
type: bar
options:
  legend:
    display: false
  indexAxis: y
data:
  - label: High
    value: 0
    backgroundColor: "#4caf50"
  - label: Medium
    value: 0
    backgroundColor: "#ff9800"
  - label: Low
    value: 0
    backgroundColor: "#f44336"
```

## Top Tags

<!-- CUSTOMIZE: Replace these placeholder tags with your actual tags after ingesting sources. -->

```chartsview
type: wordcloud
options:
  maxRotation: 0
  minRotation: 0
data:
  - tag: placeholder-tag-1
    value: 1
  - tag: placeholder-tag-2
    value: 1
  - tag: placeholder-tag-3
    value: 1
```
````

- **wiki/flashcards.md** — Spaced repetition card deck. Start with 3 starter flashcards explaining ingest, confidence levels, and lint operations.

````markdown
---
title: "Flashcards"
type: flashcards
tags: [meta, flashcards]
updated: 2026-04-08
---

# Flashcards

Spaced repetition cards for the [Spaced Repetition](https://github.com/st3v3nmw/obsidian-spaced-repetition) Obsidian plugin.

## Format

Each flashcard uses this format:

```
Question text goes here
?
Answer text goes here
```

Separate cards with blank lines. The `?` on its own line separates question from answer.

Ask the LLM to generate flashcards from any wiki page:
```
Generate flashcards from [[concepts/concept-name]]
```

---

## Cards

What is the purpose of the "ingest" workflow?
?
The ingest workflow reads a raw source document, creates a summary page, identifies and creates/updates concept and entity pages, adds cross-links between all touched pages, and updates the index and log.

What are the three confidence levels and when is each used?
?
**High** — well-established idea with multiple corroborating sources and concrete examples. **Medium** — supported by sources but limited examples or single-source. **Low** — single mention, anecdotal, or speculative.

What does the "lint" operation check for?
?
Orphan pages (no inbound links), stale claims, contradictions between pages, missing cross-links, incomplete sections, and low-confidence pages that could be strengthened.
````

- **wiki/journal/template.md** — Journal entry template with Setup, Process, Result, reflection sections.

````markdown
---
title: "Journal Entry — YYYY-MM-DD"
type: journal
tags: [journal]
date: YYYY-MM-DD
concepts_used: []
result: ""
---

# Journal Entry — YYYY-MM-DD

## Setup

<!-- What were you investigating, researching, or working on? -->
<!-- What sources or wiki pages informed your approach? -->

## Process

<!-- What steps did you take? What decisions did you make and why? -->
<!-- Link to relevant concept pages: [[concepts/concept-name]] -->

## Result

<!-- What was the outcome? What did you learn? -->

## What Went Well

- 

## What Could Improve

- 
````

### 5. Create .gitignore

```gitignore
.obsidian/
node_modules/
.DS_Store
Thumbs.db
```

### 6. Initial commit

```bash
git add -A
git commit -m "chore: initialize wiki structure"
```

### 7. Report

Summarize what was created:

```
Wiki initialized. Created:
- raw/ (immutable source directory)
- wiki/ (summaries, concepts, entities, syntheses, journal, presentations)
- AGENTS.md (domain schema)
- Core pages: index.md, log.md, dashboard.md, analytics.md, flashcards.md

Next steps: collect sources (wiki-collect), then ingest them (wiki-ingest).
```

## Tool Requirements

Requires `terminal` and `file` toolsets. If unavailable, report: "Cannot bootstrap wiki — need terminal and file access."
