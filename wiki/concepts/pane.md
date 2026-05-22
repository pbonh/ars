---
title: "Pane"
type: concept
tags: [concept, zellij, ui, terminal-multiplexer]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md", "raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

A pane is a rectangular subdivision of the terminal window that hosts a single terminal session (pty + shell/program). Panes are the fundamental unit of workspace organization in Zellij.

## How It Works

Each pane:
- Owns one pty pair (primary/secondary)
- Runs one shell or program
- Has an independent scroll-back buffer
- Receives focus independently
- Can be resized, moved, closed, or put into fullscreen

Panes are arranged via the [[concepts/layout-system|layout system]] and coordinated by the [[concepts/screen-zellij|Screen]].

## Key Parameters

- Position and size (x, y, width, height)
- Focus state
- Scroll-back buffer length
- Active program / shell

## When To Use

Create or manage panes when:
- Splitting the terminal to view multiple processes
- Organizing a workspace into logical regions
- Comparing outputs side-by-side

## Risks & Pitfalls

- Too many small panes make text unreadable.
- Pane content is lost on close unless explicitly saved.
- Resizing can truncate or wrap text in unexpected ways.

## Related Concepts

- [[concepts/tab]] — a collection of panes
- [[concepts/terminal-pane]] — the Zellij-specific implementation
- [[concepts/layout-system]] — how panes are arranged
- [[concepts/pane-boundaries]] — visual separators

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)
- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)