---
title: "CSI (Control Sequence Identifier)"
type: concept
tags: [concept, zellij, terminal, protocol]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/TERMINOLOGY.md"]
confidence: high
---

## Definition

CSI (Control Sequence Introducer) is a sub-protocol of ANSI/VT that carries instructions for the terminal emulator, such as color changes, cursor movement, and screen clearing.

## How It Works

CSI sequences start with the escape character (`\033`) followed by `[` and one or more parameters terminated by a command letter:
- `\033[31m` — set foreground color to red
- `\033[2J` — clear screen
- `\033[H` — move cursor to home position

The TerminalPane parser splits the byte stream into these sequences and updates its internal grid state accordingly.

## Key Parameters

- Prefix: `ESC [` (0x1B 0x5B)
- Parameters: semicolon-separated numeric values
- Final byte: command character (e.g., `m`, `J`, `H`)

## When To Use

Relevant when:
- Adding new escape-sequence support to the emulator
- Debugging why colors or cursor positioning are incorrect
- Writing terminal tests that verify CSI parsing

## Risks & Pitfalls

- Sequences can be incomplete if the pty sends partial data; the parser must handle fragmentation.
- Some sequences have conflicting interpretations across terminal emulators.

## Related Concepts

- [[concepts/ansi-vt-stream]] — the stream containing CSI sequences
- [[concepts/osc]] — the OS-command counterpart
- [[concepts/terminal-character]] — the unit affected by CSI styling

## Sources

- [Zellij Terminology](raw/zellij-repo/docs/TERMINOLOGY.md)