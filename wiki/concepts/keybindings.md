---
title: "Keybindings"
type: concept
tags: [concept, zellij, ux, configuration]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

Keybindings in Zellij map keyboard input to actions within the scope of an [[concepts/input-modes|input mode]]. They are fully user-configurable via YAML.

## How It Works

A keybinding entry contains:
- `action`: one or more Zellij actions (e.g., `NewPane`, `CloseTab`)
- `key`: one or more key descriptors (e.g., `Char: 'c'`, `Ctrl: 'p'`, `Alt: 'n'`)

Key descriptors include:
- `Char: <c>` — single character, no modifier
- `Alt: <c>` / `Ctrl: <c>` — character with modifier
- `F: <1-12>` — function keys
- Arrow keys, `Home`, `End`, `PageUp`, `PageDown`, `Backspace`, `Delete`, `Insert`, `Esc`

Default bindings can be unbound globally or per-mode.

## Key Parameters

- `keybinds.normal`, `keybinds.pane`, etc. — mode-scoped binding blocks
- `unbind: true` — removes all defaults for the scope

## When To Use

Customize keybindings when:
- Default bindings conflict with your editor or shell
- You want a reduced or expanded command palette
- You are porting muscle memory from another multiplexer

## Risks & Pitfalls

- Unbinding critical bindings (e.g., mode switch) can lock you out of Zellij.
- Binding a key in `normal` that is needed in a nested app requires using `locked` mode.

## Related Concepts

- [[concepts/input-modes]]
- [[concepts/terminal-multiplexer]]

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)