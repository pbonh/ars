---
title: "Pi Subagent Execution Mode"
type: concept
tags: [concept, pi, subagent, concurrency, async]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

A Pi subagent execution mode is the manner in which a delegated run is launched
and observed: in the **foreground** (streaming in the conversation) or in the
**background**/async (detached, with completion delivered later), across the
**single**, **parallel**, and **chain** orchestration shapes.

## How It Works

### Foreground vs background

- **Foreground** runs stream compact live progress (current tool, recent
  output, token counts, duration); `Ctrl+O` expands the full streaming view.
- **Background** (`--bg` / `async: true`) runs keep working after control
  returns to the parent. They emit a compact async widget and a completion
  notification. A detached parent with no other useful work should end the turn
  rather than run sleep/status-polling loops — Pi delivers completion when the
  run finishes.

### Orchestration shapes

- **Single**: `{ agent, task }`.
- **Parallel**: `{ tasks: [...] }`, with `concurrency` (default 4, `maxTasks`
  default 8) and optional `count` to fan one task into N copies.
- **Chain**: `{ chain: [...] }` — see [[concepts/pi-subagent-chain]]. Chains may
  contain `parallel:` groups that keep their grouped shape in progress and
  results.

### Status and control

Background and nested runs are inspected and steered with management actions:

```ts
subagent({ action: "status" })                       // active runs
subagent({ action: "status", id: "<run-id>" })       // one run (or nested id)
subagent({ action: "interrupt", id: "<run-id>" })
subagent({ action: "resume", id: "<run-id>", message: "follow-up" })
subagent({ action: "doctor" })                        // setup diagnostics
```

`status` resolves exact foreground, top-level async, and nested ids before
prefix matching. `resume` sends a follow-up over [[entities/pi-intercom|intercom]]
when the child is still reachable; after completion it revives the child from
its stored `.jsonl` session file (a new child process, not the same OS process).

### Files and events

Async runs write `status.json`, `events.jsonl`, `output-<n>.log`, and a Markdown
log under `<tmpdir>/pi-subagents-<scope>/async-subagent-runs/<id>/`. The result
watcher emits `subagent:async-started` and `subagent:async-complete`; the
extension consumes the latter to render completion notifications, which notify
only the originating session.

## Key Parameters

- `async` (default `false`); for chains, `clarify: true` keeps the run
  foreground for the clarify UI.
- `concurrency` (per-call beats config; config default 4).
- `asyncByDefault` / `forceTopLevelAsync` config flags make depth-0 runs
  background by default (the latter also bypasses clarify).
- `maxOutput` (default 200KB / 5000 lines) truncates final output.

## When To Use

- **Foreground** for short, interactive work you want to watch.
- **Background** for long-running audits or implementations while you continue
  other work; check back with `status`.
- **Parallel** for independent tasks (multi-angle review, multi-topic research).
- **Chain** for ordered pipelines with intermediate handoffs.

## Risks & Pitfalls

- Polling background runs in a tight loop wastes turns — end the turn and let
  the completion notification arrive.
- Parallel runs that edit the same files need [[concepts/pi-worktree-isolation]].
- `resume`/revive requires a persisted `.jsonl` session file; ephemeral runs
  cannot be revived.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-subagent-chain]]
- [[concepts/pi-worktree-isolation]]
- [[concepts/pi-session-format]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
