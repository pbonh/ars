---
title: "LuaJIT"
type: entity
tags: [entity, tool, lua, jit-compiler]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lua.txt"]
confidence: high
---

## Overview

LuaJIT is a high-performance Just-In-Time (JIT) compiler for the Lua 5.1 language. Neovim recommends building with LuaJIT for performance reasons and exposes some LuaJIT-specific extensions (`ffi`, `bit`, profiler) when available, while maintaining compatibility with plain PUC Lua 5.1.

## Characteristics

- JIT compiler for Lua 5.1 (not Lua 5.2+ or 5.3+)
- Provides `ffi` (Foreign Function Interface) for calling C libraries directly
- Includes `bit` library for bitwise operations (always available in Neovim, with fallback for PUC Lua)
- Ships with an integrated profiler (`jit.p`)
- Significantly faster than PUC Lua for hot loops and numeric code

## Common Strategies

- Guard LuaJIT-specific code with `if jit then ... end` to maintain PUC Lua compatibility
- Use `require('jit.p').start(...)` / `.stop()` for profiling plugin performance
- Use `require('bit')` for bitwise operations (safe on both LuaJIT and PUC Lua in Neovim)
- Avoid LuaJIT-only extensions like `goto` in portable plugins

## Sources

- [Neovim Lua Reference](raw/nvim-docs/lua.txt)
