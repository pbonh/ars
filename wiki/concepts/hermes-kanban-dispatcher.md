---
title: "Hermes Kanban Dispatcher"
type: concept
tags: [concept, ai-agent, kanban, dispatcher, sqlite, cron, concurrency]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-kanban-v1-spec.pdf"]
confidence: high
---

## Definition

The Hermes Kanban Dispatcher is a deliberately dumb, cron-triggered process that is the only component allowed to transition tasks from `ready` to `running`. It implements exactly four operations against the shared SQLite board: recompute ready statuses, atomically claim tasks via compare-and-swap, spawn the assigned profile as a full OS process, and recover stale claims from crashed or killed workers.

## How It Works

### Three-plane separation

The dispatcher sits in the **state plane**, between the **control plane** (users and gateway) and the **execution plane** (worker profiles). All coordination flows through the board; there is no direct inter-process communication between profiles.

### The four operations

1. **Recompute ready**. For each task in `todo`, if all parent links resolve to tasks in `done`, transition the task to `ready`.
2. **Atomic claim**. For each `ready` task with `claim_lock IS NULL` and `assignee IS NOT NULL`, issue a compare-and-swap `UPDATE` setting `status='running'`, `claim_lock=<host>:<pid>`, and `claim_expires=now+900` seconds.
3. **Spawn worker**. For each successful claim, resolve the workspace (create scratch dir, ensure worktree, or validate shared dir) and execute `hermes -p <assignee> -w <workspace> chat -q "work kanban task <id>"`.
4. **Stale claim recovery**. For each `running` task with `claim_expires < now`, reset `status='ready'` and `claim_lock=NULL`.

### Concurrency correctness

The dispatcher may overlap with itself (cron ticks) and with manual `hermes kanban claim` invocations. Correctness rests on SQLite `BEGIN IMMEDIATE` transaction semantics plus a row-level CAS pattern:

```sql
BEGIN IMMEDIATE;
UPDATE tasks
SET status = 'running', claim_lock = ?, claim_expires = ?, started_at = ?
WHERE id = ? AND status = 'ready' AND claim_lock IS NULL;
COMMIT;
```

Because `WHERE status='ready' AND claim_lock IS NULL` is re-evaluated inside the transaction and SQLite serializes writers via its WAL lock, at most one claimer wins any given task. Losers observe zero affected rows and move on.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `kanban.dispatch_interval_seconds` | 60 | Cron tick interval |
| `kanban.dispatch_stale_timeout_seconds` | 900 (15 min) | Claim expiry before stale recovery |
| `kanban.failure_limit` | 2 | Auto-block after N consecutive spawn failures |

## When To Use

- The dispatcher is the default execution model for all [[concepts/hermes-kanban-board]] workloads. It is always on when `hermes gateway start` is running.
- It is the correct coordination primitive when work must survive host reboots, profile crashes, or concurrent manual claims.

## Risks & Pitfalls

- **SQLite cross-process contention**: Multiple profiles writing simultaneously can stall. Mitigation: WAL mode, short-held locks, no long reads inside write transactions.
- **Cron scheduler drift on laptop sleep/wake**: Missed ticks. Mitigation: every `hermes kanban` CLI invocation runs a cheap mini-dispatch to recompute ready states.
- **Profile misconfiguration at spawn**: Cron launches a profile that lacks necessary skills. Mitigation: verify profile existence on assign; warn if the `kanban-worker` skill is disabled.
- **Runaway automation chains**: Auto-completing tasks can chain infinitely. Mitigation: optional `--require-approval` flag on create.

## Related Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-profile-isolation]]
- [[concepts/hermes-subagent-delegation]]

## Sources

- `docs/hermes-kanban-v1-spec.pdf` §3, §4, §12
