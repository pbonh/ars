---
title: "Hermes MCP Integration"
type: concept
tags: [concept, ai-agent, mcp, tools, extensibility]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes MCP Integration connects Hermes Agent to external tool servers via the Model Context Protocol (MCP). This allows the agent to use tools that live outside Hermes itself — GitHub, databases, file systems, browser stacks, internal APIs — without requiring a native Hermes tool implementation first.

## How It Works

### Two Server Types

**Stdio servers** run as local subprocesses and communicate over stdin/stdout:

```yaml
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
```

**HTTP servers** are remote endpoints Hermes connects to directly:

```yaml
mcp_servers:
  remote_api:
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ***"
```

### Tool Registration

Hermes prefixes MCP tools to avoid collisions with built-in names:

```
mcp_<server_name>_<tool_name>
```

Examples: `mcp_filesystem_read_file`, `mcp_github_create_issue`.

### Dynamic Tool Discovery

MCP servers can notify Hermes when their available tools change at runtime via `notifications/tools/list_changed`. Hermes automatically re-fetches the tool list and updates the registry — no manual `/reload-mcp` required.

### Per-Server Filtering

Control exactly which tools each server contributes:

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    tools:
      include: [create_issue, list_issues]
      exclude: [delete_issue]
      prompts: false
      resources: false
```

If both `include` and `exclude` are present, `include` wins.

### MCP Sampling

MCP servers can request LLM inference from Hermes via `sampling/createMessage`. Configurable per-server with rate limits, timeouts, and tool-loop depth caps to prevent runaway usage.

### Running Hermes as an MCP Server

Hermes can also **be** an MCP server, exposing messaging capabilities to other MCP clients (Claude Code, Cursor, Codex):

```bash
hermes mcp serve
```

Exposes 10 tools including `conversations_list`, `messages_read`, `messages_send`, and `events_poll` / `events_wait` for near-real-time event bridging.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `timeout` | — | Tool call timeout |
| `connect_timeout` | — | Initial connection timeout |
| `supports_parallel_tool_calls` | `false` | Enable concurrent tool execution from this server |
| `sampling.enabled` | `true` | Allow server to request LLM inference |
| `sampling.max_tokens_cap` | 4096 | Max tokens per sampling response |
| `sampling.max_rpm` | 10 | Rate limit: max requests per minute |

## When To Use

- **Existing tool ecosystems**: Connect to GitHub, Stripe, or internal APIs that already have MCP servers.
- **Safe extension**: Filter out dangerous tools (`delete_customer`) while keeping useful ones.
- **Cross-agent messaging**: Use `hermes mcp serve` to let Claude Code or Cursor send Telegram/Discord messages through Hermes.

## Risks & Pitfalls

- **Parallel call safety**: Only enable `supports_parallel_tool_calls` for servers whose tools are safe to run concurrently. Read/write shared state can race.
- **Environment leakage**: For stdio servers, Hermes does not pass the full shell environment — only explicitly configured `env` plus a safe baseline.
- **Sampling abuse**: The sampling handler has rate limits and loop caps, but a compromised MCP server could still burn tokens. Disable sampling for untrusted servers.
- **Network exposure**: `hermes mcp serve` is stdio-only today. HTTP server mode is client-side only (connecting out to remote MCP servers).

## Related Concepts

- [[concepts/hermes-plugin-system]]
- [[concepts/hermes-tool-registry]]
- [[concepts/hermes-agent-loop]]

## Sources

- `user-guide/features/mcp.md`
