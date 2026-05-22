---
title: "OSC (Operating System Command)"
type: concept
tags: [concept, zellij, terminal, protocol]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/TERMINOLOGY.md"]
confidence: high
---

## Definition

OSC (Operating System Command) is a sub-protocol of ANSI/VT that carries instructions for the underlying operating system or terminal window manager, such as changing the window title.

## How It Works

OSC sequences start with the escape character (`\033`) followed by `]` and a command number, then parameters, and end with `BEL` (`\007`) or `ST` (`\033\\`):
- `\033]0;My Title\007` — set window title

Unlike CSI, OSC does not affect the terminal grid directly; it is a side channel to the OS.

## Key Parameters

- Prefix: `ESC ]` (0x1B 0x5D)
- Command number: e.g., `0` for title, `8` for hyperlink
- Terminator: BEL or ST

## When To Use

Relevant when:
- Implementing window-title updates from running programs
- Supporting hyperlink annotations (OSC 8)
- Debugging why OSC sequences are not being passed through

## Risks & Pitfalls

- OSC sequences are often stripped by terminal multiplexers or SSH clients.
- Some OSC commands have security implications (e.g., arbitrary code execution via clipboard).

## Related Concepts

- [[concepts/ansi-vt-stream]] — the stream containing OSC sequences
- [[concepts/csi]] — the emulator-control counterpart

## Sources

- [Zellij Terminology](raw/zellij-repo/docs/TERMINOLOGY.md)