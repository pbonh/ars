---
title: "Television Shell Integration"
type: concept
tags: [concept, fuzzy-finder, shell, autocomplete]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

**Shell integration** is Television's mechanism for embedding itself into interactive shells (Zsh, Bash, Fish, Nushell, PowerShell) to provide smart autocompletion and command-history search. It maps the current command-line buffer to the most appropriate channel via configurable triggers.

## How It Works

After running `tv init <shell>` and restarting the shell, two keybindings become available:

- **Ctrl+T** — smart autocomplete: Television reads the current prompt buffer, attempts to guess the best channel, and opens with the buffer as pre-filled input.
- **Ctrl+R** — command history: opens a dedicated shell-history channel to search through previously run commands.

The mapping from command to channel is controlled by `[shell_integration.channel_triggers]` in `config.toml`. Each key is a channel name and each value is a list of command prefixes that should trigger that channel. For example:

```toml
[shell_integration.channel_triggers]
"git-branches" = ["git checkout", "git branch"]
"files" = ["cat", "less", "vim"]
"dirs" = ["cd", "ls", "rmdir"]
```

If no trigger matches, a fallback channel (default `files`) is used.

Users can also dump the generated integration script to a file, customize it (e.g., to auto-execute selections), and source it manually.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fallback_channel` | `"files"` | Channel used when no trigger matches. |
| `smart_autocomplete` | `"ctrl-t"` | Keybinding for smart autocomplete. |
| `command_history` | `"ctrl-r"` | Keybinding for history search. |

## When To Use

Enable shell integration when you want Television to act as a universal completion engine that adapts to the command you are typing, rather than manually invoking `tv <channel>` each time.

## Risks & Pitfalls

- Trigger lists must be maintained manually; there is no automatic inference from channel metadata.
- The generated scripts append to shell profiles by default; users should remove duplicate source lines if they switch to customized local copies.
- Customizing the integration script (e.g., auto-executing on selection) can have unintended side effects, such as running sensitive commands immediately.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-channel]]
- [[concepts/television-remote-control]]

## Sources

- Television docs: Shell integration guide and configuration reference.
