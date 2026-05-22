---
title: "Pi TUI Component"
type: concept
tags: [concept, pi, tui, terminal-ui, typescript]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/tui.md"]
confidence: high
---

## Definition

A Pi TUI component is a custom user-interface element rendered inside the terminal by an extension or custom tool. Components are built using the `@earendil-works/pi-tui` library and can receive keyboard input, display styled text, and support IME (Input Method Editor) cursor positioning.

## How It Works

1. A component implements the `Component` interface: `render(width)` returns an array of strings (one per line), each not exceeding `width`.
2. Optional `handleInput(data)` receives keyboard input when the component has focus.
3. Components implementing `Focusable` with a `CURSOR_MARKER` enable hardware cursor placement for IME support (critical for CJK input).
4. Container components (e.g., dialogs) must propagate focus state to child inputs.
5. The TUI appends SGR and OSC 8 resets at the end of each line; styles do not carry across lines.

## Key Parameters

- Library: `@earendil-works/pi-tui`
- Key method: `render(width: number): string[]`
- IME marker: `CURSOR_MARKER` (zero-width APC escape sequence)
- Focus propagation: required for containers embedding `Input` or `Editor`

## When To Use

Build a custom TUI component when:
- You need interactive dialogs, wizards, or selectors inside Pi.
- You want a custom input method with full keyboard control.
- You are building an extension that requires user interaction beyond simple confirm/input.

## Risks & Pitfalls

- Lines exceeding the requested `width` will break layout.
- Multi-line styled text must reapply styles per line or use `wrapTextWithAnsi()`.
- Missing focus propagation breaks IME cursor positioning in containers.
- Node `readline` is not protocol-compliant for RPC mode because it splits on Unicode separators (`U+2028`, `U+2029`).

## Related Concepts

- [[concepts/pi-extension]]
- [[concepts/pi-theme]]
- [[concepts/pi-custom-tool]]

## Sources

- [Pi TUI Components Documentation](raw/pi-repo/packages/coding-agent/docs/tui.md)
