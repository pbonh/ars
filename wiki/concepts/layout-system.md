---
title: "Layout System"
type: concept
tags: [concept, zellij, configuration, ui]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

Zellij's layout system is a YAML-based declarative grammar for describing the initial arrangement of panes, their split directions, sizes, and optional plugin loads.

## How It Works

A layout file is a nested tree where each node is either:
- A **pane** (leaf): runs a shell or program
- A **split** (branch): divides space horizontally or vertically into child nodes

Each node supports:
- `direction`: `Horizontal` or `Vertical`
- `split_size`: `Percent: 1-100` or `Fixed: <lines>`
- `plugin`: path to a compiled `.wasm` plugin
- `default_fg` / `default_bg`: pane colors

## Key Parameters

- `default_layout`: config option for the layout loaded at startup
- `--layout`: CLI flag to load a specific layout file
- Layout search path: `layouts/` subdirectory of the config directory

## When To Use

Define layouts when:
- You have a recurring workspace setup (e.g., editor + terminal + log viewer)
- You want plugins pre-loaded in specific panes
- You want to share workspace templates with a team

## Risks & Pitfalls

- Percent splits must sum to 100 at each level; the parser does not validate this.
- Plugin paths are relative to the layout file or the plugin directory.
- Fixed splits can overflow if the terminal is resized below the fixed size.

## Related Concepts

- [[concepts/pane]]
- [[concepts/plugin-system]]
- [[concepts/terminal-multiplexer]]

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)