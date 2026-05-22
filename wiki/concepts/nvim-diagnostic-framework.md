---
title: "Neovim Diagnostic Framework"
type: concept
tags: [concept, neovim, diagnostics, lsp, error-reporting]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lsp.txt", "raw/nvim-docs/help.txt"]
confidence: high
---

## Definition

The Neovim Diagnostic Framework (`vim.diagnostic`) is a unified subsystem for displaying errors, warnings, hints, and information from arbitrary sources — primarily LSP servers, but also linters, compilers, and custom plugins. It provides namespaces, configurable signs, virtual text, underlines, floating windows, and location-list integration.

## How It Works

1. **Namespaces**: Each diagnostic source uses a dedicated namespace (`vim.api.nvim_create_namespace()`) so that multiple sources can annotate the same buffer without collisions.
2. **LSP Integration**: By default, LSP clients publish diagnostics via `textDocument/publishDiagnostics`, which Nvim routes into `vim.diagnostic` using a per-client namespace.
3. **Display**: Diagnostics are rendered via signs (gutter icons), virtual text (end-of-line messages), underlines (highlighted text ranges), and floating windows (`vim.diagnostic.open_float()`).
4. **Configuration**: `vim.diagnostic.config()` controls severity sorting, virtual text format, signs, update events, and jump behavior.
5. **API**: `vim.diagnostic.set()`, `vim.diagnostic.get()`, `vim.diagnostic.goto_next()`, `vim.diagnostic.hide/show()`, and `vim.diagnostic.reset()`.

## Key Parameters

- `namespace`: integer ID isolating one source from another
- `severity`: `ERROR`, `WARN`, `INFO`, `HINT` (or 1–4)
- `source`: string identifying the origin (e.g., "lua-language-server")
- `lnum`, `col`, `end_lnum`, `end_col`: buffer position of the diagnostic
- `message`: human-readable description
- `vim.diagnostic.config()`: global display settings

## When To Use

- Use for any code-analysis tool that produces location-tagged messages.
- Use LSP diagnostics for semantic analysis (type errors, unused variables).
- Use custom namespaces for linters or build tools that output line/column data.

## Risks & Pitfalls

- **Namespace hygiene**: Forgetting to reset or clear a namespace on buffer change can leave stale diagnostics.
- **Severity overload**: Too many `INFO`/`HINT` virtual-text items clutter the view; filter by severity in `vim.diagnostic.config()`.
- **Multiple sources**: Different LSP servers may report conflicting diagnostics for the same line; namespaces keep them separate but visual overlap can occur.
- **Performance**: Large workspaces with aggressive file-watching can flood diagnostics; throttle or debounce in `LspProgress` handlers if needed.

## Related Concepts

- [[concepts/nvim-lsp-client]]
- [[concepts/nvim-treesitter-integration]]
- [[entities/neovim]]

## Sources

- [Neovim LSP Reference (diagnostics)](raw/nvim-docs/lsp.txt)
- [Neovim Help Index](raw/nvim-docs/help.txt)
