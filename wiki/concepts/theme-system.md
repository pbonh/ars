---
title: "Theme System"
type: concept
tags: [concept, zellij, ui, theming]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

Zellij's theme system allows users to define color palettes in truecolor, 256-color, or hex format, and assign them to UI elements and pane defaults.

## How It Works

Themes are declared in the configuration file under a `themes` block. Each theme defines colors for:
- `fg` / `bg`: default foreground and background
- Standard palette colors: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `orange`

Color formats:
- Truecolor: `fg: [0, 0, 0]` (RGB triplet)
- 256-color: `fg: 0` (index)
- Hex: `fg: "#000000"`

The theme named `default` is loaded automatically; others are selected via `--theme` or the `theme:` config option.

## Key Parameters

- `default_fg` / `default_bg`: per-pane overrides in layouts
- `theme: <name>`: global config option
- `--theme <name>`: CLI override

## When To Use

Define themes when:
- You want Zellij to match your terminal or editor color scheme
- You need high-contrast or accessibility-focused palettes
- You want different themes for different environments (e.g., prod vs. dev)

## Risks & Pitfalls

- Not all terminals support truecolor; fallback to 256-color may be needed.
- Hex shorthand (`#000`) may not be supported by all config parsers.

## Related Concepts

- [[concepts/layout-system]] — per-pane color overrides
- [[concepts/terminal-multiplexer]] — the tool being themed

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)