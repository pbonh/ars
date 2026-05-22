---
title: "Hermes Kanban Board"
type: concept
tags: [concept, ai-agent, kanban, multi-agent, coordination, sqlite]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs", "raw/hermes-kanban-v1-spec.pdf"]
confidence: high
---

## Definition

The Hermes Kanban Board is a durable SQLite-backed task board shared across all Hermes profiles. It enables multiple named agents to collaborate on work without fragile in-process subagent swarms. Every task is a row in `~/.hermes/kanban.db`; every handoff is a row anyone can read and write; every worker is a full OS process with its own identity and persistent memory.

## How It Works

### Core Primitives

| Primitive | Description |
|-----------|-------------|
| **Board** | A standalone queue with its own SQLite DB, workspaces directory, and dispatcher loop. Fresh installs have one `default` board; users can create more. |
| **Task** | A row with title, body, assignee (profile name), status (`triage | todo | ready | running | blocked | done | archived`), optional tenant namespace, optional idempotency key. |
| **Link** | `task_links` row recording a parent → child dependency. The dispatcher promotes `todo → ready` when all parents are `done`. |
| **Comment** | The inter-agent protocol. Agents and humans append comments; workers read the full thread as context. |
| **Workspace** | Directory a worker operates in: `scratch` (fresh tmp), `dir:<path>` (shared existing directory), or `worktree` (git worktree). |
| **Dispatcher** | Long-lived loop inside the gateway that reclaims stale claims, promotes ready tasks, and spawns assigned profiles every 60 seconds. |

### Worker Interaction

Workers do not shell out to `hermes kanban`. The dispatcher sets `HERMES_KANBAN_TASK=<id>` in the child's environment, which activates a dedicated `kanban_*` toolset:

| Tool | Purpose |
|------|---------|
| `kanban_show` | Read current task + comments + prior handoffs |
| `kanban_complete` | Finish with structured handoff (`summary` + `metadata`) |
| `kanban_block` | Escalate for human input with a `reason` |
| `kanban_heartbeat` | Signal liveness during long operations |
| `kanban_comment` | Append a durable note |
| `kanban_create` | Fan out child tasks (orchestrators) |
| `kanban_link` | Add parent → child dependency |
| `kanban_unblock` | Move blocked task back to `ready` (orchestrators) |

### Collaboration Patterns

The board supports 8 canonical patterns:

| Pattern | Shape | Example |
|---------|-------|---------|
| P1 Fan-out | N siblings, same role | Research 5 angles in parallel |
| P2 Pipeline | Role chain | Scout → editor → writer |
| P3 Voting / quorum | N siblings + 1 aggregator | 3 researchers → 1 reviewer picks |
| P4 Long-running journal | Same profile + shared dir + cron | Obsidian vault maintenance |
| P5 Human-in-the-loop | Worker blocks → user comments → unblock | Ambiguous decisions |
| P6 @mention | Inline routing from prose | `@reviewer look at this` |
| P7 Thread-scoped workspace | `/kanban here` in a thread | Per-project gateway threads |
| P8 Fleet farming | One profile, N subjects | 50 social accounts |

### Kanban vs delegate_task

| | `delegate_task` | Kanban |
|---|---|---|
| Shape | RPC call (fork → join) | Durable message queue + state machine |
| Resumability | None — failed = failed | Block → unblock → re-run; crash → reclaim |
| Child identity | Anonymous subagent | Named profile with persistent memory |
| Human in loop | Not supported | Comment / unblock at any point |
| Audit trail | Lost on context compression | Durable SQLite rows forever |

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kanban.dispatch_interval_seconds` | 60 | Dispatcher tick interval |
| `kanban.dispatch_stale_timeout_seconds` | 14400 (4h) | Reclaim running tasks with no recent heartbeat |
| `kanban.failure_limit` | 2 | Auto-block after N consecutive spawn failures |
| `kanban.auto_decompose` | `true` | Auto-run decomposer on triage tasks |
| `kanban.auto_decompose_per_tick` | 3 | Cap on decompositions per tick |

## When To Use

- Work crosses agent boundaries and needs to survive restarts.
- Human input may be required mid-workflow.
- Tasks might be picked up by a different role than originally assigned.
- Audit trail must be discoverable after the fact.
- Long-running operations that outlive a single conversation turn.

## Risks & Pitfalls

- **Gateway dependency**: The dispatcher runs inside the gateway. Without a running gateway, `ready` tasks stall. Run `hermes gateway start`.
- **Profile existence**: The dispatcher silently fails on unknown assignee names. Orchestrators must ground every task in profiles that actually exist.
- **Workspace path safety**: Only absolute paths accepted for `dir:<path>`. Relative paths are rejected to prevent confused-deputy escapes.
- **Protocol violation**: If a worker exits without `kanban_complete` / `kanban_block`, the dispatcher auto-blocks the task on the next tick.
- **Heartbeat neglect**: Tasks without heartbeats for >1 hour during operations >4 hours are reclaimed. Call `kanban_heartbeat` at least hourly for long work.

## v1 Specification Details

The April 2026 v1 design spec formalizes the kernel boundary and adds explicit semantics not present in the general user-guide description.

### SQLite schema (v1)

Four tables, three indexes, no JSON masquerading as schema:

- `tasks` — id, title, body, assignee, status, priority, created_by, created_at, started_at, completed_at, workspace_kind, workspace_path, claim_lock, claim_expires
- `task_links` — parent_id → child_id foreign-key pairs
- `task_comments` — id, task_id, author, body, created_at
- `task_events` — id, task_id, kind, payload (opaque JSON diagnostics only), created_at

### Status semantics and ownership

| Status | Owner | Meaning |
|--------|-------|---------|
| `todo` | creator | Created, one or more parents not yet done. |
| `ready` | dispatcher | All parents done; eligible for atomic claim. |
| `running` | worker | Claimed by a profile process; worker is executing. |
| `blocked` | worker | Requires peer or human input to proceed. |
| `done` | worker | Completion result written; triggers child re-evaluation. |
| `archived` | user | Removed from default views; workspace may be GC’d. |

Only one role may transition each status. This separation eliminates write contention.

### Assignment semantics (v1)

- Exactly one assignee per task (profile name). No multi-assignee, no round-robin pools, no auto-claim queues in v1.
- Worker prompt contains, in order: task title, task body, every comment chronologically, completion results of every parent task, and the worker’s normal skills/memory.
- If it is not visible on `hermes kanban show <id>`, the worker cannot see it.

### Scope boundaries: explicitly out of kernel

| Proposed feature | User-space realization |
|------------------|----------------------|
| Smart routing / auto-assignment | Router profile scans unassigned tasks and reassigns. |
| Org chart / hierarchy | Profile naming convention + skills. |
| Budgets per agent | Plugin wrapping spawn to enforce limits. |
| Fleet dashboards | Dashboard plugin reading the board. |
| Approval gates | Reuse `tools/approval.py`. |
| Governance control plane | Router + budget plugin + audit-export plugin. |

### Collaboration patterns (P1–P8)

The v1 spec documents eight reusable idioms:

- **P1 Fan-out** — one role, N siblings, no dependencies.
- **P2 Pipeline** — role-specialized chain (scout → editor → writer).
- **P3 Voting / Quorum** — N workers race or vote; an aggregator picks.
- **P4 Long-running journal** — same profile + shared dir + recurring tasks.
- **P5 Human-in-the-loop** — block → comment → unblock.
- **P6 @mention delegation** — `@<profile-name>` implicitly creates a task.
- **P7 Thread-scoped workspace** — workspace pinned to a conversation thread.
- **P8 Fleet farming** — one specialist, N parallel tasks, one workspace per subject.

### Kanban vs `delegate_task` (v1)

The v1 spec offers a twelve-dimension comparison. The one-sentence distinction: `delegate_task` is a function call; Kanban is a durable work queue where every handoff is a row any profile (or human) can read and edit.

- Use `delegate_task` for short, self-contained reasoning subtasks (seconds to minutes, no human in the loop, result consumed immediately by parent).
- Use Kanban for work that crosses agent boundaries, needs to survive restarts, might need human input, might be picked up by a different role, or needs to be discoverable after the fact.

## Related Concepts

- [[concepts/hermes-subagent-delegation]]
- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-profile-isolation]]
- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-kanban-dispatcher]]
- [[concepts/hermes-kanban-orchestrator-profile]]
- [[concepts/hermes-kanban-tenant]]

## Sources

- `user-guide/features/kanban.md`
- `docs/hermes-kanban-v1-spec.pdf` §1–§5, §9–§11, §14–§17
