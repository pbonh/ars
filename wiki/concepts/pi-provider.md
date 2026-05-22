---
title: "Pi Provider"
type: concept
tags: [concept, pi, llm, api, authentication]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/providers.md", "raw/pi-repo/packages/coding-agent/docs/custom-provider.md", "raw/pi-repo/packages/coding-agent/docs/models.md"]
confidence: high
---

## Definition

A Pi provider is an LLM backend integration that supplies models and handles authentication. Pi supports both subscription-based providers (OAuth) and API-key providers, as well as fully custom provider implementations.

## How It Works

1. Built-in providers ship with model definitions updated per release.
2. API keys are resolved in order: environment variable → `auth.json` → auth file.
3. Subscriptions (ChatGPT Plus/Pro, Claude Pro/Max, GitHub Copilot) use OAuth via `/login`; tokens are stored in `~/.pi/agent/auth.json` and auto-refresh.
4. Custom providers can be added by implementing a provider class with model listing, completion, and streaming methods.
5. Model entries can be customized or added via `settings.json` under `models`.

## Key Parameters

- Built-in providers: Anthropic, OpenAI, Google Gemini, DeepSeek, Groq, Cerebras, Mistral, Azure OpenAI, Cloudflare
- Auth storage: `~/.pi/agent/auth.json`
- API key env vars: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.
- Custom provider path: `~/.pi/agent/providers/` or `.pi/providers/`

## When To Use

Configure or create a provider when:
- You need to switch between LLM backends for cost, latency, or capability reasons.
- You want to add a new model not yet in the built-in registry.
- You are integrating an internal or private LLM API.
- You need to route traffic through a gateway or proxy.

## Risks & Pitfalls

- OAuth tokens are stored locally; protect `auth.json` from unauthorized access.
- Claude Pro/Max third-party usage draws from "extra usage" and is billed per token.
- Custom providers must handle streaming, error responses, and token counting correctly.
- Model definitions must include token limits; missing limits may cause compaction or truncation issues.

## Related Concepts

- [[concepts/pi-custom-tool]]
- [[concepts/pi-extension]]
- [[concepts/pi-rpc-mode]]

## Sources

- [Pi Providers Documentation](raw/pi-repo/packages/coding-agent/docs/providers.md)
- [Pi Custom Provider Documentation](raw/pi-repo/packages/coding-agent/docs/custom-provider.md)
- [Pi Custom Models Documentation](raw/pi-repo/packages/coding-agent/docs/models.md)
