---
title: "Screen (Zellij)"
type: concept
tags: [concept, zellij, architecture, terminal-multiplexer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

The Screen is the top-level server-side component in Zellij responsible for coordinating all on-screen panes. It mediates pane lifecycle and spatial layout.

## How It Works

The Screen receives instructions (e.g., from IPC messages or user input) and translates them into pane mutations:
- Resizing panes in response to terminal dimension changes
- Creating new panes at specified positions
- Closing panes and redistributing their space to neighbors

It does not directly render to the terminal; instead it delegates to individual TerminalPane instances.

## Key Parameters

- `max_panes`: limits the total number of panes allowed in a session
- `screen_bus`: the IPC bus through which the Screen receives instructions

## When To Use

Understanding the Screen is essential when:
- Implementing new pane layout policies
- Debugging why a resize or split did not produce expected results
- Extending Zellij with new pane-management commands

## Risks & Pitfalls

- The Screen is not thread-safe by itself; it lives inside a dedicated thread (`screen_thread_main`) and all mutations are serialized through the bus.
- Adding new pane operations requires updating both the Screen's internal state and the boundary-drawing logic.

## Related Concepts

- [[concepts/terminal-pane]] — each pane the Screen manages
- [[concepts/pane-boundaries]] — the visual borders between panes
- [[concepts/pty-bus]] — the stream multiplexer feeding the Screen

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)