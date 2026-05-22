---
title: "Zellij Manpage"
type: summary
tags: [summary, zellij, user-guide, terminal-multiplexer]
created: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
updated: 2026-05-21
confidence: high
---

## Overview

Zellij is a terminal workspace and multiplexer that targets developers and ops users. Beyond basic pane/tabs/session management (like [[entities/tmux|tmux]] or [[entities/gnu-screen|screen]]), it adds a YAML-based [[concepts/layout-system|layout system]], a WebAssembly plugin framework, configurable [[concepts/input-modes|input modes]], and a [[concepts/theme-system|theme system]]. Configuration is hierarchical: CLI flags override environment variables, which override the default config file.

## Key Claims

- Layouts are nested trees of panes with directional splits and optional plugin loads.
- Keybindings are mode-scoped (normal, locked, pane, tab, resize, scroll, session, tmux, renametab, renamepane).
- Plugins compile to WASI and are loaded via layout files; built-in plugins include status-bar, strider, and tab-bar.
- The manpage is a concise offline reference; canonical docs live at https://zellij.dev/documentation.

## Source Metadata

- **Type**: Manpage source (Markdown)
- **Owner**: Zellij Contributors
- **URL**: https://github.com/zellij-org/zellij/tree/main/docs/MANPAGE.md
- **License**: MIT
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/terminal-multiplexer]]
- [[concepts/layout-system]]
- [[concepts/plugin-system]]
- [[concepts/input-modes]]
- [[concepts/keybindings]]
- [[concepts/pane]]
- [[concepts/tab]]
- [[concepts/session]]
- [[concepts/theme-system]]

## Relevant Entities

- [[entities/zellij]]
- [[entities/tmux]]
- [[entities/gnu-screen]]
- [[entities/webassembly]]