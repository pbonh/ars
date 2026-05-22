---
title: "Zellij Architecture"
type: summary
tags: [summary, zellij, architecture, terminal-multiplexer]
created: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
updated: 2026-05-21
confidence: high
---

## Overview

Zellij's server-side architecture is organized around a handful of core components that manage the terminal grid, pane lifecycle, and inter-process communication. The design follows a model where a central [[concepts/screen-zellij|Screen]] coordinates multiple [[concepts/terminal-pane|TerminalPane]] instances, each backed by a single pty. A [[concepts/pty-bus|PtyBus]] multiplexes byte streams from those ptys into structured ANSI/VT events that the Screen routes to the correct pane.

## Key Claims

- The Screen is the single coordinator for pane creation, destruction, and resizing.
- Each TerminalPane owns one pty, one scroll buffer, and one ANSI/VT parser.
- Character styling is stateful relative to the current cursor position, not global.
- Pane boundaries are drawn with Unicode box-drawing characters computed from adjacent pane geometries.

## Source Metadata

- **Type**: Markdown documentation
- **Owner**: Zellij Contributors (zellij-org/zellij)
- **URL**: https://github.com/zellij-org/zellij/tree/main/docs/ARCHITECTURE.md
- **License**: MIT
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/screen-zellij]]
- [[concepts/terminal-pane]]
- [[concepts/scroll-buffer]]
- [[concepts/terminal-character]]
- [[concepts/ansi-vt-stream]]
- [[concepts/pane-boundaries]]
- [[concepts/pty-bus]]
- [[concepts/pty]]