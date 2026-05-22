---
title: "tmux"
type: entity
tags: [entity, tool, terminal-multiplexer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Overview

tmux is a popular terminal multiplexer. Zellij provides a `tmux` input mode that emulates common tmux keybindings to ease migration for users with existing tmux muscle memory.

## Characteristics

- Session-based with attach/detach
- Pane and window management
- Client-server architecture
- Text-based status bar
- Widely available on Unix systems

## Common Strategies

- Switch to `tmux` mode in Zellij for familiar keybindings
- Use tmux for remote session persistence
- Compare Zellij layouts to tmux window layouts when evaluating migration

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)