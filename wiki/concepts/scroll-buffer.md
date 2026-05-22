---
title: "Scroll Buffer"
type: concept
tags: [concept, zellij, terminal-emulator, buffer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

The Scroll holds the terminal buffer for a single TerminalPane. It tracks the viewport, cursor position, and line-wrapping behavior.

## How It Works

The Scroll is a ring-like or growable buffer of lines. It supports:
- **Viewport tracking** — which slice of the buffer is currently visible
- **Cursor tracking** — row and column of the insertion point
- **Line wrapping** — deciding when a line overflows the pane width

When the user scrolls up or down, only the viewport window moves; the underlying buffer is unchanged.

## Key Parameters

- `viewport`: start/end indices of the visible region
- `cursor_position`: current (row, col) in the buffer
- `lines`: the actual stored lines of text and styling

## When To Use

Relevant when:
- Implementing scroll-up/scroll-down keybindings
- Adding search or copy-mode features
- Tuning memory usage for long-running sessions with large scroll-back

## Risks & Pitfalls

- Unbounded scroll-back growth can consume significant memory over long sessions.
- Cursor position must stay consistent with viewport boundaries after resizes.

## Related Concepts

- [[concepts/terminal-pane]]
- [[concepts/terminal-character]]

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)