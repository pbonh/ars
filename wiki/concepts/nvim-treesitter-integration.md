---
title: "Neovim Treesitter Integration"
type: concept
tags: [concept, neovim, treesitter, parsing, syntax-highlighting]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/treesitter.txt", "raw/nvim-docs/help.txt"]
confidence: high
---

## Definition

Neovim Treesitter Integration is the native embedding of the `tree-sitter` incremental parsing library into Neovim. It provides query-driven syntax highlighting, language injections, structural navigation, and code analysis by operating on concrete syntax trees rather than regular expressions.

## How It Works

1. **Parsers**: Tree-sitter parsers are shared libraries (`parser/{lang}.so`) discovered on `runtimepath`. Nvim bundles parsers for C, Lua, Markdown, Vimscript, Vimdoc, and query files.
2. **Incremental Parsing**: As the buffer changes, tree-sitter incrementally updates its syntax tree, recovering gracefully from errors.
3. **Queries**: Lisp-like `.scm` files in `queries/` define patterns over node types. A query consists of patterns, matches, captures (named nodes), and predicates (conditional filters).
4. **Highlights**: `highlights.scm` queries map AST nodes to capture names (e.g., `@variable.parameter`), which Nvim links to highlight groups. A fallback system lets specific captures fall back to generic ones.
5. **Language Injections**: `injections.scm` queries identify regions of embedded languages (e.g., `<script>` tags in HTML, Lua heredocs, Vimscript in `vim.cmd()`) and re-parse them with the appropriate parser.
6. **Lua API**: `vim.treesitter.language.add/register()`, `vim.treesitter.start()`, `vim.treesitter.query`, and `vim.treesitter.languagetree` provide programmatic access.

## Key Parameters

- `parser/{lang}.so` or `.wasm` (if built with `ENABLE_WASMTIME`): parser search path under `runtimepath`
- `queries/{lang}/{highlights,injections,locals,...}.scm`: query file locations
- `vim.treesitter.language.register(lang, {filetypes})`: associate filetypes with parsers
- Capture names: `@variable`, `@function`, `@keyword`, `@string`, etc. (see `treesitter-highlight-groups`)
- Predicates: `eq?`, `match?`, `lua-match?`, `contains?`, `any-of?`, `has-ancestor?`, `has-parent?`, plus negated variants

## When To Use

- Use tree-sitter highlighting instead of regex-based `syntax` for accuracy and performance on large files.
- Use language injections for polyglot files (HTML/JS/CSS, Markdown/code blocks).
- Use custom queries for domain-specific highlighting or structural search.

## Risks & Pitfalls

- **Experimental status**: Treesitter support is still experimental and APIs may change.
- **Parser availability**: A parser must be installed for each language; the `nvim-treesitter` plugin automates this.
- **Query precedence**: The first query on `runtimepath` wins; use `; extends` modeline to extend rather than replace bundled queries.
- **Injection performance**: Injection queries run over the entire buffer and can be slow for large files; disable with an empty `queries/c/injections.scm` if needed.
- **WASM parsers**: Only available if Nvim was built with `ENABLE_WASMTIME`.

## Related Concepts

- [[concepts/nvim-lsp-client]]
- [[entities/tree-sitter]]
- [[entities/nvim-treesitter]]

## Sources

- [Neovim Treesitter Reference](raw/nvim-docs/treesitter.txt)
- [Neovim Help Index](raw/nvim-docs/help.txt)
