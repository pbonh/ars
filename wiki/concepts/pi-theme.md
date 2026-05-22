---
title: "Pi Theme"
type: concept
tags: [concept, pi, theming, terminal, json]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/themes.md"]
confidence: high
---

## Definition

A Pi theme is a JSON file that defines color tokens for the Pi TUI, enabling customization of the terminal interface's appearance.

## How It Works

1. The user creates a JSON file with a `$schema` reference, a `name`, and a `vars` object mapping color tokens to values.
2. Pi loads themes from built-in (`dark`, `light`), global (`~/.pi/agent/themes/`), project (`.pi/themes/`), packages, or explicit CLI paths.
3. On first run, Pi detects the terminal background and defaults to `dark` or `light`.
4. The active theme is selected via `/settings` or `settings.json`.

## Key Parameters

- Token values: hex strings (`#00aaff`), 256-color indices (0–255), or ANSI names (`black`, `red`, etc.)
- Required tokens: `primary`, `secondary`, `background`, `foreground`, `accent`, `error`, `success`, `warning`, `info`, `muted`
- Discovery paths: `~/.pi/agent/themes/*.json`, `.pi/themes/*.json`

## When To Use

Create a custom theme when:
- You want Pi to match your terminal or desktop color scheme.
- You need higher contrast or accessibility-focused colors.
- You are distributing a Pi package that includes a branded theme.

## Risks & Pitfalls

- Missing required tokens cause rendering issues.
- 256-color indices may render differently across terminals.
- Themes do not affect the underlying terminal emulator, only Pi's own UI chrome.

## Related Concepts

- [[concepts/pi-tui-component]]
- [[concepts/pi-package]]

## Sources

- [Pi Themes Documentation](raw/pi-repo/packages/coding-agent/docs/themes.md)
