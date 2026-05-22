---
title: "Nushell Structured Pipeline"
type: concept
tags: [concept, shell, data-processing, pipeline]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

A Nushell pipeline is a sequence of commands where data flows from an **input** (producer), through one or more **filters**, to an **output** (sink). Unlike traditional Unix shells where pipelines carry only raw text or bytes, Nushell pipelines carry typed structured data such as lists, records, and tables.

## How It Works

1. **Input commands** (`ls`, `open`, `http get`) create structured values and feed them into the pipeline.
2. **Filter commands** (`where`, `update`, `sort-by`, `each`) transform the data in-flight.
3. **Output commands** (`save`, `print`, `table`) consume the pipeline and produce a side effect or final display.

Commands declare their supported input/output types. For example, `ls` outputs a `table` and accepts `nothing` as input. Attempting to pipe an incompatible type can result in a parse-time error.

External commands are treated as boundaries: data flowing out of Nushell into an external command is converted to text (or binary), and data coming in from an external command is read as bytes and optionally converted to UTF-8 text.

## Key Parameters

- `$in` — a special variable holding the current pipeline input. It can be used in the first position of a pipeline inside a block or closure, or in subsequent positions to reference the previous stage's output.
- Input/output signatures — custom commands and built-ins declare which types they accept and emit, enabling static type checking across pipeline stages.

## When To Use

- Use structured pipelines whenever you need to filter, sort, aggregate, or transform tabular or hierarchical data.
- Prefer built-in Nushell commands over external tools (`jq`, `awk`, `sed`) when working with JSON, CSV, TOML, or other structured formats, because Nushell parses them natively into typed values.

## Risks & Pitfalls

- Using `$in` forces collection of a stream into a single value, which may increase memory usage and reduce performance for large datasets.
- External commands do not understand Nushell's structured types; piping a rendered table to `grep` will include Unicode border characters, producing unexpected results. Explicitly convert to plain text first (`to text`) when needed.
- Commands like `ls` that do not accept pipeline input will silently ignore an input stream rather than erroring at runtime.

## Related Concepts

- [[concepts/nushell-data-types]] — the types that flow through pipelines
- [[concepts/nushell-custom-command]] — defining commands with explicit input/output signatures
- [[concepts/nushell-implicit-return]] — the value returned by the last stage becomes the pipeline's result

## Sources

- Nushell Book: [Pipelines](raw/nushell-book/book/pipelines.md)
- Nushell Book: [Types of Data](raw/nushell-book/book/types_of_data.md)
