---
title: "Input Modes"
type: concept
tags: [concept, zellij, ux, keybindings]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

Input modes in Zellij are named keyboard contexts that define which keybindings are active. Switching modes changes the available commands without requiring modifier chords.

## How It Works

Zellij ships with these modes:
- **normal**: default mode; provides navigation and mode-switching shortcuts
- **locked**: disables all bindings except unlock (Ctrl+g by default); for nested apps
- **tmux**: emulates common tmux keybindings
- **pane**: pane creation, movement, closing
- **tab**: tab creation, switching, closing
- **resize**: directional pane resizing
- **scroll**: scrollback navigation
- **session**: detach from session
- **renametab** / **renamepane**: hidden modes triggered by `SwitchToMode`

Modes are defined in the `keybinds` section of the config file.

## Key Parameters

- `SwitchToMode: <ModeName>` action to change modes
- `locked` mode default unlock key: `Ctrl+g`

## When To Use

Relevant when:
- Customizing the keyboard workflow
- Avoiding conflicts with nested terminal applications (use `locked`)
- Migrating from tmux (use `tmux` mode)

## Risks & Pitfalls

- Forgetting which mode you're in leads to unexpected key behavior.
- Overlapping keybindings across modes can cause accidental actions.

## Related Concepts

- [[concepts/keybindings]]
- [[concepts/pane]]
- [[concepts/tab]]

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)