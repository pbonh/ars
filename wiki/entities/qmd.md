---
title: "qmd"
type: entity
tags: [entity, tool, search-engine, markdown, local-first]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Overview

**qmd** is a local search engine for markdown files, offering hybrid BM25/vector search with LLM re-ranking, all running on-device. It is recommended in the LLM Wiki pattern as an optional CLI tool for searching large wikis once the `index.md` catalog becomes insufficient.

## Characteristics

- **Search model:** Combines traditional BM25 keyword ranking with vector semantic search, then re-ranks with an LLM.
- **Deployment:** Entirely local; no data leaves the device.
- **Interfaces:** Both a CLI (for shelling out from an agent) and an MCP server (for native tool use).
- **Scale target:** Useful when a wiki grows beyond the "moderate scale" where `index.md` + drill-down is sufficient.

## Common Strategies

- **Wiki search at scale:** When `index.md` has hundreds of entries and manual scanning is slow, `qmd` lets the LLM agent run targeted searches.
- **Agent integration:** Use the CLI from agent workflows, or connect via MCP for tighter tool integration.
- **Fallback for index gaps:** If `index.md` is stale or incomplete, `qmd` can still find relevant pages by content.

## Sources

- [LLM Wiki](raw/llm-wiki.md) — recommended as a search engine for markdown files
- [qmd GitHub repository](https://github.com/tobi/qmd)
