---
title: "Nushell"
type: entity
tags: [entity, tool, shell, programming-language, rust]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Overview

Nushell (Nu) is a modern cross-platform shell and programming language written in Rust. It combines the Unix pipeline philosophy with structured data types, static parsing, and a rich type system. The project is maintained by the Nushell organization on GitHub and consists of multiple repositories including the core shell, this documentation book, the Reedline line editor, and community script collections.

## Characteristics

- **Language**: Rust
- **License**: MIT
- **Platforms**: Cross-platform (Linux, macOS, Windows)
- **Data model**: Structured (tables, records, lists) rather than plain text
- **Execution model**: Parse-then-eval (static parsing, no `eval`)
- **Extensibility**: Plugin protocol (`nu-plugin`), modules, custom commands
- **Default line editor**: Reedline (separate repository)

## Common Strategies

- Use Nushell as an interactive daily driver for file exploration, data wrangling, and system administration, replacing Bash/PowerShell/Zsh.
- Write reusable scripts and modules in `.nu` files, leveraging typed custom commands and scoped environment.
- Integrate with external tools via plugins (Polars for analytics, query for SQL/XML, formats for extra file types).
- Embed Nushell's parser or engine crates as libraries in Rust applications that need shell-like scripting capabilities.

## Sources

- Nushell Book: [README / Introduction](raw/nushell-book/book/README.md)
- GitHub: https://github.com/nushell/nushell
