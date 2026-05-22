---
title: "Session"
type: concept
tags: [concept, zellij, workspace, persistence]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

A session in Zellij is a named, persistent workspace that survives client detachment. It contains one or more tabs, each with its own pane layout.

## How It Works

Sessions are managed by the Zellij server process:
- `zellij` creates a new session
- `zellij list-sessions` shows active sessions
- `zellij attach <name>` reconnects to an existing session
- `Detach` action disconnects the client while leaving the session running

The server keeps all ptys, pane states, and scroll buffers alive even when no client is attached.

## Key Parameters

- Session name: unique identifier
- Server process: the daemon holding session state
- Client: the terminal UI that attaches to the server

## When To Use

Use sessions when:
- Running long-lived tasks (builds, servers, log tails)
- Working remotely over SSH
- Maintaining persistent workspace state across reboots or disconnections

## Risks & Pitfalls

- Orphaned sessions consume resources indefinitely.
- Session names are not namespaced; attaching to the wrong name creates a new session.
- Server crashes lose all session state.

## Related Concepts

- [[concepts/tab]] — the pages within a session
- [[concepts/pane]] — the units within a tab
- [[concepts/terminal-multiplexer]] — the category of tool

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)