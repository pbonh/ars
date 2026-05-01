---
name: wiki-query
description: Use when the user asks a question about the wiki's domain, wants to look something up in the knowledge base, or asks "what does the wiki say about..."
---

# Wiki Query

Answer questions by searching the wiki and synthesizing findings with citations.

## Query Workflow

### 1. Read the index

Start with `wiki/index.md` to identify candidate pages. Scan the Concepts, Entities, and Summaries tables for relevant titles and tags.

### 2. Search

Search across candidate pages:

- **Keyword match**: page titles, frontmatter `tags`, section headings
- **Cross-link traversal**: follow `[[links]]` from matching pages to discover related content
- **Full-text scan**: if needed, read page content for deeper matches

### 3. Synthesize answer

Compose an answer that:

1. **Answers directly** — lead with the conclusion, then explain
2. **Cites sources** — use `[[wiki links]]` as inline citations: "According to [[concepts/attention-mechanism]], the key insight is..."
3. **Signals confidence** — qualify claims from low-confidence sources:
   - "[[concepts/speculative-idea]] suggests X, though this is low confidence (single source)"
4. **Notes gaps** — when the wiki cannot fully answer: "The wiki has limited information on this. Related: [[concepts/partial-match]] touches on..."

### 4. Offer synthesis creation

If the answer reveals a novel cross-cutting insight not captured in any existing page:

```
This question touches on multiple concepts: [[concepts/A]], [[concepts/B]], [[concepts/C]].
Would you like me to create a synthesis page comparing these?
```

If user agrees, create `wiki/syntheses/<descriptive-slug>.md` using the Synthesis page format from `references/page-formats.md` (via wiki-ingest skill). Then update `wiki/index.md` and `wiki/log.md`.

## Answer Format

```
[Direct answer, 1-3 sentences]

[Supporting detail with citations]

**Key pages**: [[concepts/X]], [[concepts/Y]], [[summaries/Z]]

**Confidence**: overall assessment of answer quality
**Gaps**: what the wiki doesn't yet cover on this topic
```

## Tool Requirements

Requires `file` toolset. Works with any wiki that has an index.md.