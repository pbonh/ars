---
title: "Compounding Knowledge"
type: concept
tags: [concept, knowledge-management, llm]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

**Compounding knowledge** is the principle that information in a knowledge base should accumulate and strengthen over time rather than being re-derived from scratch on every query. Each new source enriches the existing synthesis; cross-references are built once and kept current; contradictions are flagged and resolved incrementally.

## How It Works

In a typical RAG system, the LLM retrieves document chunks and assembles an answer at query time. The knowledge is **rediscovered** each time — even if the same five documents were queried yesterday. There is no persistent structure between queries.

In a compounding model, the LLM performs the integration work **once during ingest**:
1. Reads the new source.
2. Extracts claims, concepts, and entities.
3. Writes or updates wiki pages.
4. Adds cross-references to related pages.
5. Flags contradictions with existing claims.
6. Appends to the log.

Subsequent queries read from the **pre-synthesized wiki** rather than raw sources. The cross-references are already there. The synthesis already reflects the full corpus. The knowledge base grows richer with every addition, compounding like interest rather than resetting to zero.

## Key Parameters

| Dimension | Rediscovered (RAG) | Compounding (LLM Wiki) |
|-----------|----------------------|------------------------|
| Query cost | High: retrieval + ranking + synthesis | Low: read relevant pages + answer |
| Multi-source synthesis | Fragile: must re-assemble fragments | Robust: already integrated during ingest |
| Cross-references | Generated per answer | Persistent, navigable, graph-visible |
| Contradiction detection | Rare, accidental | Explicit, logged, resolved over time |
| Knowledge depth | Flat: same effort every query | Deep: effort amortized, depth grows |

## When To Use

Compounding knowledge is the right model when:
- You expect to ask many questions about the same corpus over time.
- Synthesis across multiple sources is common (e.g., "How does concept X in paper A relate to concept Y in book B?").
- You want a browsable, linkable structure that you can explore visually (e.g., in a graph view).
- You are building up expertise or a narrative that evolves (research, book reading, competitive tracking).

Rediscovered knowledge (standard RAG) is preferable when:
- The document set is vast and queries are one-off (e.g., "What was the revenue in Q3?").
- You do not have an agent capable of multi-file maintenance.
- Latency of ingest is unacceptable and you need immediate answers to a static corpus.

## Risks & Pitfalls

- **Stale synthesis danger:** A claim integrated early may be contradicted by a later source. If the LLM does not flag or resolve the contradiction, the wiki can entrench outdated information. Periodic [[concepts/wiki-lint|linting]] and explicit contradiction logging are essential.
- **Integration bottleneck:** The cost is paid upfront during ingest. If sources are very large or numerous, ingest can become slow or expensive. Batch ingest and progressive summarization can mitigate this.
- **Over-confidence in pre-synthesis:** Users may trust wiki pages as "settled" when the underlying sources are still evolving. Frontmatter `confidence:` fields and source citations help signal uncertainty.
- **Compounding without pruning:** A wiki can grow indefinitely. Without periodic review and archival of obsolete pages, the index becomes unwieldy and the signal-to-noise ratio drops.

## Related Concepts

- [[concepts/llm-wiki-pattern]] — the pattern that implements compounding knowledge
- [[concepts/wiki-ingest]] — where the compounding happens
- [[concepts/wiki-lint]] — how to keep the compound healthy
- [[entities/obsidian]] — viewer with graph view for visualizing accumulated structure

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's description of the compounding principle
