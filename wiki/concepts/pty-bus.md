---
title: "Pty Bus"
type: concept
tags: [concept, zellij, architecture, ipc]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

The PtyBus is a multiplexer that reads from multiple pty sockets concurrently, parses the raw bytes into ANSI/VT events, and routes those events to the correct TerminalPane in the Screen.

## How It Works

The PtyBus maintains a set of asynchronous readers, one per pty socket (e.g., `/dev/pts/999`). As bytes arrive:
1. The reader parses the byte stream into structured ANSI/VT events.
2. The event is tagged with the originating pty identifier.
3. The event is sent to the Screen, which dispatches it to the associated TerminalPane.

This decouples the pty I/O layer from the terminal-emulation layer.

## Key Parameters

- `pty_readers`: the set of active pty sockets
- `senders`: IPC channels to the Screen

## When To Use

Relevant when:
- Adding support for new pty types or backends
- Debugging why a pane is not receiving output
- Optimizing I/O throughput for many concurrent panes

## Risks & Pitfalls

- The PtyBus must handle ptys being created and destroyed dynamically (pane open/close).
- Blocking on a single slow pty can stall the entire bus; async I/O is critical.

## Related Concepts

- [[concepts/pty]] — the underlying pseudoterminal device
- [[concepts/screen-zellij]] — the destination for parsed events
- [[concepts/ansi-vt-stream]] — the payload being routed

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)