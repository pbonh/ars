---
title: "Hermes Profile Isolation"
type: concept
tags: [concept, ai-agent, profile, isolation, multi-tenant]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Profile Isolation is a design principle that gives each named profile (`hermes -p <name>`) its own `HERMES_HOME`, configuration, memory, sessions, skills, and gateway PID. Multiple profiles can run concurrently on the same host without interfering.

## How It Works

### Per-Profile Resources

| Resource | Isolation |
|----------|-----------|
| `HERMES_HOME` | Separate directory per profile |
| `config.yaml` | Independent configuration |
| `MEMORY.md` / `USER.md` | Independent persistent memory |
| `state.db` | Independent session store |
| `kanban.db` | **Shared** across all profiles (the coordination surface) |
| Gateway PID | Profile-scoped PID file |
| Skills | Stored per-profile; external dirs may be shared |

### Creating and Using Profiles

```bash
hermes profile create coder --description "Code-focused profile with terminal + file tools"
hermes -p coder chat
hermes -p coder gateway start
```

### Gateway Scoping

- `hermes gateway stop` stops only the current profile's gateway.
- `hermes gateway stop --all` kills every gateway process (used during updates).
- Token locks prevent two profiles from using the same bot token simultaneously.

## Key Parameters

| Parameter | Description |
|-----------|-------------|
| `-p <name>` / `--profile <name>` | CLI flag to select profile |
| `HERMES_HOME` | Environment variable; defaults to `~/.hermes` for `default` profile |

## When To Use

- **Persona separation**: A "coder" profile with dev tools and a "writer" profile with web research tools.
- **Multi-tenant gateway**: Different Telegram bots for personal and work use.
- **Kanban specialization**: Named worker profiles (`researcher`, `writer`, `ops`) with distinct toolsets and memory.
- **Safe experimentation**: Test new configs or plugins in a throwaway profile without affecting the default.

## Risks & Pitfalls

- **Kanban shared state**: While most resources are isolated, `kanban.db` is shared. Any profile can read/write any task. This is by design (coordination primitive) but worth knowing for multi-persona setups.
- **Disk usage**: Each profile duplicates the `hermes-agent` repo, venv, and state databases. Heavy profile proliferation consumes disk.
- **Profile name drift**: The dispatcher auto-blocks tasks after 2 spawn failures. If a Kanban task references a deleted profile, it will stall until manually reassigned.

## Related Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-gateway]]
- [[concepts/hermes-persistent-memory]]

## Sources

- `user-guide/profiles.md`
- `developer-guide/architecture.md`
