---
title: "pi-mcp-adapter"
type: entity
tags: [entity, tool, pi-extension, mcp]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: medium
---

## Overview

`pi-mcp-adapter` is a [[entities/pi|Pi]] [[concepts/pi-extension|extension]]
(github.com/nicobailon/pi-mcp-adapter) that enables direct MCP (Model Context
Protocol) tools. In [[entities/pi-subagents]], an agent's `mcp:` tool entries
(e.g. `tools: mcp:chrome-devtools`) are forwarded as direct MCP selections only
when this adapter is installed.

## Characteristics

- Required for `mcp:`-prefixed tool entries in
  [[concepts/pi-agent-definition|agent definitions]] to resolve as direct MCP
  tools.
- Subagents receive direct MCP tools only when `mcp:` entries are listed in
  their frontmatter; a global `directTools: true` in `mcp.json` is not
  sufficient by itself.
- The generic `mcp` proxy tool can still be used for discovery when available.
- The adapter caches tool metadata at startup, so after connecting a new MCP
  server for the first time, Pi must be restarted before relying on direct
  tools.

## Common Strategies

- Install it, then declare specific servers in an agent's frontmatter, e.g.
  `tools: read, bash, mcp:chrome-devtools`, to give that child direct
  Chrome DevTools MCP tools alongside selected builtins.
- An `mcp:` entry named `subagent` does **not** authorize nested fanout — only
  the builtin `subagent` tool name does (see
  [[concepts/pi-subagent-recursion-guard]]).

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
