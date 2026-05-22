---
title: "Tab"
type: concept
tags: [concept, zellij, ui, workspace]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

A tab in Zellij is a named workspace containing a set of panes. Tabs allow users to maintain multiple independent layouts within a single session.

## How It Works

Each tab:
- Has a unique index and optional name
- Contains its own pane layout
- Can be switched to via keybindings or commands
- Supports operations: create, close, rename, reorder
- Can optionally sync input across all its panes (`ToggleActiveSyncTab`)

## Key Parameters

- `tab_index`: zero-based position
- `name`: optional display name
- `active_sync`: whether keystrokes are broadcast to all panes

## When To Use

Use tabs when:
- One layout is not enough for your workflow
- You want context separation (e.g., "frontend", "backend", "logs")
- You want to preserve pane arrangements while switching contexts

## Risks & Pitfalls

- Closing a tab destroys all its panes and their running processes.
- Tab names are not globally unique; they are per-session.

## Related Concepts

- [[concepts/pane]] — the units inside a tab
- [[concepts/session]] — the container holding tabs
- [[concepts/layout-system]] — defines the pane arrangement per tab

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)