---
title: "Hermes Kanban Tenant"
type: concept
tags: [concept, ai-agent, kanban, multi-tenant, namespace, isolation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-kanban-v1-spec.pdf"]
confidence: high
---

## Definition

The Hermes Kanban Tenant is a single nullable `tenant TEXT` column on the `tasks` table that provides namespace isolation across four scoping axes—workspace, memory, board view, and audit—without introducing a new entity type or duplicating profiles. It solves the "small company serving multiple clients" use case with one schema column and a filesystem convention.

## How It Works

### Schema addition

```sql
ALTER TABLE tasks ADD COLUMN tenant TEXT; -- nullable; defaults to NULL
CREATE INDEX idx_tasks_tenant ON tasks (tenant);
```

### Four scoping axes

| Scoping axis | How tenant achieves it |
|--------------|------------------------|
| **Workspace** | Task’s `workspace_path` lives under `~/tenants/<tenant>/`. Filesystem gives data isolation for free. |
| **Memory** | Worker receives `HERMES_TENANT` env var; profiles namespace memory entries by prefix. |
| **Board view** | `hermes kanban list --tenant <tenant>` filters; per-tenant `/kanban` pinned to a thread via P7 (thread-scoped workspace). |
| **Audit** | Tenant is stamped on every `task_events` row via the task’s tenant field. One-query export of a tenant’s complete history. |

### What stays shared across tenants

- **Profile identity itself**. One `researcher` profile exists; it is invoked with different tenant contexts. Skills, model, and tool allowlist are tenant-agnostic.
- **The dispatcher**. One cron job, one board, all tenants.
- **The orchestrator**. Same orchestrator instance routes tasks for all tenants; it reads the tenant off the incoming task and propagates it to children.

### What is deliberately not in v1

- Access control per tenant. v1 assumes all tenants are owned by the same user.
- Cross-tenant task dependencies. Links cannot cross tenants in v1.
- Tenant-scoped profiles. A profile belongs to the user, not to a tenant.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `tenant` | `NULL` | Namespace string on task creation |
| `HERMES_TENANT` | inherited | Environment variable propagated to workers |
| `workspace_path` | `~/tenants/<tenant>/...` | Convention, not enforcement |

## When To Use

- One specialist fleet (researcher, writer, reviewer) that must operate in multiple business contexts without mixing data.
- Fleet farming where each "subject" (e.g., 50 social media accounts) is logically a tenant.
- Any workflow where a single user manages separate personal, business-a, and business-b contexts.

## Risks & Pitfalls

- **No access control in v1**: All tenants are visible to all profiles. A future plugin can add per-tenant credentials or approval gates.
- **Cross-tenant link prohibition**: If work genuinely spans clients, fold it into a neutral parent tenant.
- **Path traversal**: The tenant string is interpolated into filesystem paths. Sanitize tenant names to avoid `../` injection.
- **Memory namespace collisions**: If a profile ignores `HERMES_TENANT`, memory entries leak across tenants. The skill must enforce prefixing.

## Related Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-kanban-dispatcher]]
- [[concepts/hermes-profile-isolation]]
- [[concepts/hermes-persistent-memory]]

## Sources

- `docs/hermes-kanban-v1-spec.pdf` §7
