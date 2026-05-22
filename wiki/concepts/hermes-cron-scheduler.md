---
title: "Hermes Cron Scheduler"
type: concept
tags: [concept, ai-agent, cron, scheduling, automation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

The Hermes Cron Scheduler is a first-class scheduled-task system for agent work. It runs inside the gateway daemon, ticks every 60 seconds, and executes due jobs in fresh AIAgent sessions. Jobs can attach skills, deliver to any messaging platform, run in specific working directories or profiles, and even operate in no-agent mode (script-only) for pure automation.

## How It Works

### Execution Flow

1. Gateway ticks scheduler every 60s.
2. Loads jobs from `~/.hermes/cron/jobs.json`.
3. Checks `next_run_at` against current time.
4. Starts a fresh `AIAgent` session for each due job (no chat history).
5. Optionally injects attached skills.
6. Runs the prompt to completion.
7. Delivers final response to configured target.
8. Updates run metadata and next scheduled time.

A file lock at `~/.hermes/cron/.tick.lock` prevents overlapping ticks from double-running jobs.

### Job Storage

Jobs are stored in JSON with atomic file writes. Output saved to `~/.hermes/cron/output/{job_id}/{timestamp}.md`.

### Delivery Targets

| Target | Description |
|--------|-------------|
| `origin` | Back to where the job was created |
| `local` | Save to `~/.hermes/cron/output/` only |
| `telegram`, `discord`, `slack`, ... | Any configured messaging platform |
| `all` | Every connected home channel |
| `origin,all` | Origin plus every other channel |

### Skill-Backed Jobs

Jobs can load zero, one, or multiple skills before running the prompt:

```python
cronjob(
    action="create",
    skills=["blogwatcher", "maps"],
    prompt="Look for new local events and interesting nearby places, then combine them into one short brief.",
    schedule="every 6h",
)
```

### No-Agent Mode (Script-Only)

For recurring watchdogs or alerts that don't need LLM reasoning:

```bash
hermes cron create "every 5m" \
  --no-agent \
  --script memory-watchdog.sh \
  --deliver telegram \
  --name "memory-watchdog"
```

- Script stdout (trimmed) → delivered verbatim.
- Empty stdout → silent tick (no delivery).
- Non-zero exit or timeout → error alert delivered.
- No tokens, no model, no provider fallback.

### Job Chaining with context_from

Job B's prompt gets Job A's most recent output prepended as context at runtime:

```python
cronjob(
    action="create",
    name="AI News Triage",
    schedule="30 7 * * *",
    context_from="<job1_id>",
    prompt="Read the raw stories and score each 1–10 for engagement...",
)
```

### wakeAgent Gate

A pre-check script can emit `{"wakeAgent": false}` as its final stdout line to skip the agent run for that tick. Useful for frequent polls that only need the LLM when state actually changed.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `cron.script_timeout_seconds` | 120 | Pre-run script timeout |
| `cron.wrap_response` | `true` | Wrap delivered output with cron header/footer |
| `enabled_toolsets` | job-specific | Per-job toolset restriction for cost control |

## Schedule Formats

- **Relative delays**: `30m`, `2h`, `1d` (one-shot)
- **Intervals**: `every 30m`, `every 2h`, `every 1d`
- **Cron expressions**: `0 9 * * *`, `0 */6 * * *`
- **ISO timestamps**: `2026-03-15T09:00:00`

## When To Use

- **Monitoring**: Periodic health checks, log audits, feed summaries.
- **Publishing**: Scheduled social posts, newsletters, briefs.
- **Maintenance**: Nightly backups, cleanup tasks, report generation.
- **Watchdogs**: Threshold alerts (disk, memory, error rates) via no-agent mode.

## Risks & Pitfalls

- **Gateway dependency**: Cron runs inside the gateway. If the gateway stops, jobs don't fire.
- **Self-contained prompts**: Jobs run in fresh sessions with no memory of previous runs. The prompt must contain everything the agent needs.
- **No recursive cron**: Cron-run sessions cannot create more cron jobs — prevents runaway scheduling loops.
- **Workdir/profile serialization**: Jobs with `workdir` or `profile` run sequentially (not parallel) because these are process-global mutations.
- **Rate limit fragility**: High-frequency jobs without `wakeAgent` gates waste tokens on zero-content runs.

## Related Concepts

- [[concepts/hermes-gateway]]
- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-skills-system]]

## Sources

- `user-guide/features/cron.md`
- `developer-guide/cron-internals.md`
