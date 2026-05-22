---
title: "Hermes Tool Registry"
type: concept
tags: [concept, ai-agent, tools, registry, dispatch]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Tool Registry is a central registry (`tools/registry.py`) that manages 70+ built-in tools across ~28 toolsets. Each tool file self-registers at import time via `registry.register()`. The registry handles schema collection, dispatch, availability checking (`check_fn` gating), and error wrapping.

## How It Works

### Self-Registration Pattern

```text
tools/registry.py  (no deps — imported by all tool files)
       ↑
tools/*.py  (each calls registry.register() at import time)
       ↑
model_tools.py  (imports tools/registry + triggers tool discovery)
       ↑
run_agent.py, cli.py, batch_runner.py, environments/
```

Any `tools/*.py` file with a top-level `registry.register()` call is auto-discovered — no manual import list needed.

### Toolsets

Tools are grouped into named toolsets for progressive enablement:

| Toolset | Example Tools |
|---------|---------------|
| `terminal` | `terminal`, `process` |
| `file` | `read_file`, `write_file`, `patch`, `search_files` |
| `web` | `web_search`, `web_extract` |
| `browser` | `browser_navigate`, `browser_click`, `browser_snapshot`, ... |
| `code_execution` | `execute_code` |
| `delegation` | `delegate_task` |
| `skills` | `skills_list`, `skill_view`, `skill_manage` |
| `memory` | `memory` |
| `cronjob` | `cronjob` |
| `mcp-*` | Dynamically created per MCP server |

Platform-specific toolsets (e.g., `discord`, `spotify`, `feishu_doc`) register only when their platform credentials are configured.

### Gating with check_fn

Optional subsystems use `check_fn` functions to determine tool availability at runtime. For example, `x_search` only registers when `XAI_API_KEY` or xAI OAuth is present. MCP tools register dynamically after server connection.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| Tool schema | Auto-collected from registered tool docstrings / function signatures |
| `toolsets:` in config | Per-platform enablement list |

## When To Use

- **Cost control**: Disable expensive toolsets (`browser`, `image_gen`, `video_gen`) for simple chat sessions.
- **Platform restriction**: Gateway platforms can have different toolsets than CLI — e.g., no `terminal` on Telegram for safety.
- **Custom tools**: Register new tools via the plugin system; they integrate automatically.

## Risks & Pitfalls

- **Schema bloat**: Every enabled tool adds tokens to the system prompt. Enabling all 70+ tools on every call is expensive.
- **Import-order dependency**: Because registration happens at import time, circular imports in `tools/*.py` can break discovery.
- `tools/registry.py` must have zero dependencies — it is imported by all tool files.
- **MCP tool name collisions**: Prefixed with `mcp_<server>_` to avoid collisions, but long server/tool names can produce unwieldy tool names.

## Related Concepts

- [[concepts/hermes-mcp-integration]]
- [[concepts/hermes-plugin-system]]
- [[concepts/hermes-agent-loop]]

## Sources

- `reference/tools-reference.md`
- `developer-guide/tools-runtime.md`
- `developer-guide/architecture.md`
