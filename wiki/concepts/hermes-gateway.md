---
title: "Hermes Messaging Gateway"
type: concept
tags: [concept, ai-agent, gateway, messaging, platform-adapter]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Messaging Gateway is a long-running process that connects Hermes Agent to 20+ external messaging platforms through a unified architecture. It handles inbound message normalization, user authorization, slash command dispatch, session routing, outbound delivery, cron ticking, and background maintenance.

## How It Works

### Architecture

```text
Platform Adapters (Telegram, Discord, Slack, ...)
         ↓
    BaseAdapter — normalizes to MessageEvent
         ↓
  GatewayRunner._handle_message()
         ↓
    ┌─────────────┬─────────────┐
    ▼             ▼             ▼
Slash command  AIAgent    Queue/BG sessions
  dispatch    creation
         ↓
    SessionStore (SQLite)
```

### Message Flow

1. **Platform adapter** receives raw event, normalizes into `MessageEvent`.
2. **Base adapter** checks active session guard:
   - If agent is running for this session → queue message, set interrupt event.
   - If `/approve`, `/deny`, `/stop` → bypass guard (dispatched inline).
3. **GatewayRunner** receives the event:
   - Resolve session key: `agent:main:{platform}:{chat_type}:{chat_id}`.
   - Check authorization (allowlists / DM pairing).
   - Check if slash command → dispatch to handler.
   - Otherwise → create `AIAgent` instance and run conversation.
4. **Response** sent back through platform adapter.

### Authorization Layers

Evaluated in order:
1. Per-platform allow-all flag (e.g., `TELEGRAM_ALLOW_ALL_USERS`).
2. Platform allowlist (e.g., `TELEGRAM_ALLOWED_USERS`).
3. DM pairing — authenticated users pair new users via a code.
4. Global allow-all (`GATEWAY_ALLOW_ALL_USERS`).
5. Default: deny.

### Two-Level Message Guard

When an agent is actively running, incoming messages pass through:
1. **Level 1 — Base adapter**: checks `_active_sessions`, queues in `_pending_messages`, sets interrupt event.
2. **Level 2 — Gateway runner**: checks `_running_agents`, intercepts `/stop`, `/new`, `/queue`, `/status`, `/approve`, `/deny`.

Commands that must reach the runner while the agent is blocked (like `/approve`) are dispatched inline via `await self._message_handler(event)` to avoid race conditions.

### Platform Adapters

20 adapters ship in `gateway/platforms/`:

Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, DingTalk, Feishu/Lark, WeCom, Weixin, BlueBubbles (iMessage), QQ Bot, Yuanbao, Home Assistant, Webhook, API Server, Microsoft Graph (Teams/Outlook).

### Background Maintenance

The gateway runs periodic tasks alongside message handling:
- **Cron ticking** — checks job schedules and fires due jobs.
- **Session expiry** — cleans up abandoned sessions.
- **Memory flush** — proactively flushes memory before session expiry.
- **Cache refresh** — refreshes model lists and provider status.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `gateway.dispatch_interval_seconds` | Cron / kanban dispatcher tick interval (default 60) |
| Token locks | Profile-scoped locks prevent two profiles using the same bot token simultaneously |

## When To Use

- **Remote interaction**: Talk to Hermes from Telegram while it works on a cloud VM.
- **Multi-platform presence**: One agent instance serves Discord, Slack, and WhatsApp simultaneously.
- **Scheduled delivery**: Cron job outputs route through gateway to any connected platform.
- **Team access**: DM pairing lets admins onboard new users without editing config files.

## Risks & Pitfalls

- **Session key construction**: Never construct session keys manually — always use `build_session_key()` from `gateway/session.py`.
- **Config divergence**: The gateway reads `config.yaml` directly via YAML loader, not the CLI's defaults dict. Keys present in CLI defaults but absent from the user's config may behave differently between CLI and gateway.
- **Profile-scoped PID files**: `hermes gateway stop` stops only the current profile's gateway. Use `--all` to stop every gateway process.
- **Cron delivery isolation**: Cron job deliveries are NOT mirrored into gateway session history — they live in their own cron session to avoid message alternation violations.

## Related Concepts

- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-session-storage]]

## Sources

- `developer-guide/gateway-internals.md`
- `user-guide/messaging/index.md`
