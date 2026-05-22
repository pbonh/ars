---
title: "string-pipeline"
type: entity
tags: [entity, rust-crate, templating, string-processing]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Overview

`string-pipeline` is a Rust crate that provides a pipeline-based template language for string transformations. It is the engine behind Television's template system, enabling dynamic formatting of entries, previews, and action commands inside channel TOML files.

## Characteristics

- **Pipeline syntax**: operations are chained with `|` and evaluated left to right.
- **Built-in operations**: split, strip ANSI, trim, case conversion, pad, prepend/append, regex extract/replace, map, filter, sort, and join.
- **Delimiter-aware**: supports custom delimiters with escape sequences (`\\:` for literal `:`, `\t`, `\n`).
- **Collection processing**: map/filter/sort/join work on arrays produced by `split`.

## Common Strategies

- Use `string-pipeline` inside Television channels to extract fields from delimited output (e.g., `file:line:content` from ripgrep).
- Chain `strip_ansi|split:\::0` to clean colored output and grab the first field.
- Use `map:{prepend:• }|join:\n` to format multi-select output as a Markdown list.
- Reference the crate documentation at https://docs.rs/string_pipeline for the complete syntax specification.

## Sources

- Crates.io / docs.rs: https://docs.rs/string_pipeline
- Television docs: Template system guide and channel specification.
