---
title: "Neovim Lua Scripting"
type: concept
tags: [concept, neovim, lua, scripting, configuration]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lua.txt", "raw/nvim-docs/help.txt"]
confidence: high
---

## Definition

Neovim Lua Scripting is the first-class embedded scripting model that replaces Vimscript as the preferred configuration and extension language for Neovim. It is based on Lua 5.1 (with optional LuaJIT acceleration) and exposes a comprehensive `vim.*` standard library that bridges Lua to Vimscript variables, functions, options, editor commands, and the low-level Nvim C API.

## How It Works

1. **Lua 5.1 Engine**: Neovim bundles a Lua 5.1 interpreter (ideally LuaJIT). All Lua code runs in-process and shares the editor's event loop.
2. **`vim.*` Standard Library**: Nvim provides a large Lua stdlib (`vim.api`, `vim.fn`, `vim.keymap`, `vim.opt`, `vim.iter`, `vim.fs`, etc.) that wraps editor functionality.
3. **Vimscript Bridge**: Lua can read/write Vimscript scopes (`vim.g`, `vim.b`, `vim.w`, `vim.t`, `vim.v`) and call Vim functions (`vim.fn`). Objects are copied (marshalled), not referenced.
4. **Module Loading**: Lua modules are discovered on `runtimepath` using standard Lua `require()` semantics, with `.` treated as a directory separator.
5. **API Access**: `vim.api.*` exposes the Nvim C API directly (buffers, windows, tabs, namespaces, highlights, etc.).

## Key Parameters

- Lua version: 5.1 (LuaJIT recommended for performance)
- `jit` global: indicates LuaJIT availability; `ffi` and `bit` are LuaJIT-specific
- `vim.g` / `vim.b` / `vim.w` / `vim.t` / `vim.v`: scope bridges to Vimscript dictionaries
- `vim.o` / `vim.bo` / `vim.wo` / `vim.go` / `vim.opt`: option bridges
- `vim.api`: direct C API; note `api-fast` restriction in some callbacks
- `vim.fn`: direct Vimscript function calls with automatic type conversion

## When To Use

- Use Lua for all new Neovim configuration (`init.lua` instead of `init.vim`).
- Use Lua for plugin development to leverage coroutines, closures, and tables.
- Use `vim.system()` for async shell integration.
- Use `vim.iter()` for list/dict processing in a functional style.

## Risks & Pitfalls

- **LuaJIT vs PUC Lua**: LuaJIT extensions (`goto`, `ffi`) are not guaranteed on all platforms; guard with `if jit then ... end`.
- **Copy semantics**: Objects passed through `vim.fn` or scope bridges are copied, not shared. Modifying a Lua table returned from `vim.fn` does not affect Vimscript state.
- **Dictionary field mutation**: Setting `vim.g.my_dict.field = 'x'` does not write back; you must reassign the whole dictionary.
- **API restrictions**: `vim.api` functions (except `api-fast`) cannot be called in certain callbacks (e.g., `vim.api.nvim_create_autocmd` callbacks may need `vim.schedule()`).
- **Error handling**: Lua throws errors; use `pcall()` for exceptional failures and the `result-or-message` pattern (`nil, err`) for expected failures.

## Related Concepts

- [[concepts/nvim-async-jobs]]
- [[concepts/nvim-lsp-client]]
- [[entities/luajit]]

## Sources

- [Neovim Lua Reference](raw/nvim-docs/lua.txt)
- [Neovim Help Index](raw/nvim-docs/help.txt)
