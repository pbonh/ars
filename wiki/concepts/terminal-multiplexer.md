---
title: "Terminal Multiplexer"
type: concept
tags: [concept, zellij, terminal, infrastructure]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

A terminal multiplexer is a program that multiplexes a single physical terminal into multiple virtual terminals (panes or windows), allowing users to run multiple shell sessions side-by-side and persist them across disconnections.

## How It Works

The multiplexer:
1. Creates pseudoterminals (ptys) for each pane.
2. Intercepts the output streams from each pty.
3. Renders the combined output into a single terminal window, adding borders and UI chrome.
4. Forwards user keystrokes to the focused pane.
5. Persists sessions so they survive SSH disconnects or local terminal closure.

## Key Parameters

- Panes: the subdivisions of the terminal window
- Tabs: collections of panes that can be switched between
- Sessions: named persistent workspaces
- Attach/detach: connecting to or disconnecting from a running session

## When To Use

Use a terminal multiplexer when:
- Running long-lived processes that must survive terminal closure
- Working with multiple shells or logs simultaneously
- Pair-programming or sharing a terminal session

## Risks & Pitfalls

- Keybinding conflicts between the multiplexer and nested terminal applications.
- Resource leaks if sessions are left running indefinitely.
- Complex layouts can become hard to navigate without muscle memory.

## Related Concepts

- [[concepts/pane]]
- [[concepts/tab]]
- [[concepts/session]]
- [[concepts/layout-system]]

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)