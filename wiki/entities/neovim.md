---
title: "Neovim"
type: entity
tags: [entity, tool, text-editor, vim-fork]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/help.txt"]
confidence: high
---

## Overview

Neovim is a hyperextensible, Vim-based text editor focused on modern extensibility, usability, and embeddability. It is a community-driven fork of Vim that re-architected the plugin and configuration model around Lua, built-in LSP, tree-sitter, and async job control, while maintaining backward compatibility with Vimscript.

## Characteristics

- Fork of Vim with active community governance
- First-class Lua 5.1 scripting with optional LuaJIT
- Built-in LSP client framework (`vim.lsp`)
- Native tree-sitter integration for incremental parsing
- Async job control and MessagePack-RPC API
- Cross-platform (Linux, macOS, Windows, BSD)
- Terminal UI (TUI) and external GUI support via UI protocol
- Extensive remote plugin support (Python, Ruby, Perl, etc.)

## Common Strategies

- Configure via `init.lua` instead of `init.vim` for new setups
- Define LSP configs in `lsp/<server>.lua` and enable with `vim.lsp.enable()`
- Use `vim.system()` for async shell integration
- Prefer tree-sitter highlighting over legacy regex syntax
- Extend via Lua coroutines and closures for complex plugins
- Use `:checkhealth` to diagnose LSP, treesitter, and provider issues

## Sources

- [Neovim Help Index](raw/nvim-docs/help.txt)
