---
title: "Obsidian"
type: entity
tags: [entity, tool, knowledge-base, markdown, notes]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/obsidian-cli.md"]
confidence: high
---

## Overview

Obsidian is a proprietary knowledge base and note-taking application centered on locally stored Markdown files. It organizes notes into vaults (folders of Markdown files), supports wikilinks, tags, YAML frontmatter properties, embedded media, and a rich plugin and theme ecosystem. The desktop application is built on Electron and available for Windows, macOS, and Linux. Since installer version 1.12.7, Obsidian ships with an official command-line interface (Obsidian CLI) for scripting and automation.

## Characteristics

- **Local-first**: All notes are plain Markdown stored on the local filesystem; there is no mandatory cloud lock-in.
- **Extensible**: Community plugins (JavaScript/TypeScript via the Obsidian API) and CSS snippets allow deep UI and behavior customization.
- **Commercial services**: Obsidian Sync provides end-to-end encrypted synchronization; Obsidian Publish generates a hosted website from selected notes; Obsidian Headless enables server-side sync without the desktop app.
- **Electron-based desktop app**: The CLI is bundled as a native binary inside the application package and communicates with the running Electron process.

## Common Strategies

- Use **Obsidian CLI** for scripting daily-note workflows, batch searches, and external integrations.
- Use the **plugin API** for deep UI extensions, custom views, and data model manipulations.
- Use **Obsidian Sync** for encrypted, cross-device vault synchronization.
- Use **CSS snippets and themes** to adapt the UI for accessibility or personal preference.

## Sources

- raw/obsidian-cli.md
