---
title: "Pi Extension"
type: concept
tags: [concept, pi, extensibility, typescript]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/extensions.md"]
confidence: high
---

## Definition

A Pi extension is a TypeScript module that extends the behavior of the Pi coding agent by subscribing to lifecycle events, registering custom tools, adding slash commands, rendering custom UI, and persisting state across sessions.

## How It Works

1. The user writes a TypeScript file that exports a default function receiving an `ExtensionAPI` object.
2. The extension calls `pi.on(event, handler)` to intercept events (e.g., `tool_call`, `session_start`).
3. It can register custom LLM-callable tools via `pi.registerTool()`, custom slash commands via `pi.registerCommand()`, and custom TUI components via `ctx.ui.custom()`.
4. Pi auto-discovers extensions in `~/.pi/agent/extensions/` and `.pi/extensions/`, or loads explicit paths via `-e`.
5. Extensions in auto-discovered directories support hot-reload with `/reload`.

## Key Parameters

- Discovery paths: `~/.pi/agent/extensions/`, `.pi/extensions/`
- API types: `@earendil-works/pi-coding-agent`
- Event categories: resource, session, agent, model, tool
- State persistence: `pi.appendEntry()` writes to the JSONL session

## When To Use

Write an extension when:
- You need the agent to call a custom external API or tool.
- You want to gate dangerous commands (e.g., confirm before `rm -rf`).
- You need custom TUI interactions (wizards, selectors, dialogs).
- You want to modify or block tool calls dynamically.
- You need to store state that survives session restarts.

## Risks & Pitfalls

- Extensions execute arbitrary code with full system access; review before installing third-party extensions.
- Blocking events with `{ block: true }` can silently suppress agent actions if overused.
- Custom tools must validate parameters carefully; the LLM may supply unexpected inputs.
- Hot-reload only works for auto-discovered locations, not for `-e` quick tests.

## Related Concepts

- [[concepts/pi-custom-tool]]
- [[concepts/pi-tui-component]]
- [[concepts/pi-package]]
- [[concepts/pi-skill]]

## Sources

- [Pi Extensions Documentation](raw/pi-repo/packages/coding-agent/docs/extensions.md)
