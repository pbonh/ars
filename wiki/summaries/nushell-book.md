---
title: "Nushell Book"
type: summary
tags: [summary, shell, programming-language, data-processing, rust]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Overview

Nushell is a modern cross-platform shell and programming language written in Rust. Rather than treating shells and programming languages as separate tools, Nushell unifies them into a single environment. It takes the Unix philosophy of composable pipelines and extends it beyond plain text to structured data types such as tables, records, and lists.

The shell is designed around three core ideas:
1. **Structured data pipelines** — commands communicate via typed data (tables, records, lists) rather than raw byte streams, enabling powerful query and transformation operations without external tools like `awk` or `jq`.
2. **Everything is an expression** — Every command returns a value; the last expression in a block is implicitly returned. There are no "statements" that produce no value.
3. **Static parsing before evaluation** — Nushell parses entire expressions or files before executing them, similar to compiled languages. This enables rich IDE support, real-time error highlighting, accurate completions, and a strong type system, but means dynamic constructs like `eval` or runtime-generated source files are not supported.

Nushell also emphasizes immutable-by-default variables, scoped environment mutation, and a first-class module system for organizing code. It ships with a plugin protocol (`nu-plugin`) that allows external binaries to extend the shell with new commands, and includes official plugins for DataFrames (via Polars), additional file formats, SQL queries, and more.

## Key Claims

- [[concepts/nushell-structured-pipeline]] — Nushell pipelines carry typed structured data, not just text.
- [[concepts/nushell-implicit-return]] — The last expression in any block is automatically returned; there is no distinction between expressions and statements.
- [[concepts/nushell-static-parsing]] — Nushell uses a separate parse-then-eval stage, enabling IDE features but prohibiting runtime code generation.
- [[concepts/nushell-scoped-environment]] — Environment variable changes are scoped to the block in which they occur, avoiding global mutable state.
- [[concepts/nushell-immutable-variables]] — Variables are immutable by default, encouraging functional data-transformation patterns.
- [[concepts/nushell-data-types]] — Nushell provides a rich type system including durations, file sizes, ranges, cell-paths, closures, records, and tables.
- [[concepts/nushell-custom-command]] — User-defined commands are first-class citizens with typed signatures, flags, rest parameters, and attributes.
- [[concepts/nushell-module-system]] — Modules organize commands, aliases, constants, and environment variables into reusable containers.
- [[concepts/nushell-plugin-system]] — Plugins communicate via a versioned protocol and extend Nushell without modifying core code.
- [[concepts/nushell-dataframe]] — Columnar DataFrames backed by Apache Arrow and Polars enable high-performance analytics on large datasets.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Open-source documentation (Markdown book) |
| Owner | Nushell project (GitHub organization) |
| URL | https://github.com/nushell/nushell.github.io/tree/main/book |
| License | MIT |
| Ingested on | 2026-05-21 |

## Relevant Concepts

- [[concepts/nushell-structured-pipeline]]
- [[concepts/nushell-implicit-return]]
- [[concepts/nushell-static-parsing]]
- [[concepts/nushell-scoped-environment]]
- [[concepts/nushell-immutable-variables]]
- [[concepts/nushell-data-types]]
- [[concepts/nushell-custom-command]]
- [[concepts/nushell-module-system]]
- [[concepts/nushell-plugin-system]]
- [[concepts/nushell-dataframe]]
