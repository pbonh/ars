---
title: "Neovim Async Job Control"
type: concept
tags: [concept, neovim, async, jobs, lua, channels]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nvim-docs/lua.txt", "raw/nvim-docs/help.txt"]
confidence: high
---

## Definition

Neovim Async Job Control is the subsystem for spawning and managing external processes, pipes, and asynchronous IO without blocking the editor UI. It is exposed primarily through `vim.system()` in Lua and complemented by lower-level `job-control` and `channel` APIs for RPC and event-driven communication.

## How It Works

1. **`vim.system()`**: The high-level Lua API for running a command. It spawns a process, returns a `vim.SystemObj`, and invokes an optional callback on completion. Call `:wait()` to block, or provide a callback for async handling.
2. **`vim.SystemObj`**: Represents a running process with methods `kill(signal)`, `wait(timeout)`, `write(data)`, and `is_closing()`.
3. **`vim.SystemCompleted`**: Result object containing `code`, `signal`, `stdout`, and `stderr`.
4. **Channels**: Nvim supports asynchronous IO channels (`job-control`, `channel`) for communicating with long-running processes over stdin/stdout/stderr or TCP/IPv4/IPv6 sockets.
5. **RPC**: The Nvim API itself is exposed over MessagePack-RPC, enabling external UIs and remote plugins to control Nvim as a server.

## Key Parameters

- `cmd`: array of command and arguments
- `text`: boolean; if true, output is returned as string instead of string[]
- `timeout`: milliseconds for `wait()`; process is SIGKILL'd (exit code 124) if timeout exceeded
- `stdin`, `stdout`, `stderr`: can be redirected to files, callbacks, or pipes
- `detach`: run process independently of Nvim
- `channel`: ID for lower-level channel/IO control

## When To Use

- Use `vim.system()` for one-shot shell commands (formatters, linters, git operations).
- Use channels/job-control for long-running language servers, REPLs, or build watchers.
- Use RPC API when building external UIs or headless automation tools.

## Risks & Pitfalls

- **Blocking**: Forgetting to use a callback and calling `wait()` in an autocommand or keymap can still block the UI if the command is slow.
- **Signal handling**: `wait()` without timeout blocks indefinitely; always set a timeout for user-facing operations.
- **Stdin management**: Writing to stdin after the process closes may error; check `is_closing()` first.
- **Callback context**: `vim.system()` callbacks run in a fast event context; use `vim.schedule()` to defer API calls that are not `api-fast`.

## Related Concepts

- [[concepts/nvim-lua-scripting]]
- [[concepts/nvim-lsp-client]]
- [[entities/neovim]]

## Sources

- [Neovim Lua Reference (vim.system)](raw/nvim-docs/lua.txt)
- [Neovim Help Index](raw/nvim-docs/help.txt)
