---
title: "Nushell DataFrame"
type: concept
tags: [concept, shell, data-processing, analytics, columnar]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

A Nushell DataFrame is a columnar data structure optimized for high-performance analytics on large datasets. It is backed by the Apache Arrow memory format and powered by the Polars library via the official `nu_plugin_polars` plugin. DataFrames store data in a column-oriented layout, making operations like group-by, join, and aggregation significantly faster and more memory-efficient than row-based lists or tables for large files.

## How It Works

DataFrames are created from files or Nushell tables using `polars` commands:

```nu
let df = polars open --eager large_dataset.csv
$df | polars group-by year | polars agg (polars col geo_count | polars sum)
```

Lazy evaluation is supported (default as of 0.97) for deferred execution and query optimization; use `--eager` for immediate materialization.

The columnar format means that values of the same type are stored contiguously, allowing vectorized operations and efficient memory use compared to Nushell's native `list<record>` (row-based) tables.

## Key Parameters

- `polars open` / `polars read` — load data into a DataFrame.
- `polars into-df` — convert a Nushell table to a DataFrame.
- `polars group-by`, `polars join`, `polars agg`, `polars filter` — core analytics operations.
- `--eager` vs lazy — controls whether operations are executed immediately or deferred.

## When To Use

- Use DataFrames when working with millions of rows or when performing heavy aggregations, joins, or group-by operations.
- For small or medium datasets where readability and interactivity matter more than raw performance, native Nushell tables and lists are often simpler.

## Risks & Pitfalls

- DataFrames require the Polars plugin, which must be installed, added to the registry, and imported.
- The plugin protocol version must match the Nushell version; mismatches will prevent the plugin from loading.
- DataFrames are a separate type from Nushell's native `table`; they must be explicitly converted (`polars into-df` / `polars collect`) to interoperate with standard Nushell commands.

## Related Concepts

- [[concepts/nushell-plugin-system]] — DataFrames are provided by the Polars plugin
- [[concepts/nushell-structured-pipeline]] — DataFrames fit into pipelines but use their own specialized command set

## Sources

- Nushell Book: [Dataframes](raw/nushell-book/book/dataframes.md)
