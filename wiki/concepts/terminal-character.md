---
title: "Terminal Character"
type: concept
tags: [concept, zellij, terminal-emulator, rendering]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

A TerminalCharacter represents one cell in the terminal grid, holding both the Unicode character and its styling information.

## How It Works

Each character stores:
- The raw `char` value
- A `CharacterStyles` struct encoding foreground/background colors, bold, italic, underline, etc.

The struct derives `Copy` because it is moved frequently during line wrapping and buffer scrolling.

## Key Parameters

- `character`: the Unicode scalar value
- `styles`: the `CharacterStyles` bitset or struct

## When To Use

Relevant when:
- Adding new text styling capabilities (e.g., strikethrough, blink)
- Optimizing memory layout of the terminal grid
- Supporting wide characters (e.g., CJK, emoji)

## Risks & Pitfalls

- Because `Copy` is derived, adding heap-allocated fields (like `String`) will break the derive and degrade performance.
- Wide characters occupy two column cells; the grid must account for this.

## Related Concepts

- [[concepts/ansi-vt-stream]] — where style instructions originate
- [[concepts/scroll-buffer]] — the container holding TerminalCharacters

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)