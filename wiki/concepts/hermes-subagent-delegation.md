---
title: "Hermes Subagent Delegation"
type: concept
tags: [concept, ai-agent, parallelism, subagent, isolation]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-agent-docs/website/docs"]
confidence: high
---

## Definition

Hermes Subagent Delegation is a mechanism for spawning isolated child AIAgent instances via the `delegate_task` tool. Each child gets a fresh conversation, restricted toolsets, its own terminal session, and an independent iteration budget. Only the final summary enters the parent's context.

## How It Works

### Single Task

```python
delegate_task(
    goal="Debug why tests fail",
    context="Error: assertion in test_foo.py line 42",
    toolsets=["terminal", "file"]
)
```

### Parallel Batch

Up to 3 concurrent subagents by default (configurable, no hard ceiling):

```python
delegate_task(tasks=[
    {"goal": "Research topic A", "toolsets": ["web"]},
    {"goal": "Research topic B", "toolsets": ["web"]},
    {"goal": "Fix the build", "toolsets": ["terminal", "file"]}
])
```

### Critical Isolation Property

Subagents start with **completely fresh conversations**. They have zero knowledge of the parent's history, prior tool calls, or anything discussed before delegation. The parent must pass everything the subagent needs in the `goal` and `context` fields.

### Toolset Restrictions

Blocked tools for leaf subagents:
- `delegate_task` — blocked by default (see depth limit below)
- `clarify` — subagents cannot interact with the user
- `memory` — no writes to shared persistent memory
- `code_execution` — children should reason step-by-step
- `send_message` — no cross-platform side effects

### Depth Limit and Nested Orchestration

By default, delegation is flat (depth 1). A parent spawns children, and children cannot delegate further. For multi-stage workflows, a parent can spawn `role="orchestrator"` children that can delegate their own workers, gated by `delegation.max_spawn_depth` (default 1, max 3).

### Interrupt Propagation

Interrupting the parent (new message, `/stop`, signal) interrupts all active children. Cancelled children return `status="interrupted"`.

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `delegation.max_concurrent_children` | 3 | Parallel children per batch |
| `delegation.max_iterations` | 50 | Max turns per child |
| `delegation.max_spawn_depth` | 1 | Tree depth (1=flat, max 3) |
| `delegation.child_timeout_seconds` | 600 | Wall-clock timeout per child |
| `delegation.orchestrator_enabled` | `true` | Global kill switch for nested delegation |

## When To Use

- **Parallel research**: Multiple topics investigated simultaneously with collected summaries.
- **Code review + fix**: Delegate review-and-fix to fresh context without flooding parent's context window.
- **Multi-file refactoring**: Large changes that would consume too many parent turns.
- **Isolated reasoning**: Tasks requiring judgment where intermediate tool results should not bloat parent context.

## Risks & Pitfalls

- **Context starvation**: Bad delegation passes insufficient context (`goal="Fix the error"`). The subagent has no idea what "the error" is. Always include file paths, error messages, and project structure.
- **Cost multiplication**: With `max_spawn_depth: 3` and `max_concurrent_children: 3`, the tree can reach 27 concurrent leaf agents. Each extra level multiplies spend.
- **Synchronous, not durable**: `delegate_task` blocks the parent until children finish. For durable long-running work, use `cronjob` or `terminal(background=True)`.
- **Timeout on reasoning models**: High-reasoning models on non-trivial tasks may exceed the default 10-minute timeout. Tune `child_timeout_seconds` per model.
- **Protocol violation**: If a subagent exits without calling `kanban_complete` or `kanban_block` when running under Kanban, the dispatcher auto-blocks the task.

## Related Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-agent-loop]]
- [[concepts/hermes-cron-scheduler]]

## Sources

- `user-guide/features/delegation.md`
