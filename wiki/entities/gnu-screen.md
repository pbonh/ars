---
title: "GNU Screen"
type: entity
tags: [entity, tool, terminal-multiplexer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Overview

GNU Screen is the original terminal multiplexer. Zellij lists it alongside tmux as a comparable infrastructure-layer tool, though Screen predates both tmux and Zellij by decades.

## Characteristics

- Session persistence with attach/detach
- Window (tab) management
- Copy mode and scrollback
- Minimal UI chrome
- Ubiquitous on Unix systems

## Common Strategies

- Use Screen when only basic session persistence is needed
- Prefer Zellij or tmux for modern pane layouts and plugin extensibility

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)