---
title: "Dataview"
type: entity
tags: [entity, plugin, obsidian, query, data]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Overview

**Dataview** is an Obsidian plugin that runs queries over page frontmatter to generate dynamic tables, lists, and counts. In an LLM wiki, it becomes a powerful navigation and auditing tool: if the LLM adds consistent YAML frontmatter (tags, dates, source counts, confidence levels), Dataview can surface custom views of the knowledge base.

## Characteristics

- **Query language:** DQL (Dataview Query Language) or JavaScript API.
- **Data source:** YAML frontmatter and inline fields from Obsidian markdown files.
- **Output types:** Tables, lists, task lists, and calendars.
- **Live updates:** Results refresh automatically when underlying files change.

## Common Strategies

- **Source audit table:** `TABLE source-count, confidence, updated FROM #concept SORT updated DESC` to see which concepts are stale or thinly sourced.
- **Tag dashboards:** Create a dashboard page per tag (e.g., `#ai-agent`) that auto-lists all matching concept and entity pages.
- **Ingest tracking:** Count pages created per source or per week to visualize wiki growth.
- **Confidence heatmap:** Surface all pages with `confidence: low` for targeted review.

## Sources

- [LLM Wiki](raw/llm-wiki.md) — recommended for generating dynamic tables and lists from wiki frontmatter
