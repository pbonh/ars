---
title: "ANSI/VT Stream"
type: concept
tags: [concept, zellij, terminal, protocol]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md", "raw/zellij-repo/docs/TERMINOLOGY.md"]
confidence: high
---

## Definition

The ANSI/VT stream is the byte sequence emitted by the primary side of a pty that a terminal emulator consumes to draw characters, move the cursor, and change styling.

## How It Works

The stream interleaves plain text bytes with escape sequences:
- **CSI sequences** (Control Sequence Introducer) control emulator behavior: colors, cursor moves, clear-screen, etc.
- **OSC sequences** (Operating System Command) control OS-level features: window titles, etc.
- Plain text bytes are rendered at the current cursor position with the current active style.

Style changes are stateful and relative to the cursor: once a "red foreground" instruction is received, all subsequent characters are red until a reset or new line.

## Key Parameters

- Escape character: `\033` (0x1B)
- CSI prefix: `\033[`
- OSC prefix: `\033]`

## When To Use

Relevant when:
- Implementing new escape-sequence support in the TerminalPane parser
- Debugging why colors or cursor positions are wrong
- Writing terminal-emulation tests

## Risks & Pitfalls

- Not all programs emit well-formed sequences; the parser must be robust to partial or malformed input.
- Stateful style tracking means the parser must maintain a "current brush" state that resets on line boundaries.

## Related Concepts

- [[concepts/csi]]
- [[concepts/osc]]
- [[concepts/terminal-character]] — the unit being styled
- [[concepts/pty]] — the source of the stream

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)
- [Zellij Terminology](raw/zellij-repo/docs/TERMINOLOGY.md)