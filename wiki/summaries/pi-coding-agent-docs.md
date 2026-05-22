---
title: "Pi Coding Agent Documentation"
type: summary
tags: [summary, pi, coding-agent, terminal, extensions, skills]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs"]
confidence: high
---

## Overview

Pi is a minimal terminal-based coding agent harness developed by [[entities/earendil-works]]. It is designed to stay small at the core while being extended through TypeScript [[concepts/pi-extension|extensions]], [[concepts/pi-skill|skills]], [[concepts/pi-prompt-template|prompt templates]], [[concepts/pi-theme|themes]], and [[concepts/pi-package|pi packages]]. Pi runs as an interactive TUI application inside a terminal, communicates with LLM providers via API keys or OAuth subscriptions, and persists conversation state in a tree-structured [[concepts/pi-session-format|JSONL session format]].

The architecture separates a minimal runtime from user-supplied extensions. Extensions can register custom tools the LLM calls, intercept lifecycle events, add slash commands, render custom [[concepts/pi-tui-component|TUI components]], and persist state across restarts. Skills provide on-demand specialized workflows following the [[entities/agentskills-io|Agent Skills standard]]. When conversations grow beyond the LLM context window, [[concepts/pi-compaction|compaction]] automatically summarizes older messages. For headless or programmatic use, Pi offers both a [[concepts/pi-sdk|Node.js SDK]] and a [[concepts/pi-rpc-mode|JSONL RPC mode]] over stdin/stdout.

## Key Claims

- Pi’s core is intentionally minimal; almost all behavior beyond basic chat comes from user-provided extensions, skills, and themes.
- Extensions are TypeScript modules that subscribe to lifecycle events, register custom tools, add commands, and render custom UI via a provided TUI component library.
- Skills follow the Agent Skills standard and are loaded progressively: only descriptions sit in the system prompt, full instructions load on demand via `read`.
- Sessions are stored as JSONL files with a tree structure (id/parentId), enabling in-place branching without creating new files.
- Compaction summarizes older conversation history when token use approaches the context window limit, preserving recent messages and cumulative file-operation tracking.
- Pi supports multiple LLM providers (Anthropic, OpenAI, Google, DeepSeek, Groq, Cerebras, Mistral, Azure, Cloudflare) via API keys or subscription OAuth.
- The SDK exposes `createAgentSession()` for embedding pi in Node.js applications; RPC mode exposes the same capabilities over stdin/stdout JSONL.
- Pi packages bundle extensions, skills, themes, and prompts for distribution via npm, git, or local paths.

## Source Metadata

- **Type**: Documentation source tree (Markdown)
- **Owner**: Earendil Works (https://github.com/earendil-works)
- **URL**: https://github.com/earendil-works/pi/tree/main/packages/coding-agent/docs
- **License**: Not stated in docs; project is proprietary OSS under Earendil Works
- **Ingested on**: 2026-05-21

## Relevant Concepts

- [[concepts/pi-extension]]
- [[concepts/pi-skill]]
- [[concepts/pi-theme]]
- [[concepts/pi-tui-component]]
- [[concepts/pi-compaction]]
- [[concepts/pi-session-format]]
- [[concepts/pi-provider]]
- [[concepts/pi-prompt-template]]
- [[concepts/pi-package]]
- [[concepts/pi-rpc-mode]]
- [[concepts/pi-sdk]]
- [[concepts/pi-custom-tool]]
