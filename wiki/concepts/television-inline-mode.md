---
title: "Television Inline Mode"
type: concept
tags: [concept, fuzzy-finder, ui, embedding]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

**Inline mode** is a non-fullscreen display mode where Television renders as a widget at the bottom of the terminal, using only the available empty space rather than taking over the entire screen.

## How It Works

When `--inline` is passed, Television computes the available bottom space and renders the picker there. If there is insufficient space, the terminal scrolls to accommodate the minimum height. Additional flags constrain the dimensions:

- `--height 15` — fixed height in lines.
- `--width 80` — fixed width in columns (must be combined with `--inline` or `--height`).

Inline mode respects all other UI settings (preview panel, layout, scaling, borders) within the constrained rectangle.

## Key Parameters

| Flag | Description |
|------|-------------|
| `--inline` | Enable inline rendering at the bottom of the terminal. |
| `--height <N>` | Set a fixed height in lines. |
| `--width <N>` | Set a fixed width in columns. |

## When To Use

Use inline mode when embedding Television inside scripts, tmux panes, or other UI contexts where a fullscreen takeover would be disruptive. It is also useful for quick selections that need to leave prior terminal output visible.

## Risks & Pitfalls

- If the terminal is too small, inline mode may force a scroll, which can break visual context in split-pane layouts.
- Preview panels may be cramped in inline mode with a small height; consider hiding the preview (`--no-preview`) or reducing preview size.
- Inline mode combined with `--ui-scale` interacts in non-obvious ways; test the exact terminal geometry before deploying in scripts.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-watch-mode]]

## Sources

- Television docs: Tips and tricks (inline mode), CLI reference.
