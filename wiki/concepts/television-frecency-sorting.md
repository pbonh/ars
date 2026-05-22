---
title: "Television Frecency Sorting"
type: concept
tags: [concept, fuzzy-finder, ranking, algorithm]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

**Frecency sorting** is Television's default result-ranking algorithm that combines **frequency** (how often an entry has been selected) with **recency** (how recently it was selected). Items that are used often and recently bubble toward the top of the results list.

## How It Works

As the user searches and selects entries, Television records usage metadata. When computing the result order, the matcher first filters by query relevance, then the frecency score reorders matches so that habitually or recently used items appear earlier. The algorithm is automatic and requires no user configuration beyond enabling or disabling it.

Per-channel controls exist in the `[source]` section:

- `frecency = true` (default) — enables frecency ranking alongside match-quality sorting.
- `frecency = false` — disables frecency while keeping match-quality sorting.
- `no_sort = true` — disables both frecency and match-quality sorting, preserving the exact source-command order.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frecency` | `true` | Enable frecency-based ranking for the channel. |
| `no_sort` | `false` | Preserve original source order; disables all sorting. |

## When To Use

Keep frecency enabled for general browsing channels (files, git repos) where personal usage patterns improve discoverability. Disable frecency for channels where the source order is meaningful, such as shell history, git log, or process listings, to prevent reordering based on past selections.

## Risks & Pitfalls

- Frecency data is stored locally; there is no documented migration or sync mechanism across machines.
- Global history (`--global-history`) may cross-pollute frecency scores between unrelated channels if the same string appears in different contexts.
- Very large entry sets with frecency enabled may incur a slight memory overhead to track scores.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-search-pattern]]

## Sources

- Television docs: Tips and tricks (frecency sorting), channel specification reference.
