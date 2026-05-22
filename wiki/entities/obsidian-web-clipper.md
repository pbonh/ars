---
title: "Obsidian Web Clipper"
type: entity
tags: [entity, tool, browser-extension, obsidian, markdown]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Overview

**Obsidian Web Clipper** is a browser extension that converts web articles to markdown and sends them directly into an Obsidian vault. It is recommended in the LLM Wiki pattern as the fastest way to get online sources into the `raw/` collection.

## Characteristics

- **Conversion:** Extracts article content, strips ads and clutter, and produces clean markdown.
- **Destination:** Sends clips to a configurable folder within an Obsidian vault (e.g., `raw/`).
- **Metadata capture:** Preserves title, URL, author, and date where available.
- **Browser support:** Available for major browsers (Chrome, Firefox, Safari).

## Common Strategies

- **Frictionless ingest pipeline:** See an interesting article → clip it → it lands in `raw/` → tell the LLM to ingest it. No manual copy-paste or download.
- **Batch research:** Before a research session, clip 5–10 relevant articles, then batch-ingest them into the wiki.
- **Image handling:** After clipping, use Obsidian's "Download attachments for current file" hotkey to pull images locally, ensuring the LLM can reference them even if original URLs break.

## Sources

- [LLM Wiki](raw/llm-wiki.md) — recommended for quickly getting web sources into the raw collection
