---
title: "Television Remote Control"
type: concept
tags: [concept, fuzzy-finder, ui, navigation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

The **remote control** is Television's built-in channel picker UI. It allows users to switch between available channels on the fly without quitting and restarting the application.

## How It Works

Pressing the default keybinding (`Ctrl+T`) opens a secondary fuzzy-finder interface that lists all channels discovered in the cable directory. The list can show channel descriptions and be sorted alphabetically. Selecting a channel from the remote control immediately swaps the source, preview, and UI configuration to the new channel's settings.

Remote control behavior is configurable per channel and globally:

- `[ui.remote_control]` in `config.toml` or a channel file controls visibility, descriptions, alphabetical sorting, and whether the feature is disabled entirely.
- The `--no-remote` CLI flag disables it for a single session.

## Key Parameters

| Option | Default | Description |
|--------|---------|-------------|
| `show_channel_descriptions` | `true` | Show descriptions alongside names. |
| `sort_alphabetically` | `true` | Sort alphabetically instead of by usage. |
| `disabled` | `false` | Completely disable the remote control. |

## When To Use

Use the remote control when you start tv without specifying a channel (e.g., just `tv`) and realize you need a different context, or when you want to explore what channels are available without memorizing their CLI names.

## Risks & Pitfalls

- Disabling the remote control (`disabled = true`) removes the ability to switch channels interactively; users must rely on CLI arguments or shell integration shortcuts.
- If many channels are installed, the remote control list can become long; enabling alphabetical sort and descriptions makes navigation easier.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-cable]]
- [[concepts/television-shell-integration]]

## Sources

- Television docs: User guide (channels, keybindings, configuration reference).
