---
title: "Reedline"
type: entity
tags: [entity, tool, line-editor, rust, nushell]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Overview

Reedline is Nushell's dedicated line editor, maintained in its own repository under the Nushell GitHub organization. It provides the interactive readline experience for the Nushell REPL, including syntax highlighting, completions, multi-line editing, and history.

## Characteristics

- **Language**: Rust
- **License**: MIT
- **Relationship to Nushell**: Separate crate/repository, tightly integrated as the default line editor
- **Key features**: Syntax highlighting, tab completion, history, multi-line editing, hints

## Common Strategies

- Use Reedline as the default line editor when running Nushell interactively.
- Contribute to Reedline for improvements in completion, history search, or prompt behavior.
- Embed Reedline in other Rust projects that need a modern readline implementation.

## Sources

- Nushell Book: [README — The Many Parts of Nushell](raw/nushell-book/book/README.md)
- GitHub: https://github.com/nushell/reedline
