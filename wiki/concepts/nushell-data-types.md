---
title: "Nushell Data Types"
type: concept
tags: [concept, shell, type-system, data-structures]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

Nushell provides a rich, statically checked type system that includes both primitive scalar types and structured compound types. Every value has a type that can be inspected with the `describe` command, and many commands declare which input/output types they support.

## How It Works

### Scalar Types

| Type | Annotation | Examples |
|------|------------|----------|
| Integer | `int` | `42`, `0xff`, `-10` |
| Float | `float` | `3.14`, `-0.5` |
| String | `string` | `"hello"`, `'hello'`, `r#'raw'#` |
| Boolean | `bool` | `true`, `false` |
| DateTime | `datetime` | `2000-01-01`, `date now` |
| Duration | `duration` | `2min + 12sec`, `3.14day` |
| Filesize | `filesize` | `64mb`, `1.5GiB` |
| Range | `range` | `0..4`, `0..<5`, `2..4..20` |
| Binary | `binary` | `0x[ff d8]` |
| Cell-path | `cell-path` | `$.name.0` |
| Closure | `closure` | `{\|e\| $e + 1}` |
| Null | `nothing` | `null` |

### Structured Types

| Type | Annotation | Description |
|------|------------|-------------|
| List | `list` | Ordered sequence of values: `[1 2 3]` |
| Record | `record` | Key-value pairs: `{name: "Nu", lang: "Rust"}` |
| Table | `table` | List of records with the same keys; rendered as rows and columns |

Tables are the primary output format of many Nushell commands (e.g., `ls`). Internally, a table is simply a `list<record>`.

## Key Parameters

- `describe` — returns the type of a value.
- Type annotations — can be used in `let` bindings, custom command parameters, and pipeline signatures to enforce static type checking.

## When To Use

- Use Nushell's native types for configuration parsing, data exploration, and reporting instead of converting everything to strings.
- Leverage durations and file sizes for arithmetic (e.g., `30day / 1sec`, `1GiB / 1B`).
- Use closures as arguments to filter commands (`where`, `each`, `update`).

## Risks & Pitfalls

- Decimal floats are approximate, as in most languages (`10.2 * 5.1` may not equal `52.02` exactly).
- Ranges are inclusive by default; use `..<` for exclusive end bounds.
- Binary data from external sources may arrive as a raw byte stream rather than a structured value.

## Related Concepts

- [[concepts/nushell-structured-pipeline]] — structured types flow through pipelines
- [[concepts/nushell-custom-command]] — parameters and signatures reference these types

## Sources

- Nushell Book: [Types of Data](raw/nushell-book/book/types_of_data.md)
- Nushell Book: [Working with Lists](raw/nushell-book/book/working_with_lists.md)
- Nushell Book: [Working with Records](raw/nushell-book/book/working_with_records.md)
- Nushell Book: [Working with Tables](raw/nushell-book/book/working_with_tables.md)
