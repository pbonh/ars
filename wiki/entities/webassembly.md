---
title: "WebAssembly"
type: entity
tags: [entity, technology, plugin, wasi]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/zellij-repo/docs/MANPAGE.md"]
confidence: high
---

## Overview

WebAssembly (WASM) is a portable binary instruction format. Zellij's plugin system compiles plugins to WebAssembly targeting WASI (WebAssembly System Interface), enabling plugins to be written in any language that compiles to WASM.

## Characteristics

- Sandbox execution model
- Language-agnostic: Rust, C, AssemblyScript, etc.
- WASI provides limited system interfaces (filesystem, clocks, random)
- `.wasm` files are loaded via layout definitions

## Common Strategies

- Write plugins in Rust and compile with `wasm32-wasi` target
- Load plugins through layout files with `plugin: /path/to/plugin.wasm`
- Use built-in plugins (status-bar, strider, tab-bar) as reference implementations

## Sources

- [Zellij Manpage](raw/zellij-repo/docs/MANPAGE.md)