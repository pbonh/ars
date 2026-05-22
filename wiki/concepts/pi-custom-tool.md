---
title: "Pi Custom Tool"
type: concept
tags: [concept, pi, tool, llm, extension]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/extensions.md"]
confidence: high
---

## Definition

A Pi custom tool is a function registered by an extension that the LLM can invoke during a conversation. Tools are defined with a JSON Schema parameter specification and an async execution handler.

## How It Works

1. An extension calls `pi.registerTool({ name, description, parameters, execute })`.
2. The `parameters` field uses JSON Schema (via TypeBox) to declare expected arguments.
3. When the LLM decides to use the tool, Pi calls `execute(toolCallId, params, signal, onUpdate, ctx)`.
4. The handler returns a structured result with content blocks (text, images, etc.).
5. Extensions can intercept tool calls via the `tool_call` event to block or modify them.

## Key Parameters

- Registration API: `pi.registerTool()`
- Schema library: `@sinclair/typebox` (via `Type`)
- Execution signature: `async execute(toolCallId, params, signal, onUpdate, ctx)`
- Interception event: `tool_call`

## When To Use

Register a custom tool when:
- You want the LLM to interact with an external API or database.
- You need the agent to perform calculations, file conversions, or data processing.
- You want to gate or audit specific tool invocations (e.g., require confirmation).
- You are building an integration that goes beyond what built-in `bash`/`read`/`edit` provide.

## Risks & Pitfalls

- The LLM may hallucinate parameter values; always validate in the execute handler.
- Long-running tools should respect the `signal` (AbortSignal) for cancellation.
- `onUpdate` can stream partial results, but not all clients handle streaming tool results.
- Blocking tool calls in interceptors can confuse the LLM if no replacement result is provided.

## Related Concepts

- [[concepts/pi-extension]]
- [[concepts/pi-tui-component]]
- [[concepts/pi-rpc-mode]]

## Sources

- [Pi Extensions Documentation](raw/pi-repo/packages/coding-agent/docs/extensions.md)
