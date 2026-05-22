---
title: "Television"
type: entity
tags: [entity, tool, fuzzy-finder, rust, terminal]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Overview

Television (`tv`) is a fast, portable, and hackable fuzzy finder for the terminal, written in Rust by Alexandre Pasmantier. It is distributed under the MIT license and available for Linux, macOS, Windows, NetBSD, and Chimera Linux via multiple package managers (Nix, Homebrew, Scoop, WinGet, Arch, Debian, Conda, pkgsrc) as well as via `cargo install` and precompiled binaries.

## Characteristics

- **Channel-driven architecture**: every search context is a TOML configuration rather than hard-coded behavior.
- **Real-time fuzzy matching**: powered by the `nucleo-matcher` Rust crate.
- **Template system**: dynamic formatting via the `string-pipeline` crate.
- **Multi-platform shell integration**: supports Zsh, Bash, Fish, Nushell, and PowerShell.
- **Extensible UI**: customizable themes, layouts (landscape/portrait), panel visibility, borders, and padding.
- **Community channels**: downloadable channel prototypes via `tv update-channels`.

## Common Strategies

- Use `tv` with built-in channels (`files`, `text`, `git-repos`, `env`, `dirs`) for everyday terminal navigation.
- Pipe command output into `tv` for interactive filtering: `git log --oneline | tv`.
- Create custom cable channels for team-specific workflows (e.g., Kubernetes pods, AWS resources, Jira tickets).
- Embed `tv --inline` in scripts or tmux panes where fullscreen takeover is undesirable.
- Enable shell integration to turn Television into a context-aware autocomplete engine.

## Sources

- GitHub repository: https://github.com/alexpasmantier/television
- Documentation: https://github.com/alexpasmantier/television/tree/main/docs
