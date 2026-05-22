---
title: "Zellij"
type: entity
tags: [entity, tool, terminal-multiplexer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md", "raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Overview

Zellij is a terminal workspace and multiplexer aimed at developers, ops-oriented users, and terminal enthusiasts. At its core it is a terminal multiplexer (similar to [[entities/tmux|tmux]] and [[entities/gnu-screen|GNU Screen]]), but it adds a [[concepts/layout-system|layout system]], a [[concepts/plugin-system|WebAssembly plugin system]], configurable [[concepts/input-modes|input modes]], and a [[concepts/theme-system|theme system]].

## Characteristics

- Written in Rust
- Open source (MIT license)
- Cross-platform (Linux, macOS)
- Session-based persistence with attach/detach
- WebAssembly plugin framework (WASI)
- YAML configuration and layouts

## Common Strategies

- Start with `zellij` to create a new session
- Use `zellij attach <name>` to reconnect
- Define recurring workspace layouts in `~/.config/zellij/layouts/`
- Use `locked` mode when nested applications conflict with default bindings
- Install via package managers (Homebrew, pacman, cargo) or build from source

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)
- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)