---
title: "Polars"
type: entity
tags: [entity, library, dataframe, rust, data-processing]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Overview

Polars is a fast DataFrame library implemented in Rust. In the Nushell ecosystem, it serves as the computation engine behind the DataFrame plugin (`nu_plugin_polars`), providing columnar data operations via the Apache Arrow memory format.

## Characteristics

- **Language**: Rust (with Python and other bindings)
- **License**: MIT / Apache-2.0
- **Data model**: Columnar (Apache Arrow)
- **Integration**: Exposed to Nushell through the `polars` core plugin
- **Performance**: Optimized for large datasets; benchmarked against Pandas and native Nushell tables

## Common Strategies

- Use Polars via the Nushell DataFrame plugin when processing CSV, Parquet, or other large tabular datasets that exceed the performance limits of Nushell's native `list<record>` tables.
- Leverage lazy evaluation for query optimization on large files.
- Compare performance with native Nushell pipelines using `std bench` before committing to DataFrames for medium-sized data.

## Sources

- Nushell Book: [Dataframes](raw/nushell-book/book/dataframes.md)
- GitHub: https://github.com/pola-rs/polars
