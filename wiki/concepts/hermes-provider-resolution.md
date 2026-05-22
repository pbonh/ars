---
title: "Hermes Provider Resolution"
type: concept
tags: [concept, ai-agent, llm-provider, api-routing, credentials]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Provider Resolution is the runtime subsystem that maps `(provider, model)` tuples to `(api_mode, api_key, base_url)`. It handles 18+ providers, OAuth flows, credential pools, alias resolution, and automatic fallback when the primary model fails. The resolver is shared across CLI, gateway, cron, ACP, and auxiliary LLM calls.

## How It Works

### Resolution Order

1. **Explicit `api_mode` constructor arg** (highest priority).
2. **Provider-specific detection** (e.g., `anthropic` provider → `anthropic_messages`).
3. **Base URL heuristics** (e.g., `api.anthropic.com` → `anthropic_messages`).
4. **Default**: `chat_completions`.

### Fallback Behavior

When the primary model fails:

| Error Type | Behavior |
|------------|----------|
| 429 rate limit / 5xx server error | Try each `fallback_providers` in order |
| 401/403 auth error | Attempt credential refresh before failing over |
| Success on fallback | Continue conversation with the new provider |

Fallback also covers auxiliary tasks independently — vision, compression, and web extraction each have their own fallback chain under `auxiliary.*` in config.

### Credential Pools

Multiple API keys for the same provider can be configured as a pool. On rate limit or auth error, Hermes rotates to the next credential in the pool before falling back to a different provider entirely.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `fallback_providers` | Ordered list of backup providers |
| `auxiliary.*.fallback_providers` | Per-auxiliary-task fallback chains |
| Provider alias resolution | Maps friendly names to canonical provider + model |

## When To Use

- **Resilience**: Configure `fallback_providers` so high-frequency cron jobs survive peak-hour rate limits.
- **Cost optimization**: Route cheap models (Gemini Flash) for subagents and routine tasks, keep frontier models for hard problems.
- **Multi-provider setups**: Use OpenRouter as primary with direct OpenAI/Anthropic fallbacks.

## Risks & Pitfalls

- **Base URL heuristic misclassification**: Auto-detection can guess wrong for LiteLLM proxies, Azure AI Foundry, MiniMax, or Zhipu GLM. Set `api_mode` explicitly when the heuristic fails.
- **Credential pool exhaustion**: If all keys in a pool are rate-limited, fallback to the next provider may not be the cheapest option. Monitor `auxiliary.*` fallback chains separately.
- **Mid-conversation provider switch**: The fallback system changes provider mid-conversation. While the message format converges internally, token pricing and behavior can shift unexpectedly.

## Related Concepts

- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-subagent-delegation]]

## Sources

- `developer-guide/provider-runtime.md`
- `developer-guide/adding-providers.md`
