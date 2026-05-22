---
title: "Terminal Pane"
type: concept
tags: [concept, zellij, architecture, terminal-emulator]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

A TerminalPane is a single on-screen pane that connects to one pty and hosts one shell or program. It is both a terminal emulator (parsing ANSI/VT) and a scroll-back buffer manager.

## How It Works

Each TerminalPane has two primary responsibilities:
1. **Scroll management** — maintains the viewport, cursor position, and line-wrapping state.
2. **ANSI/VT interpretation** — parses the byte stream from its pty to update character styles, cursor position, and buffer content.

The pane receives parsed events from the PtyBus and updates its internal grid accordingly.

## Key Parameters

- `pid`: process ID of the pty-backed process
- `scroll`: the internal scroll buffer holding terminal lines
- `grid`: the character grid that models the visible and scroll-back regions

## When To Use

Relevant when:
- Adding new terminal-emulation features (e.g., new escape sequences)
- Optimizing scroll-back performance
- Implementing pane-specific behaviors (e.g., search, copy mode)

## Risks & Pitfalls

- `TerminalCharacter` derives `Copy` for performance; be careful when adding large fields.
- ANSI/VT parsing is stateful relative to cursor position; style changes apply only to characters printed after the instruction.

## Related Concepts

- [[concepts/scroll-buffer]]
- [[concepts/terminal-character]]
- [[concepts/ansi-vt-stream]]
- [[concepts/pty]]

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)