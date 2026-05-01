---
name: wiki-lint
description: Use when the user says "lint", "health check", "audit", or "check wiki health" — or after 3-5 ingest operations as a maintenance check
---

# Wiki Lint

Audit wiki health. Fix what can be fixed automatically, report what needs human judgment.

## Lint Workflow

### 1. Read all wiki pages

Load `wiki/index.md` for the page catalog. Read every page listed (or spot-check for large wikis, prioritizing stale/low-confidence pages).

### 2. Run checks

| Check | Detection | Auto-Fix |
|-------|-----------|----------|
| **Orphan pages** | Pages with no inbound `[[links]]` from other pages | Add natural link targets in related pages |
| **Stale pages** | `updated` date > 90 days ago AND confidence is `low` | Flag for review — add `> ⚠️ Stale: last updated YYYY-MM-DD. Consider re-ingesting sources.` |
| **Contradictions** | Two pages make conflicting claims on the same topic | No auto-fix. Lower confidence on both pages. Note conflict in both with cross-reference. |
| **Missing cross-links** | Concept mentioned in one page's text but not linked | Add `[[link]]` |
| **Dead links** | `[[link]]` pointing to non-existent page | Remove link or create stub page with `> ⚠️ Placeholder page` |
| **Incomplete sections** | Required sections with no content | Fill with `TBD — no information available from current sources` |
| **Low-confidence pages** | Pages with `confidence: low` | Flag for review. Note: "Consider adding more sources to strengthen." |
| **Index accuracy** | Index entries that don't match filesystem | Sync: add missing entries, remove dead entries |

### 3. Update statistics

After checks, update the Statistics section of `wiki/index.md`:
- Count all pages by type
- Count sources ingested (from log.md)
- Count pages by confidence level

### 4. Update dashboard and analytics

Update `wiki/dashboard.md` if Dataview queries reference stats.
Update `wiki/analytics.md` charts with current numbers:
- Page distribution pie chart data
- Confidence distribution bar chart data
- Top tags wordcloud data

### 5. Append to log

```markdown
### YYYY-MM-DD HH:MM — Lint

- **Pages checked**: X
- **Issues found**: Y
- **Auto-fixed**: Z
- **Needs attention**: list of pages needing human review
```

### 6. Report

```
Lint complete.
- X pages checked
- Y issues found
- Z auto-fixed
- N issues need human attention: [list with brief description]
```

## Suggested Frequency

Run every 3-5 ingest operations, or when the user requests it.

## Tool Requirements

Requires `file` toolset. Works with any wiki that has an index.md.