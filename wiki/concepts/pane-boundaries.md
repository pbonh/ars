---
title: "Pane Boundaries"
type: concept
tags: [concept, zellij, ui, rendering]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/ARCHITECTURE.md"]
confidence: high
---

## Definition

Pane Boundaries are the visual lines drawn between adjacent terminal panes in the Zellij UI. They are composed of Unicode box-drawing characters.

## How It Works

The boundary renderer:
1. Queries each pane via the `Rect` trait for its position and dimensions.
2. Computes intersection points where panes meet.
3. Selects the appropriate Unicode box-drawing glyph for each intersection based on which sides have neighboring panes.

This produces T-junctions, corners, and straight segments automatically.

## Key Parameters

- Unicode box-drawing characters from U+2500 through U+257F
- `Rect` trait: `x`, `y`, `width`, `height`

## When To Use

Relevant when:
- Customizing the visual appearance of borders (e.g., rounded corners, double lines)
- Adding boundary interaction (e.g., drag-to-resize, click-to-focus)
- Supporting terminals that lack full box-drawing support

## Risks & Pitfalls

- Some terminal fonts render box-drawing characters at inconsistent widths, causing visual gaps.
- Boundary computation must be updated on every pane resize or creation.

## Related Concepts

- [[concepts/screen-zellij]] — triggers boundary redraws
- [[concepts/terminal-pane]] — provides `Rect` geometry

## Sources

- [Zellij Architecture](raw/zellij-repo/docs/ARCHITECTURE.md)