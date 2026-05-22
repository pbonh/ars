---
title: "Plugin System"
type: concept
tags: [concept, zellij, webassembly, extensibility]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Definition

Zellij's plugin system is a WebAssembly-based extension framework that allows developers to write plugins in any language compiling to WASI, load them into panes, and interact with the Zellij runtime.

## How It Works

1. A plugin is compiled to a `.wasm` file targeting WASI.
2. The plugin path is referenced in a layout file.
3. Zellij instantiates the WASM module inside a WASI sandbox.
4. The plugin communicates with Zellij via a defined API (events, commands, state queries).

Built-in plugins: status-bar, strider, tab-bar.

## Key Parameters

- Plugin directory: `$XDG_DATA_HOME/zellij/plugins`
- WASI target: `wasm32-wasi`
- Layout integration: `plugin: /path/to/plugin.wasm`

## When To Use

Write a plugin when:
- You need custom UI chrome (e.g., a custom status line)
- You want to integrate external tools (e.g., file browser, git dashboard)
- You want to automate Zellij behavior (e.g., auto-layout, session management)

## Risks & Pitfalls

- WASI sandboxing limits file system and network access; plan accordingly.
- Plugin API stability is not guaranteed across Zellij versions.
- Performance-critical plugins may hit WASM overhead.

## Related Concepts

- [[concepts/layout-system]]
- [[entities/webassembly]]
- [[concepts/pane]]

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)