---
title: "Television Watch Mode"
type: concept
tags: [concept, fuzzy-finder, monitoring, realtime]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/television-repo/docs"]
confidence: high
---

## Definition

**Watch mode** automatically reloads a channel's source command at a configurable interval, keeping the results list up to date without manual intervention.

## How It Works

Watch mode is enabled by setting a positive floating-point interval in the channel configuration or via CLI:

- Channel TOML: `[source] watch = 2.0` — reload every 2 seconds.
- CLI: `tv files --watch 5.0` — reload every 5 seconds.
- Disable: `watch = 0` (default).

When active, Television spawns the source command repeatedly on the timer and refreshes the internal entry list. The user's current selection and input are preserved across reloads where possible.

## Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `watch` | float | `0` (disabled) | Reload interval in seconds. |
| `--watch <FLOAT>` | CLI flag | inherited from channel | Override for a single session. |

## When To Use

Use watch mode for monitoring dynamic data sources: running processes (`ps aux`), Docker containers (`docker ps`), live logs, or frequently changing directories. It turns Television from a static picker into a live dashboard.

## Risks & Pitfalls

- Short intervals on expensive source commands can spike CPU usage; balance responsiveness against command cost.
- Rapid reloads may reset selection state or scroll position if the entry list changes size dramatically.
- Watch mode does not diff entries intelligently; it rebuilds the list from scratch each cycle, which may cause flicker in the UI.

## Related Concepts

- [[concepts/television-channel]]
- [[concepts/television-inline-mode]]

## Sources

- Television docs: Tips and tricks (watch mode), channel specification reference, CLI reference.
