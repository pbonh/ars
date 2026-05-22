---
title: "Pty (Pseudoterminal)"
type: concept
tags: [concept, zellij, terminal, linux, unix]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md", "raw/zellij-repo/docs/TERMINOLOGY.md"]
confidence: high
---

## Definition

A pty (pseudoterminal) is a character device that emulates a traditional terminal. It is a bidirectional communication channel split into a primary (emulator) side and a secondary (program) side.

## How It Works

In Zellij:
- The **primary** side is read by the [[concepts/pty-bus|PtyBus]], which parses the ANSI/VT byte stream.
- The **secondary** side is connected to the shell or program running inside a pane.
- One pty pair is created per terminal pane.

The pty abstraction allows Zellij to host real terminal programs (like `bash`, `vim`, `htop`) without them knowing they are inside a multiplexer.

## Key Parameters

- Device path: `/dev/pts/<N>` on Linux
- Primary side: read by Zellij's PtyBus
- Secondary side: standard input/output of the hosted program

## When To Use

Relevant when:
- Adding support for alternative pty backends (e.g., ConPTY on Windows)
- Debugging why a program does not detect terminal capabilities
- Tuning pty buffer sizes for performance

## Risks & Pitfalls

- Pty allocation can fail under resource pressure (max pty limit).
- Programs that query terminal dimensions via TIOCGWINSZ need the pty size kept in sync with the pane size.
- Not all platforms support Unix ptys (e.g., native Windows before ConPTY).

## Related Concepts

- [[concepts/terminal-pane]] — the Zellij component backed by one pty
- [[concepts/pty-bus]] — the multiplexer reading from ptys
- [[concepts/ansi-vt-stream]] — the data flowing through the pty

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)
- [Zellij Terminology](raw/zellij-repo/docs/TERMINOLOGY.md)