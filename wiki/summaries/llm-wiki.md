---
title: "LLM Wiki"
type: summary
tags: [summary, knowledge-management, llm, ai-assisted-development]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Overview

The LLM Wiki is a pattern for building personal knowledge bases using LLM agents, authored by Andrej Karpathy. It replaces ephemeral RAG-style querying with a **persistent, compounding wiki** — a structured, interlinked collection of markdown files maintained by the LLM itself.

The core insight is that most LLM document interactions ([[entities/notebooklm]], ChatGPT uploads, typical RAG) force the model to rediscover knowledge from scratch on every question. The LLM Wiki pattern instead has the agent **compile knowledge once and keep it current**: when a new source arrives, the LLM reads it, extracts claims, updates concept and entity pages, flags contradictions, and strengthens the evolving synthesis. Cross-references are pre-built, contradictions are pre-flagged, and the knowledge base gets richer with every addition.

The user curates sources, asks questions, and explores. The LLM handles summarizing, cross-referencing, filing, and bookkeeping. In Karpathy's practice, the LLM agent runs alongside Obsidian: the LLM edits, the user browses links and the graph view in real time.

## Key Claims

- LLMs can maintain a **persistent, compounding wiki** rather than re-deriving answers per-query. → [[concepts/llm-wiki-pattern]]
- Knowledge should **accumulate and strengthen** over time, not be assembled from fragments on every question. → [[concepts/compounding-knowledge]]
- **Ingest** integrates a new source once, touching 10–15 wiki pages, then keeps the synthesis current. → [[concepts/wiki-ingest]]
- **Query** synthesizes from pre-built wiki pages and can file valuable answers back into the knowledge base. → [[concepts/wiki-query]]
- **Lint** periodically health-checks the wiki for contradictions, orphans, stale claims, and missing cross-references. → [[concepts/wiki-lint]]
- A **schema document** (e.g. CLAUDE.md, AGENTS.md) governs wiki structure, conventions, and workflows. → [[concepts/agent-schema-document]]
- The pattern is related in spirit to **Vannevar Bush's Memex** (1945) — a personal knowledge store with associative trails. → [[entities/memex]]

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Markdown idea file / pattern description |
| Author | Andrej Karpathy |
| URL | https://gist.githubusercontent.com/karpathy/.../llm-wiki.md |
| License | Not specified (public gist) |
| Ingested | 2026-05-21 |

## Relevant Concepts

- [[concepts/llm-wiki-pattern]] — the overarching pattern
- [[concepts/compounding-knowledge]] — the principle of persistent accumulation
- [[concepts/wiki-ingest]] — source ingestion operation
- [[concepts/wiki-query]] — question-answering operation
- [[concepts/wiki-lint]] — wiki health-check operation
- [[concepts/agent-schema-document]] — schema configuration concept
