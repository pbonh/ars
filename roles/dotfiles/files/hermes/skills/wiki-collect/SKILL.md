---
name: wiki-collect
description: Use when the user asks to collect articles, fetch content, save sources, or add reference material to the wiki
---

# Wiki Collect

Gather source documents into `raw/` using Hermes' native web tools or by accepting user-provided content.

## Collection Methods

### Method 1: Web Collection (active)

Use Hermes' `web_search` and `web_fetch` tools to find and retrieve sources:

1. **Search**: Use `web_search` to find relevant articles, papers, or pages
2. **Fetch**: Use `web_fetch` to extract the full content of each promising result
3. **Save**: Write the extracted content to `raw/<descriptive-slug>.txt`

### Method 2: User-Provided Content (passive)

The user may paste content directly or specify files. Save these to `raw/` with descriptive names.

## File Naming

Use descriptive, lowercase-hyphenated filenames:
- `attention-is-all-you-need.txt` (paper)
- `karpathy-llm-wiki-gist.txt` (article)
- `podcast-interview-sutskever-2024.txt` (transcript)

## Metadata Header

Every collected file starts with a metadata block:

```markdown
---
url: https://example.com/article
retrieved: 2026-05-01
type: article | paper | transcript | notes | book-excerpt
author: Author Name
date: 2024-03-15
---
```

Include the `url` field whenever the source came from the web.

## Deduplication

Before saving, check if any existing file in `raw/` already has the same URL in its metadata block. If yes:
- Skip the duplicate
- Report: "Source already collected: `raw/filename.txt` (retrieved YYYY-MM-DD)"

## Versioning

The `raw/` directory is immutable — never modify existing files. If re-fetching the same URL:
- Save as `<slug>-v2.txt`, `<slug>-v3.txt`, etc.
- Note the version in the metadata block

## Edge Cases

| Situation | Action |
|-----------|--------|
| Paywalled content | Save whatever is extractable. Add `incomplete: true` to metadata. |
| Non-text source (PDF, video) | Save metadata + link. Add `format: pdf` or `format: video` and note what's needed to extract. |
| Very large page (>50KB) | Truncate at a natural boundary. Add `truncated: true` to metadata. Save the URL for re-fetching. |
| Fetch fails | Save the URL in a `raw/failed-fetches.md` list. Retry once. |

## After Collection

Offer to proceed with ingestion:
```
Collected X sources into raw/. Ready to ingest? (triggers wiki-ingest)
```

## Tool Requirements

Requires `web` and `file` toolsets. If web tools unavailable, report: "Cannot fetch from web — please provide sources manually in raw/." File-only mode still works for user-provided content.