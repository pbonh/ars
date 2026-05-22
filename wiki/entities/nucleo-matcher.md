---
title: "nucleo-matcher"
type: entity
tags: [entity, rust-crate, fuzzy-matching, algorithm]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Overview

`nucleo-matcher` is a Rust crate that implements high-performance fuzzy string matching. It is the matching engine used by Television to filter entries in real time as the user types.

## Characteristics

- **Multiple matcher kinds**: supports fuzzy, substring, prefix, suffix, and exact matching.
- **Negation support**: patterns can be inverted with `!` to exclude matches.
- **AND composition**: multiple patterns are combined with implicit AND logic.
- **Performance-oriented**: designed for interactive workloads with large entry lists.

## Common Strategies

- Rely on fuzzy matching (`foo`) for exploratory search where exact spelling is unknown.
- Switch to substring (`'foo`), prefix (`^foo`), suffix (`foo$`), or exact (`^foo$`) for precise filtering.
- Combine patterns with spaces to narrow results: `src ^main !test$`.
- Use Television's `--exact` flag to force substring matching globally when fuzzy noise is undesirable or performance is critical.

## Sources

- Crates.io / docs.rs: https://docs.rs/nucleo-matcher/latest/nucleo_matcher/pattern/enum.AtomKind.html
- Television docs: Search patterns reference.
