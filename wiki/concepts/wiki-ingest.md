---
title: "Wiki Ingest"
type: concept
tags: [concept, knowledge-management, llm, workflow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

**Wiki ingest** is the operation of adding a new raw source to an LLM wiki. The LLM reads the source, extracts key information, and integrates it into the existing wiki — creating or updating summary pages, concept pages, entity pages, the index, and the log.

## How It Works

A typical ingest flow:

1. **User drops a source** into the `raw/` collection and tells the LLM to process it.
2. **LLM reads the source** fully, identifying distinct claims, concepts, and entities.
3. **LLM discusses key takeaways** with the user (optional but recommended by Karpathy).
4. **LLM writes a summary page** in `wiki/summaries/` describing what the source says, in the LLM's own words, with key terms wiki-linked.
5. **LLM creates or updates concept pages** in `wiki/concepts/` — one page per distinct claim or concept the source introduces or substantially refines.
6. **LLM creates or updates entity pages** in `wiki/entities/` — one page per distinct tool, product, person, or organization named.
7. **LLM updates `wiki/index.md`** with new rows in the relevant tables.
8. **LLM appends to `wiki/log.md`** with one entry per page touched.

A single source commonly touches 10–15 wiki pages. The raw source remains immutable; all mutable work happens in the wiki layer.

## Key Parameters

| Parameter | Guidance |
|-----------|----------|
| Batch vs. single | Karpathy prefers single-source ingest with human review for quality control. Batch is possible but risks missed cross-references. |
| Atomic claims | Each concept page should represent one claim; do not bundle unrelated ideas into a single page. |
| Frontmatter | Standard YAML frontmatter on every page (title, type, tags, created, updated, sources, confidence). |
| Wiki-links | Internal links use double-bracket syntax with a `concepts/` or `entities/` prefix and must resolve to existing pages. |
| Confidence | Honest assessment: `high`, `medium`, or `low` depending on source quality and speculation level. |

## When To Use

Ingest whenever:
- A new article, paper, transcript, book chapter, or dataset arrives that belongs in the knowledge base.
- You want to update the wiki's synthesis with fresh information.
- You need to add a new entity or concept that the wiki does not yet cover.
- You are starting a new research thread and want to seed the wiki with foundational sources.

Delay or skip ingest when:
- The source is ephemeral or low-quality (spam, unverified rumor).
- The source duplicates an already-ingested document with no new claims.
- You are in the middle of a query or lint pass and want to avoid concurrent modifications.

## Risks & Pitfalls

- **Missing cross-references:** A new concept may relate to existing pages the LLM overlooks. The schema should prompt the LLM to check for related pages before finishing ingest.
- **Contradiction blindness:** The LLM may fail to notice that a new source contradicts an existing claim. Explicit contradiction-checking steps in the ingest workflow help.
- **Page sprawl:** Over-eager creation of tiny concept pages can bloat the wiki. The schema should define what merits a standalone page vs. an inline mention.
- **Log inconsistency:** If the log is not appended correctly, the timeline of wiki evolution becomes unreliable. Entries should use a consistent, parseable prefix.
- **Frontmatter drift:** Pages created in different ingests may have inconsistent frontmatter. The schema must specify the canonical format.

## Related Concepts

- [[concepts/llm-wiki-pattern]] — the pattern that defines ingest as one of three core operations
- [[concepts/compounding-knowledge]] — the principle that ingest implements
- [[concepts/wiki-query]] — the complementary read operation
- [[concepts/wiki-lint]] — the health-check that often follows a batch of ingests
- [[concepts/agent-schema-document]] — the document that defines ingest conventions
- [[entities/obsidian-web-clipper]] — tool for quickly clipping web articles into the raw collection

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's description of the ingest operation
