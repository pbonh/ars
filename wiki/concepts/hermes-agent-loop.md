---
title: "Hermes Agent Loop"
type: concept
tags: [concept, ai-agent, orchestration, llm]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Agent Loop is the synchronous orchestration engine at the core of Hermes Agent. Implemented as the `AIAgent` class in `run_agent.py`, it handles the complete conversation lifecycle: prompt assembly, provider selection, API calling, tool dispatch, retries, fallback switching, compression, and persistence.

## How It Works

The loop follows a strict turn lifecycle:

1. **Generate task_id** if not provided.
2. **Append user message** to conversation history.
3. **Build or reuse cached system prompt** via `prompt_builder.py`.
4. **Preflight compression check** — if conversation exceeds 50% of model context window.
5. **Build API messages** in the correct wire format:
   - `chat_completions`: OpenAI format as-is
   - `codex_responses`: converted to Responses API input items
   - `anthropic_messages`: converted via `anthropic_adapter.py`
6. **Inject ephemeral layers** (budget warnings, context pressure).
7. **Apply prompt caching markers** if on Anthropic.
8. **Make interruptible API call** — runs HTTP in a background thread while monitoring an interrupt event.
9. **Parse response**:
   - If `tool_calls`: execute them, append results, loop back to step 5.
   - If text response: persist session, flush memory, return.

### API Modes

| Mode | Used For | Client |
|------|----------|--------|
| `chat_completions` | OpenAI-compatible endpoints (OpenRouter, custom, most providers) | `openai.OpenAI` |
| `codex_responses` | OpenAI Codex / Responses API | `openai.OpenAI` with Responses format |
| `anthropic_messages` | Native Anthropic Messages API | `anthropic.Anthropic` via adapter |

Mode resolution order: explicit `api_mode` arg → provider-specific detection → base URL heuristics → default `chat_completions`.

### Message Format

All messages use OpenAI-compatible format internally:
```python
{"role": "system", "content": "..."}
{"role": "user", "content": "..."}
{"role": "assistant", "content": "...", "tool_calls": [...]}
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

Strict alternation rules: never two assistant messages in a row, never two user messages in a row. Only `tool` role can have consecutive entries (parallel tool results).

### Tool Execution

- **Single tool call** → executed directly in main thread.
- **Multiple tool calls** → executed concurrently via `ThreadPoolExecutor`, except interactive tools (e.g., `clarify`) which force sequential execution. Results are reinserted in original tool call order regardless of completion order.

### Interruptible API Calls

API requests run in a background thread while the main thread monitors:
- response ready event
- interrupt event (user sends new message, `/stop`, signal)
- timeout

When interrupted, the API thread is abandoned (response discarded) and the agent processes new input or shuts down cleanly. No partial response is injected into conversation history.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `agent.max_turns` | 90 | Iteration budget per agent |
| `delegation.max_iterations` | 50 | Iteration budget per subagent |
| `compression.protect_last_n` | 20 | Messages preserved intact during compression |

## When To Use

The agent loop is the runtime engine — users do not invoke it directly. Understanding it matters when:
- Debugging why a conversation stopped mid-task (iteration budget exceeded).
- Configuring fallback providers for resilience.
- Tuning compression thresholds for long-context models.
- Writing custom tools or plugins that interact with the loop.

## Risks & Pitfalls

- **Iteration budget exhaustion**: Default 90 turns can be exceeded on complex multi-file refactoring. The agent stops and returns a summary of work done.
- **Context compression data loss**: Middle conversation turns are summarized; critical details may be lost if not in the protected last N messages.
- **Interrupt abandonment**: Interrupted API calls discard in-flight responses. For expensive reasoning models, this wastes tokens.
- **Message alternation violations**: malformed histories are rejected by providers. Custom tools must not produce consecutive assistant or user messages.

## Related Concepts

- [[concepts/hermes-context-compression]]
- [[concepts/hermes-provider-resolution]]
- [[concepts/hermes-session-storage]]
- [[concepts/hermes-subagent-delegation]]
- [[concepts/hermes-persistent-memory]]

## Sources

- `developer-guide/agent-loop.md`
- `developer-guide/architecture.md`
