---
title: "Hermes Plugin System"
type: concept
tags: [concept, ai-agent, plugin, extensibility, python]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Plugin System is an extensibility framework that allows third-party and user-authored code to register tools, hooks, and CLI commands. Plugins are discovered from three sources: `~/.hermes/plugins/` (user), `.hermes/plugins/` (project-local), and pip entry points. Two specialized plugin types exist: memory providers and context engines.

## How It Works

### Discovery Sources

1. `~/.hermes/plugins/` — user-installed plugins.
2. `.hermes/plugins/` — project-local plugins (checked into repos).
3. **pip entry points** — plugins installed as Python packages.

### Plugin API

Plugins register capabilities through a context API:
- **Tools**: Add new agent-callable tools to the registry.
- **Hooks**: Respond to gateway lifecycle events (`gateway:startup`, `session:start`, `agent:end`, etc.).
- **CLI commands**: Add new `hermes` subcommands.

### Specialized Plugin Types

| Type | Location | Behavior |
|------|----------|----------|
| **Memory providers** | `plugins/memory/` | Single-select — only one active at a time. Adds deep memory (knowledge graphs, semantic search, cross-session modeling). |
| **Context engines** | `plugins/context_engine/` | Single-select — only one active at a time. Replaces the default context compression/summarization strategy. |

Both are configured via `hermes plugins` or `config.yaml`.

### Plugin Loading

The `PluginManager` (`hermes_cli/plugins.py`) handles discovery, loading, and hook dispatch. Plugins are loaded at startup; tools register at import time through `registry.register()` calls.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `plugins.enabled` | List of enabled plugin names |
| Memory provider config | `memory.provider` key selects active memory plugin |
| Context engine config | `context_engine.provider` key selects active context engine |

## When To Use

- **Custom tools**: Add organization-specific APIs or internal services as first-class agent tools.
- **Deep memory**: Replace MEMORY.md/USER.md with a knowledge graph (Honcho, Mem0, etc.).
- **Custom compression**: Implement a domain-specific context management strategy (e.g., code-aware compression that preserves function signatures).
- **Gateway hooks**: Add observability, metrics, or custom authorization logic.

## Risks & Pitfalls

- **Single-select contention**: Only one memory provider and one context engine can be active. Loading a second silently replaces the first.
- **Import-time side effects**: Plugins that register tools at import time can fail startup if dependencies are missing. Graceful degradation depends on the plugin author.
- **Hook ordering**: No explicit ordering guarantee for hooks responding to the same event. Hooks should be idempotent.
- **Security**: Project-local plugins (`.hermes/plugins/`) are loaded automatically. Malicious plugins checked into a cloned repo could run with the user's permissions.

## Related Concepts

- [[concepts/hermes-mcp-integration]]
- [[concepts/hermes-skills-system]]
- [[concepts/hermes-persistent-memory]]
- [[concepts/hermes-context-compression]]

## Sources

- `developer-guide/architecture.md`
- `user-guide/features/plugins.md`
