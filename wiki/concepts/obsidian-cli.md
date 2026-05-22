---
title: "Obsidian CLI"
type: concept
tags: [concept, obsidian, cli, productivity, automation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/obsidian-cli.md"]
confidence: high
---

## Definition

Obsidian CLI is the official command-line interface bundled with the Obsidian desktop application starting with installer version 1.12.7. It allows users and external tools to control Obsidian—creating and reading notes, managing plugins and themes, searching vaults, inspecting file metadata, and invoking developer tools—entirely from the terminal.

## How It Works

- **Connection model**: The CLI communicates with a running Obsidian instance. If Obsidian is not running, the first command launches the app automatically.
- **Command syntax**: Commands follow `obsidian <command> [parameters] [flags]`. Parameters are key-value pairs written as `name=value`. Flags are boolean switches with no value (e.g., `open`, `overwrite`).
- **Vault targeting**: If the terminal’s current working directory is inside a vault folder, that vault is used by default. Otherwise, the currently active Obsidian vault is targeted. Override with `vault=<name>` or `vault=<id>` as the first parameter.
- **File targeting**: `file=<name>` resolves using wikilink-style matching by filename (no path or extension required). `path=<path>` requires the exact path from the vault root.
- **Output capture**: The `--copy` flag can be appended to any command to copy its output to the system clipboard.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `vault=<name\|id>` | Target vault; must appear before the command. |
| `file=<name>` | Wikilink-style file resolution. |
| `path=<path>` | Exact vault-root path. |
| `--copy` | Copy command output to clipboard. |

## When To Use

- Scripting daily-note workflows, templated note creation, or batch property updates.
- Integrating Obsidian into external toolchains (Alfred, Raycast, CI pipelines).
- Quickly searching or reading vault content without leaving the terminal.
- Automating plugin and theme reload cycles during development.

## Risks & Pitfalls

- **Installer version requirement**: The CLI binary is only present in Obsidian 1.12.7+ installers; earlier versions cannot register the CLI.
- **PATH issues**: On macOS, registration creates a symlink at `/usr/local/bin/obsidian` requiring admin privileges. On Linux, it copies to `~/.local/bin/obsidian`. A terminal restart is usually required for PATH changes to take effect.
- **Windows stdout quirks**: Because Obsidian is a GUI application, Windows routes CLI I/O through a `Obsidian.com` terminal redirector installed alongside `Obsidian.exe`.
- **Data mutation**: Commands like `create`, `append`, `move`, `rename`, and `delete` can overwrite or lose data if flags like `overwrite` or `permanent` are used carelessly.

## Related Concepts

- [[concepts/obsidian-cli-tui]] — the interactive terminal mode.
- [[concepts/obsidian-cli-developer-commands]] — developer and debugging commands.
- [[entities/obsidian]] — the Obsidian application.

## Sources

- raw/obsidian-cli.md
