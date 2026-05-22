---
title: "Nushell Plugin System"
type: concept
tags: [concept, shell, extensibility, plugin]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/nushell-book/book"]
confidence: high
---

## Definition

Nushell plugins are external binaries that extend the shell with new commands. They communicate with Nushell via the versioned `nu-plugin` protocol, behaving much like built-in commands once registered. Plugins allow developers to add functionality in any language without modifying the Nushell core.

## How It Works

To use a plugin, it must be:

1. **Installed** — the plugin binary (named `nu_plugin_<name>`) must be on the system.
2. **Added** — registered with `plugin add <path_or_name>`, which records it in the plugin registry file.
3. **Imported** — made available in the current session with `plugin use <name>`, or automatically on restart.

Core plugins maintained by the Nushell project include:

- **polars** — fast columnar DataFrames.
- **formats** — additional file formats (EML, ICS, INI, plist, VCF).
- **gstat** — Git repository status as structured data.
- **query** — SQL, XML, JSON, HTML querying.
- **inc** — version/semver incrementing.

The plugin protocol is versioned; plugins must match the `nu-plugin` version of the host Nushell installation. Updating Nushell without updating plugins can cause protocol mismatches.

## Key Parameters

- `plugin add` — registers a plugin binary.
- `plugin use` — imports a registered plugin into the current session.
- `plugin list` — shows registered plugins.
- `$NU_PLUGIN_DIRS` / `$env.NU_PLUGIN_DIRS` — search paths for plugin binaries.

## When To Use

- Use official plugins when you need DataFrame analytics, extra formats, or SQL querying.
- Write a custom plugin when you need to integrate a domain-specific tool or library that has no Nushell equivalent.

## Risks & Pitfalls

- Protocol version mismatches between Nushell and plugins cause communication failures. Always update plugins when upgrading Nushell.
- Plugin binaries must be named `nu_plugin_<name>`; the `plugin add` command uses this convention.
- Plugin installation paths vary by package manager; Cargo installs do not automatically include plugins.

## Related Concepts

- [[concepts/nushell-dataframe]] — the Polars plugin provides DataFrame support
- [[concepts/nushell-custom-command]] — plugins expose commands with signatures similar to custom commands

## Sources

- Nushell Book: [Plugins](raw/nushell-book/book/plugins.md)
