---
title: "pi-web-access"
type: entity
tags: [entity, tool, pi-extension, web-search]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: medium
---

## Overview

`pi-web-access` is a [[entities/pi|Pi]] [[concepts/pi-extension|extension]]
(github.com/nicobailon/pi-web-access) that provides web-access tools. The
`researcher` builtin agent in [[entities/pi-subagents]] relies on it: the
agent's `web_search`, `fetch_content`, and `get_search_content` tools require
`pi-web-access` to be installed.

## Characteristics

- **Install**: `pi install npm:pi-web-access`
- **Tools provided** (consumed by `researcher`): `web_search`, `fetch_content`,
  `get_search_content`.
- Optional — only needed when an agent must do web/docs research with sources.

## Common Strategies

- Install it before using the `researcher` builtin or any custom agent that
  needs to search the web or fetch external documentation, so research briefs
  can cite official docs, specs, and benchmarks.

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
