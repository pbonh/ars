---
title: "Television Cable"
type: concept
tags: [concept, fuzzy-finder, configuration, extensibility]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

**Cable** is the directory where Television stores and discovers user-defined and community channel configurations. The term extends the "television" metaphor: just as a TV receives channels via a cable, Television receives its search contexts via TOML files placed in this directory.

## How It Works

On startup, Television scans the cable directory for `.toml` files. Each file is a valid channel that can be invoked by its metadata name. The default cable location is:

- **Linux / macOS**: `~/.config/television/cable/`
- **Windows**: `%LocalAppData%\television\config\cable\`
- **Custom**: override with `$TELEVISION_CONFIG/cable/` or the `--cable-dir` CLI flag.

Community-maintained channel prototypes are hosted in the main Television repository. Running `tv update-channels` downloads the latest set of prototypes into the local cable directory, making them immediately available.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| Default path | `~/.config/television/cable/` (Unix) or `%LocalAppData%\television\config\cable\` (Windows) |
| Override env | `TELEVISION_CONFIG` |
| Override CLI | `--cable-dir <PATH>` |
| File format | `.toml` |
| Update command | `tv update-channels` |

## When To Use

Create or edit cable files when you need a persistent, reusable search context that goes beyond ad-hoc `--source-command` usage. Cable channels can declare dependencies, custom keybindings, actions, and UI tweaks, making them suitable for team dotfiles or personal workflow automation.

## Risks & Pitfalls

- `tv update-channels` overwrites or adds community prototypes; keep personal channels in clearly named files to avoid accidental collisions.
- Channels are identified by the `name` field inside the TOML, not by the filename. Mismatches can cause confusion when invoking via CLI.
- There is no namespacing within cable; all channel names share a flat namespace.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-remote-control]]
- [[concepts/television-shell-integration]]

## Sources

- Television docs: Channels user guide and installation quickstart.
