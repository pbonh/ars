---
title: "Wiki Query"
type: concept
tags: [concept, knowledge-management, llm, workflow]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

**Wiki query** is the operation of asking questions against an LLM wiki. The LLM searches for relevant pages, reads them, synthesizes an answer with citations, and optionally files the answer back into the wiki as a new page — turning ephemeral exploration into persistent knowledge.

## How It Works

A typical query flow:

1. **User asks a question** against the wiki.
2. **LLM reads `wiki/index.md`** to find relevant page categories and candidate pages.
3. **LLM drills into relevant pages** — summaries, concepts, entities — to gather evidence.
4. **LLM synthesizes an answer** with inline citations to the wiki pages used.
5. **LLM optionally files the answer** back into the wiki as a new page (comparison, analysis, connection, table, or slide deck).

The critical insight is that **good answers are valuable and should not disappear into chat history**. A comparison table, an analysis, a newly discovered connection — these compound the knowledge base just like ingested sources do.

Answers can take many forms depending on the question:
- Markdown narrative or comparison table
- Slide deck using [[entities/marp]]
- Chart using matplotlib
- Canvas or diagram
- New concept or entity pages if the query surfaces missing wiki coverage

## Key Parameters

| Parameter | Guidance |
|-----------|----------|
| Search strategy | Start with `index.md`, then drill into linked pages. At moderate scale (~100s of pages) this avoids embedding-based RAG infrastructure. |
| Citation style | Inline wiki-links to the pages that provided evidence. |
| Answer filing | If the answer is non-trivial and reusable, create a new wiki page and update the index. |
| Output formats | Determined by the schema document; the LLM should know which formats are supported. |

## When To Use

Query the wiki when:
- You need a synthesized answer that draws on multiple sources already in the wiki.
- You want to explore connections between concepts or entities.
- You are checking the current state of the knowledge base on a topic.
- You want to produce a deliverable (presentation, analysis, report) from wiki content.

Query raw sources directly (bypassing the wiki) when:
- The wiki does not yet contain relevant pages and you need a quick answer.
- The question is about a source you have not yet ingested.

## Risks & Pitfalls

- **Answer loss:** If the LLM does not file good answers back into the wiki, the exploration is ephemeral and must be repeated. The schema should encourage filing by default.
- **Circular citations:** An answer page that cites itself or other answer pages (rather than original sources) can create circular reasoning. Filed answers should cite the original concept/entity/summary pages.
- **Stale answer pages:** A filed answer may become outdated as the wiki evolves. Answers should include a `created:` date and be subject to [[concepts/wiki-lint|linting]] for stale claims.
- **Index-first blindness:** If `index.md` is incomplete or stale, the LLM may miss relevant pages. The index must be maintained on every ingest.
- **Format mismatch:** The LLM may generate a Marp deck when the user has no Marp plugin, or a chart when matplotlib is unavailable. The schema should specify which output tools are installed.

## Related Concepts

- [[concepts/llm-wiki-pattern]] — the pattern that defines query as one of three core operations
- [[concepts/compounding-knowledge]] — the principle that query answers compound when filed back
- [[concepts/wiki-ingest]] — the write operation that populates pages queries read from
- [[concepts/agent-schema-document]] — the document that defines query conventions and output formats

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's description of the query operation
