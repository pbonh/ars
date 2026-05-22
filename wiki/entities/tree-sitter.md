---
title: "Tree-sitter"
type: entity
tags: [entity, library, parsing, syntax-highlighting]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/treesitter.txt"]
confidence: high
---

## Overview

Tree-sitter is an incremental parsing library that generates concrete syntax trees for source code. It is designed to be fast, error-resilient, and suitable for use in text editors. Neovim integrates tree-sitter natively to power syntax highlighting, language injections, and structural code navigation.

## Characteristics

- Incremental parsing (updates tree on edit, not full re-parse)
- Error recovery (produces valid tree even with syntax errors)
- Parser generator (grammars compiled to C, then to shared libraries)
- Query language (lisp-like `.scm` files for pattern matching on AST nodes)
- Wasm parser support (in Neovim, if built with `ENABLE_WASMTIME`)
- Language-agnostic core with per-language grammar repositories

## Common Strategies

- Install parsers via the `nvim-treesitter` plugin or manually to `parser/` on `runtimepath`
- Write `highlights.scm` queries for custom language support
- Use `injections.scm` for polyglot files (HTML/CSS/JS, Markdown/code)
- Override bundled queries by placing files earlier on `runtimepath` or using `; extends`
- Profile slow buffers by disabling injections with empty `queries/<lang>/injections.scm`

## Sources

- [Neovim Treesitter Reference](raw/nvim-docs/treesitter.txt)
