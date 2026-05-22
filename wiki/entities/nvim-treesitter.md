---
title: "nvim-treesitter"
type: entity
tags: [entity, plugin, neovim, treesitter]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/treesitter.txt"]
confidence: high
---

## Overview

nvim-treesitter is a community Neovim plugin that simplifies installation, updating, and management of tree-sitter parsers and queries. It wraps Neovim's native treesitter APIs and provides convenient commands for parser lifecycle management.

## Characteristics

- Automates parser installation from upstream grammar repos
- Provides `:TSInstall`, `:TSUpdate`, and `:TSUninstall` commands
- Supports query and parser consistency checks
- Often used as a dependency by colorschemes and language-specific plugins

## Common Strategies

- Install via package manager and run `:TSInstall <lang>` to add parsers
- Use `:TSUpdate` after Neovim upgrades to keep parsers compatible
- Configure `highlight = { enable = true }` to activate tree-sitter highlighting per language
- Extend with modules like `textobjects`, `refactor`, or `playground` for advanced usage

## Sources

- [Neovim Treesitter Reference](raw/nvim-docs/treesitter.txt)
