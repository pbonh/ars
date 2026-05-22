---
title: "Television Documentation"
type: summary
tags: [summary, fuzzy-finder, terminal, cli]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Overview

Television (`tv`) is a fast, portable, and hackable fuzzy finder for the terminal. It is written in Rust and designed to search through any kind of data in real-time. Unlike traditional fuzzy finders that are hard-coded for files or text, Television is built around a **channel** abstraction: every search context is a declarative TOML configuration that specifies a source command, an optional preview command, UI layout, keybindings, and custom actions. Users can invoke built-in channels (files, text, git-repos, env, dirs, etc.), create their own in a `cable` directory, or download community-maintained channels via `tv update-channels`.

Television can run in fullscreen mode or as an inline widget at the bottom of the terminal. It supports piping arbitrary command output into it, multi-select with Tab, custom search patterns (fuzzy, substring, prefix, suffix, exact, and negation), and a powerful template system based on the `string-pipeline` crate for formatting entries, previews, and action commands. Shell integration provides smart autocompletion (Ctrl+T) and history search (Ctrl+R) by mapping the current prompt buffer to the most appropriate channel via configurable triggers.

The documentation covers installation across many platforms (Nix, Homebrew, Scoop, WinGet, Arch, Debian, Conda, Crates.io), a quickstart guide, channel authoring tutorials, a full channel specification, CLI reference, action reference, template system deep-dive, tips and tricks, and troubleshooting.

## Key Claims

- Television is **channel-driven**: all search behavior is configurable through TOML files rather than hard-coded logic. [[concepts/television-channel]]
- Channels are stored in a **cable** directory and can be shared via a community repository. [[concepts/television-cable]]
- A built-in **remote control** (Ctrl+T) lets users switch channels without restarting the application. [[concepts/television-remote-control]]
- The **template system** uses `string-pipeline` syntax for splitting, filtering, mapping, and transforming entries dynamically. [[concepts/television-template-system]]
- Results are ranked by **frecency** (frequency + recency) by default, with per-channel toggles to disable sorting or frecency. [[concepts/television-frecency-sorting]]
- **Shell integration** provides context-aware channel selection based on the command being typed. [[concepts/television-shell-integration]]
- Search supports multiple matchers that can be combined with AND logic, including negation. [[concepts/television-search-pattern]]
- Television can run in **inline mode** for scripted or embedded use cases without taking over the terminal. [[concepts/television-inline-mode]]
- **Watch mode** automatically reloads the source command at a configurable interval. [[concepts/television-watch-mode]]

## Source Metadata

| Property | Value |
|----------|-------|
| Type | GitHub repository documentation (Markdown) |
| Owner | alexpasmantier |
| URL | https://github.com/alexpasmantier/television/tree/main/docs |
| License | MIT (repository) |
| Ingested on | 2026-05-21 |

## Relevant Concepts

- [[concepts/television-channel]]
- [[concepts/television-cable]]
- [[concepts/television-remote-control]]
- [[concepts/television-template-system]]
- [[concepts/television-frecency-sorting]]
- [[concepts/television-shell-integration]]
- [[concepts/television-search-pattern]]
- [[concepts/television-inline-mode]]
- [[concepts/television-watch-mode]]

## Relevant Entities

- [[entities/television]]
- [[entities/string-pipeline]]
- [[entities/nucleo-matcher]]
