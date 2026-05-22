---
title: "Pi SDK"
type: concept
tags: [concept, pi, sdk, nodejs, typescript, embedding]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/sdk.md"]
confidence: high
---

## Definition

The Pi SDK is a programmatic Node.js/TypeScript API for embedding Pi's agent capabilities into other applications. It exposes `AgentSession`, `SessionManager`, `AuthStorage`, and `ModelRegistry` for full control over agent behavior without using the interactive TUI or RPC subprocess.

## How It Works

1. Install `@earendil-works/pi-coding-agent` via npm.
2. Create an `AuthStorage` and `ModelRegistry` to handle credentials and model metadata.
3. Call `createAgentSession({ sessionManager, authStorage, modelRegistry })` to obtain an `AgentSession`.
4. Subscribe to events (`message_update`, `tool_call`, etc.) via `session.subscribe()`.
5. Send prompts with `session.prompt()`; tool calls stream back as events.
6. The SDK supports custom `ResourceLoader` for injecting extensions, skills, themes, and prompts.

## Key Parameters

- Package: `@earendil-works/pi-coding-agent`
- Factory: `createAgentSession()`
- Core classes: `AgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, `ResourceLoader`
- Session types: `SessionManager.inMemory()`, `SessionManager.fileSystem()`

## When To Use

Use the SDK when:
- You are building a Node.js application that needs agent reasoning.
- You want a custom UI (web, desktop, mobile) driving Pi directly.
- You need automated pipelines with programmatic agent control.
- You want to test agent behavior in unit/integration tests.
- You are building custom tools that spawn sub-agents.

## Risks & Pitfalls

- The SDK shares the same session format and extension system as the CLI; security rules for extensions and skills still apply.
- In-memory sessions are lost on process exit; use `SessionManager.fileSystem()` for persistence.
- Custom `ResourceLoader` implementations must correctly resolve paths and validate resources.
- The SDK API may evolve; pin versions for production use.

## Related Concepts

- [[concepts/pi-rpc-mode]]
- [[concepts/pi-session-format]]
- [[concepts/pi-extension]]
- [[concepts/pi-provider]]

## Sources

- [Pi SDK Documentation](raw/pi-repo/packages/coding-agent/docs/sdk.md)
