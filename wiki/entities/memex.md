---
title: "Memex"
type: entity
tags: [entity, system, history, knowledge-management]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Overview

The **Memex** (Memory Extender) is a conceptual device described by Vannevar Bush in his 1945 essay "As We May Think." It envisioned a personal, curated knowledge store with associative trails between documents — mechanically linked microfilm records that a user could navigate by association rather than by strict hierarchy. The LLM Wiki pattern cites the Memex as a historical predecessor that shared the vision of private, actively curated knowledge with connections as valuable as the documents themselves.

## Characteristics

- **Personal:** A single user's private knowledge store, not a public web.
- **Associative:** Documents linked by conceptual trails ("associative indexing") rather than fixed categories.
- **Curated:** The owner actively builds and maintains the collection.
- **Mechanical realization:** Bush proposed microfilm, photoelectric cells, and levers; the web later realized a fragment of the linking vision, but as a public rather than private system.

## Common Strategies

- **Historical analogy:** The LLM Wiki pattern explicitly positions itself as closer to Bush's Memex than to the modern web. Where the web is public, fragmented, and link-rotted, the Memex/LLM-Wiki is private, curated, and actively maintained.
- **Maintenance problem:** Bush could not solve who would do the tedious cross-referencing and upkeep. The LLM Wiki pattern solves this by assigning maintenance to an LLM agent — "the part he couldn't solve was who does the maintenance. The LLM handles that."
- **Design inspiration:** When architecting a wiki, the Memex reminds designers to prioritize associative trails, personal curation, and persistent context over rigid taxonomies.

## Sources

- [LLM Wiki](raw/llm-wiki.md) — cites the Memex as the historical spirit of the LLM Wiki pattern
- Vannevar Bush, "As We May Think" (1945) — original essay in *The Atlantic*
