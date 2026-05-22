---
title: "LLM Wiki Pattern"
type: concept
tags: [concept, knowledge-management, llm, ai-assisted-development]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

An **LLM Wiki** is a personal knowledge-base pattern in which an LLM agent incrementally builds and maintains a structured, interlinked collection of markdown files that sits between the user and raw sources. The wiki is a **persistent, compounding artifact**: cross-references are pre-built, contradictions are flagged and resolved incrementally, and the synthesis reflects every source ever read.

## How It Works

The pattern has three layers:

1. **Raw sources** — immutable source documents (articles, papers, transcripts, images). The LLM reads from them but never modifies them. This is the source of truth.
2. **The wiki** — LLM-generated markdown files: summaries, concept pages, entity pages, comparisons, syntheses. The LLM owns this layer entirely, creating pages, updating them when new sources arrive, and maintaining cross-references.
3. **The schema** — a configuration document (e.g. `CLAUDE.md`, `AGENTS.md`, or a skill file) that tells the LLM how the wiki is structured, what conventions to follow, and what workflows to use for ingest, query, and lint operations. The schema is co-evolved by the user and the LLM over time.

In practice, the user keeps an LLM agent open on one side and a markdown viewer (commonly [[entities/obsidian]]) on the other. The LLM makes edits based on conversation; the user browses links, checks the graph view, and reads updated pages in real time. Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase.

## Key Parameters

| Aspect | Typical RAG | LLM Wiki |
|--------|-------------|----------|
| Knowledge state | Re-derived per query | Persistent and compounding |
| Cross-references | Assembled on demand | Pre-built and maintained |
| Contradictions | Discovered (or missed) per query | Flagged during ingest |
| Human role | Prompt engineering, reviewing answers | Curating sources, asking questions, exploring |
| LLM role | Retrieval + generation | Ingest, query, lint, cross-reference maintenance |
| Scale | Index scales with sources; wiki scales with concepts | Moderate scale (~100s of pages) works with index.md alone |

## When To Use

Use an LLM Wiki when:
- You are accumulating knowledge on a topic over weeks or months (research, competitive analysis, due diligence).
- You want a structured companion to a book, course, or project with characters, themes, or concepts that interconnect.
- You are journaling or tracking personal data (health, goals, psychology) and want a structured picture that builds over time.
- Your team produces scattered documents (Slack, meetings, project docs) that need centralized, maintained synthesis.
- You are doing any hobby deep-dive where organization matters more than ephemeral chat answers.

A typical RAG system may still be preferable when:
- You need a single, one-off answer from a large document set.
- The document collection changes so rapidly that persistent synthesis would be constantly stale.
- You do not have an agent that can touch multiple files in one pass.

## Risks & Pitfalls

- **Schema drift:** Without a maintained schema document, the LLM may gradually change page formats, frontmatter conventions, or directory structure. The schema must be kept current as conventions evolve.
- **Over-normalization:** The LLM may create too many tiny pages or too few overloaded ones. The schema should guide atomic-claim discipline.
- **Stale synthesis:** A claim that was true in an early source may be contradicted by a later one. Without periodic [[concepts/wiki-lint|linting]], stale claims can persist.
- **Batch ingest chaos:** Ingesting many sources at once with low supervision can produce inconsistent page quality or missed cross-references. Karathy recommends ingesting one at a time with human review.
- **Tool lock-in:** The pattern is described with Obsidian in mind, but the markdown files are plain text and can be viewed with any tool or even a simple text editor.

## Related Concepts

- [[concepts/compounding-knowledge]] — the principle that distinguishes this pattern from RAG
- [[concepts/wiki-ingest]] — operation for adding a source
- [[concepts/wiki-query]] — operation for asking questions
- [[concepts/wiki-lint]] — operation for health-checking
- [[concepts/agent-schema-document]] — the configuration layer
- [[entities/obsidian]] — commonly used viewer
- [[entities/qmd]] — optional local search engine for larger wikis
- [[entities/andrej-karpathy]] — author of the pattern

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's original pattern description
