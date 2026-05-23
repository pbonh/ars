---
title: "Pi Subagent Child-Safety Boundary"
type: concept
tags: [concept, pi, subagent, safety, isolation]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

Pi subagent child-safety boundaries are the runtime constraints that keep a
delegated child from acting as a parent orchestrator: spawned children do not
receive the bundled orchestration [[concepts/pi-skill|skill]], their forked
context is filtered to remove parent-only artifacts, and they cannot run further
subagents unless explicitly authorized.

## How It Works

These boundaries are enforced at runtime, not merely by prompt convention:

- **No bundled skill for children.** The package's `pi-subagents` skill is for
  the orchestrating parent only; child subagents never receive it.
- **Context filtering.** Forked child context removes parent-only subagent
  artifacts — old hidden orchestration-instruction messages, slash/status/control
  messages, and prior parent `subagent` tool-call/tool-result history — while
  preserving ordinary prose and unrelated tool calls/results (see
  [[concepts/pi-forked-context]]).
- **No subagent tool by default.** Children do not register the `subagent` tool
  and receive boundary instructions stating they are not the parent orchestrator
  and must not propose or run subagents. The explicit exception is an agent whose
  resolved builtin `tools` include `subagent`, which gets a child-safe `subagent`
  tool bounded by [[concepts/pi-subagent-recursion-guard|maxSubagentDepth]].
- **Scoped status inside fanout.** In child-safe fanout mode, a bare `status`
  requires an id when no local foreground run is active, so a child cannot
  enumerate unrelated top-level async runs; bare `interrupt` only targets the
  visible top-level run.
- **No-edit wins.** When the only conflict is review-only/no-edit versus
  progress-writing or artifact-writing instructions, no-edit wins; a child
  should not ask for clarification on that conflict.

## Key Parameters

- `completionGuard` — read-only-tool agents skip the implementation completion
  guard; set `false` for bash-enabled validators/advisors that should never be
  judged as implementation agents.
- `tools: subagent` — the only way to grant a child nested-fanout capability.

## When To Use

This is a property of the system rather than something you toggle per task; rely
on it to:

- Delegate to a child without leaking parent orchestration machinery into it.
- Give a fanout agent controlled nested delegation while keeping ordinary
  children unable to spawn.

## Risks & Pitfalls

- An agent author may *expect* a child to inherit orchestration skill/context;
  by design it does not — pass needed context explicitly in the task.
- Granting `tools: subagent` widens what a child can do; combine with a tight
  `maxSubagentDepth`.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-forked-context]]
- [[concepts/pi-subagent-recursion-guard]]
- [[concepts/pi-agent-definition]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
