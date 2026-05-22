---
title: "Television Channel"
type: concept
tags: [concept, fuzzy-finder, configuration, terminal]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

A **channel** in Television is a declarative TOML configuration file that defines a complete search environment: what data to ingest, how to display and preview it, which keybindings to use, and what external actions can be triggered on selected entries. Channels are the primary abstraction that makes Television hackable and extensible.

## How It Works

When Television starts with a channel name (e.g., `tv files`), it loads the corresponding `.toml` file from the cable directory, executes the source command to produce entries, and renders the UI with the specified layout and keybindings. Entries are fuzzy-matched against user input in real time. Selecting an entry outputs it to stdout (or triggers a custom action).

A channel file has the following top-level sections:

- `[metadata]` — name, description, and required binaries.
- `[source]` — command(s) that produce searchable entries.
- `[preview]` — optional command to generate a preview for the selected entry.
- `[ui]` — layout, scaling, panel visibility, and border/padding settings.
- `[keybindings]` — overrides and custom mappings.
- `[actions.NAME]` — external commands that can be bound to keys.

## Key Parameters

| Field | Section | Description |
|-------|---------|-------------|
| `name` | `[metadata]` | Unique channel identifier used for invocation. |
| `command` | `[source]` | Shell command (or array of commands) producing entries. |
| `ansi` | `[source]` | Whether to parse and preserve ANSI escape codes in entries. |
| `display` | `[source]` | Template for how entries appear in the results list. |
| `output` | `[source]` | Template for the final stdout output when an entry is selected. |
| `watch` | `[source]` | Reload interval in seconds (auto-refresh). |
| `no_sort` | `[source]` | Preserve original source order, disabling match-quality sorting. |
| `frecency` | `[source]` | Enable or disable frecency-based ranking (default: `true`). |
| `command` | `[preview]` | Preview command template (supports the template syntax). |
| `shortcut` | `[keybindings]` | Global key (e.g., `f1`) to jump directly to this channel. |
| `mode` | `[actions.*]` | `fork` (return to tv) or `execute` (replace tv). |

### Source Cycling

You can specify multiple source commands as an array. Only the first runs initially; the user presses `cycle_sources` (default Ctrl+S) to rotate through them. Named variants using `{ name = "...", run = "..." }` tables display the name in the results header.

### Preview Cycling

Similarly, the `[preview]` section accepts an array of preview commands. Users cycle through them with `cycle_previews` (default Ctrl+F).

## When To Use

Use a custom channel whenever you repeatedly search the same data source and want tailored preview, keybindings, or post-selection actions. Examples: Docker containers with inspect/logs/kill actions, AWS S3 buckets, recently modified files, Git branches with checkout actions, or TLDR pages.

## Risks & Pitfalls

- The `display` template is incompatible with `ansi = true`; enabling both will cause errors.
- Action commands are shell-expanded; always quote placeholders (`'{}'`) to handle filenames with spaces or special characters.
- Requirements listed in `[metadata]` are checked at runtime, but tv only warns— it does not auto-install missing tools.
- Multiple source commands are not supported in ad-hoc (`--source-command`) mode; they only work inside a channel TOML file.

## Related Concepts

- [[concepts/television-cable]]
- [[concepts/television-template-system]]
- [[concepts/television-remote-control]]
- [[concepts/television-frecency-sorting]]
- [[concepts/television-shell-integration]]
- [[concepts/television-search-pattern]]
- [[concepts/television-watch-mode]]
- [[concepts/television-inline-mode]]

## Sources

- Television docs: Channels user guide and channel specification reference.
