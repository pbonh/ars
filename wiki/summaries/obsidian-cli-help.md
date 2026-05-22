---
title: "Obsidian CLI - Obsidian Help"
type: summary
tags: [summary, obsidian, cli, productivity]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/obsidian-cli.md"]
confidence: high
---

## Overview

Obsidian CLI is the official command-line interface bundled with Obsidian desktop 1.12.7 and later. It exposes nearly every Obsidian capability—notes, search, plugins, themes, sync, workspaces, and even developer tools—as terminal commands suitable for scripting, automation, and integration with external tools.

The CLI operates in two modes: single-shot commands (`obsidian <cmd>`) and an interactive Terminal User Interface (TUI) launched by running `obsidian` without arguments. The TUI provides autocomplete, command history, reverse search, and contextual help. In both modes, the CLI communicates with a running Obsidian instance; if the app is not running, the first command launches it automatically.

Vault targeting defaults to the current working directory when inside a vault folder, falling back to the active Obsidian window’s vault. File targeting supports both wikilink-style resolution (`file=<name>`) and exact vault-root paths (`path=<path>`). A special `--copy` flag on any command copies output to the system clipboard.

## Key Claims

- Obsidian CLI requires Obsidian installer version 1.12.7 or newer.
- The CLI requires the Obsidian desktop app to be running.
- Single commands use the pattern `obsidian <command> [parameters] [flags]`.
- The TUI drops the `obsidian` prefix after the initial launch.
- Parameters take values (`name=value`); flags are boolean switches without values.
- Developer commands expose Electron devtools, CDP, DOM/CSS inspection, screenshots, and in-app JS evaluation for plugin and theme development.
- Windows uses a terminal redirector (`Obsidian.com`) to bridge GUI-app stdout/stdin limitations.

## Source Metadata

| Field | Value |
|-------|-------|
| Type | Documentation (Obsidian Help, published via Obsidian Publish) |
| Owner | Obsidian |
| URL | https://obsidian.md/help/cli |
| License | Not specified (proprietary documentation) |
| Ingested on | 2026-05-21 |

## Relevant Concepts

- [[concepts/obsidian-cli]] — the command-line interface architecture and core commands.
- [[concepts/obsidian-cli-tui]] — the interactive terminal user interface.
- [[concepts/obsidian-cli-developer-commands]] — debugging and automation commands for developers.
