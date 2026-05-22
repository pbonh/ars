---
title: "Neovim Core Documentation"
type: summary
tags: [summary, neovim, text-editor, lua, lsp, treesitter]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/help.txt", "raw/nvim-docs/lua.txt", "raw/nvim-docs/lsp.txt", "raw/nvim-docs/treesitter.txt"]
confidence: high
---

## Overview

Neovim is a hyperextensible Vim-based text editor that distinguishes itself from Vim through first-class Lua scripting, a built-in LSP client framework, native tree-sitter integration, and an async job-control system. These four plain-text reference files (`help.txt`, `lua.txt`, `lsp.txt`, `treesitter.txt`) from the Neovim runtime documentation describe the core architecture and APIs that enable modern IDE-like features within a terminal editor.

## Key Claims

- Neovim embeds Lua 5.1 as its primary configuration and scripting language, providing a comprehensive `vim.*` standard library that bridges seamlessly to Vimscript variables, functions, options, and the underlying C API. [[concepts/nvim-lua-scripting]]
- Neovim ships a built-in LSP client (`vim.lsp`) with a config-driven activation model: define a config via `vim.lsp.config()`, enable it with `vim.lsp.enable()`, and attach buffer-local features through the `LspAttach` autocommand. [[concepts/nvim-lsp-client]]
- Neovim integrates the `tree-sitter` library for incremental parsing, using query-based predicates and captures to drive syntax highlighting, language injections, and structural navigation. [[concepts/nvim-treesitter-integration]]
- Neovim provides async job control via `vim.system()` and channel-based RPC, allowing Lua scripts to spawn processes, communicate over pipes, and interact with external tools without blocking the editor. [[concepts/nvim-async-jobs]]
- The diagnostic framework (`vim.diagnostic`) unifies error/warning display from LSP servers, linters, and custom sources, with namespaces, configurable signs, and floating windows. [[concepts/nvim-diagnostic-framework]]

## Source Metadata

- **Type**: Vim help files (plain text with `*tags*`)
- **Owner**: Neovim project (https://github.com/neovim/neovim)
- **URL**: https://neovim.io/doc/user/ (HTML rendering); raw files from `runtime/doc/`
- **License**: Apache 2.0 / Vim license
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/nvim-lua-scripting]]
- [[concepts/nvim-lsp-client]]
- [[concepts/nvim-treesitter-integration]]
- [[concepts/nvim-async-jobs]]
- [[concepts/nvim-diagnostic-framework]]

## Relevant Entities

- [[entities/neovim]]
- [[entities/tree-sitter]]
- [[entities/luajit]]
- [[entities/nvim-lspconfig]]
- [[entities/nvim-treesitter]]
