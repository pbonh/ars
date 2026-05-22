---
title: "Obsidian CLI TUI"
type: concept
tags: [concept, obsidian, cli, tui, interactive]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/obsidian-cli.md"]
confidence: high
---

## Definition

The Obsidian CLI Terminal User Interface (TUI) is an interactive shell mode entered by running `obsidian` without arguments. It provides contextual autocomplete, command history, reverse search, and readline-style keyboard shortcuts so that users can explore and execute Obsidian commands without repeatedly typing the `obsidian` prefix.

## How It Works

- Launch the TUI by running `obsidian` in the terminal.
- Once inside, subsequent commands are entered directly without the `obsidian` prefix (e.g., `help`, `daily`, `search query="meeting"`).
- **Autocomplete**: Press `Tab` to enter suggestion mode and accept the selected suggestion. Press `Shift+Tab` to exit suggestion mode. The `Down` arrow from fresh input also enters suggestion mode.
- **History navigation**: `Up` / `Ctrl+P` moves to previous entries; `Down` / `Ctrl+N` moves to next entries.
- **Reverse search**: `Ctrl+R` initiates a filtered reverse history search; press `Ctrl+R` again to cycle matches.
- **Editing**: `Ctrl+U` deletes to the start of the line; `Ctrl+K` deletes to the end; `Ctrl+W` / `Alt+Backspace` deletes the previous word.
- **Vault switching** (TUI only): Use `vault:open <name>` or `vault:open <id>` to change the active vault mid-session.
- Exit the TUI with `Ctrl+C` or `Ctrl+D`.

## Key Parameters

The TUI itself accepts no parameters, but it supports vault switching via the internal command `vault:open <name>`.

## When To Use

- Exploring available commands interactively when you do not know the exact syntax.
- Running a sequence of related commands against the same vault (e.g., `search`, `read`, `append`).
- When you want persistent command history and autocomplete for Obsidian operations within a single terminal session.

## Risks & Pitfalls

- **State coupling**: The TUI assumes the targeted Obsidian vault remains stable. If the vault is switched or closed in the GUI, the TUI may issue commands against a stale or unexpected context.
- **No persistent session**: History and state are not preserved across separate TUI invocations.
- **Accidental execution**: Autocomplete at the end of a line can be accepted by the `Right` arrow or `Enter`, which may inadvertently run a command if the user intended only to edit.

## Related Concepts

- [[concepts/obsidian-cli]] — the overall command-line interface.

## Sources

- raw/obsidian-cli.md
