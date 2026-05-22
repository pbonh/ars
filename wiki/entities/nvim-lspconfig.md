---
title: "nvim-lspconfig"
type: entity
tags: [entity, plugin, neovim, lsp]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lsp.txt"]
confidence: high
---

## Overview

nvim-lspconfig is a community-maintained Neovim plugin that provides pre-made LSP server configurations. It sits on top of Neovim's built-in `vim.lsp` client and supplies ready-to-use `lsp/<server>.lua` configs for dozens of language servers.

## Characteristics

- Officially hosted under the `neovim` GitHub organization
- Provides `lsp/*.lua` configs for 100+ language servers
- Automatically sets `cmd`, `filetypes`, and `root_markers` per server
- Can be used as-is or overridden via `after/lsp/` or `vim.lsp.config()`

## Common Strategies

- Install via package manager (lazy.nvim, packer, etc.)
- Enable a config with `vim.lsp.enable('lspconfig_server_name')` or let the plugin handle it
- Override defaults in `after/lsp/<server>.lua` to customize `root_markers` or `settings`
- Use as a reference when writing your own minimal `lsp/<server>.lua` configs

## Sources

- [Neovim LSP Reference](raw/nvim-docs/lsp.txt)
