---
name: wiki-journal
description: Use when the user wants to log a research session, experiment, applied work, or create a journal entry — structured logs akin to a lab notebook
---

# Wiki Journal

Create and manage research session entries — structured logs tracking investigations, experiments, and applied work on wiki topics.

## Journal Workflow

### 1. Load template

Read `wiki/journal/template.md`. Use it as the structure for the new entry.

### 2. Create entry

Create `wiki/journal/YYYY-MM-DD-topic-slug.md` with these sections:

```markdown
---
title: "Journal Entry — YYYY-MM-DD: topic-slug"
type: journal
tags: [journal, topic-tag]
date: YYYY-MM-DD
concepts_used: ["concepts/slug1", "concepts/slug2"]
result: "brief outcome summary"
---

# Journal Entry — YYYY-MM-DD: topic-slug

## Setup

What were you investigating? What sources or wiki pages informed the approach?
Link to relevant pages: [[concepts/idea]], [[summaries/source]]

## Process

What steps were taken? What decisions were made and why?
Use numbered steps for clarity. Link to concept pages for methods applied.

## Result

What was the outcome? What was learned? Include concrete data if available.

## What Went Well

- Specific successes and effective approaches

## What Could Improve

- Shortcomings, mistakes, and alternative approaches for next time
```

### 3. Cross-reference

- If concepts are used (`concepts_used`), add a backlink from each concept page pointing to this journal entry
- Chain consecutive entries: if there's a previous journal entry, link to it at the bottom: `← Previous: [[journal/YYYY-MM-DD-prev-topic]]`

### 4. Update index and log

Add the entry to `wiki/index.md` (add a Journal section if one doesn't exist).
Append entry to `wiki/log.md`.

### 5. Report

```
Journal entry created: [[journal/YYYY-MM-DD-topic-slug]]
Cross-referenced: [[concepts/X]], [[concepts/Y]]
```

## Retroactive Entries

If the user wants to log a past session, reconstruct from conversation history. Ask clarifying questions:
- "What were you investigating?"
- "What approach did you take?"
- "What was the outcome?"

If the user cannot recall details, note in the entry: `> ⚠️ Reconstructed from memory on YYYY-MM-DD — details may be incomplete.`

## Tool Requirements

Requires `file` toolset. Wiki must exist with `wiki/journal/template.md`.