---
name: wiki-bootstrap
description: Use when the user asks to create or start a new wiki, knowledge base, or when wiki detection finds no existing wiki
---

# Wiki Bootstrap

Initialize a new LLM-maintained wiki from scratch or from the llm-wiki template.

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

Use the [llm-wiki CLAUDE.md](https://github.com/pbonh/llm-wiki/blob/main/CLAUDE.md) as a template. Customize placeholders if the user provides domain-specific information. Ask the user: "What domain is this knowledge base for? (e.g., 'machine learning research', 'competitive SaaS landscape')"

### 4. Write core wiki files

Create these files using the llm-wiki template as the source of truth:

- **wiki/index.md** — Master catalog with empty tables for Concepts, Entities, Summaries, Syntheses, and a Statistics section. All counts start at 0. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/index.md
- **wiki/log.md** — Append-only activity log. Start with a "Setup" entry recording the initialization. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/log.md
- **wiki/dashboard.md** — Obsidian Dataview queries for low-confidence pages, recently updated, orphans. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/dashboard.md
- **wiki/analytics.md** — Obsidian ChartsView visualizations (pie, bar, wordcloud). All values start at 0 with placeholder tags. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/analytics.md
- **wiki/flashcards.md** — Spaced repetition card deck. Start with 3 starter flashcards explaining ingest, confidence levels, and lint operations. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/flashcards.md
- **wiki/journal/template.md** — Journal entry template with Setup, Process, Result, reflection sections. Full template at: https://github.com/pbonh/llm-wiki/blob/main/wiki/journal/template.md

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

## Bootstrapping from Existing Template

If the user wants to clone the llm-wiki template instead:

```bash
git clone https://github.com/pbonh/llm-wiki.git .
rm -rf .git
git init
git add -A
git commit -m "chore: initialize wiki from llm-wiki template"
```

Then customize AGENTS.md with the user's domain.

## Tool Requirements

Requires `terminal` and `file` toolsets. If unavailable, report: "Cannot bootstrap wiki — need terminal and file access."