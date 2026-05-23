---
title: "Pi Forked Context"
type: concept
tags: [concept, pi, subagent, session, context]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

Pi forked context (`context: "fork"`) starts a [[concepts/pi-subagent|subagent]]
from a real branched session created from the parent's current leaf, rather than
from a clean slate. It is the alternative to `context: "fresh"`, where the child
begins with only the task and any explicitly-passed context.

## How It Works

- With `context: "fork"`, each child launches with
  `--session <branched-session-file>` produced from the parent's current leaf.
  This is a genuine [[concepts/pi-session-format|session]] fork — a real branched
  conversation, **not** an injected summary.
- `fork` **fails fast** when the parent session is not persisted, the current
  leaf is missing, or the branched child session cannot be created. It never
  silently downgrades to `fresh`.
- Packaged `planner`, `worker`, and `oracle` default to forked context when a
  launch omits `context`; pass `context: "fresh"` to override.
- In a multi-agent run, if any requested agent has `defaultContext: fork` and
  the launch omits `context`, the whole invocation uses forked context.
- Even with a fork, parent-only subagent artifacts are stripped from the child
  by context filtering (see [[concepts/pi-subagent-child-safety-boundary]]):
  old orchestration-instruction messages, slash/status/control messages, and
  prior parent `subagent` tool-call/result history are removed, while ordinary
  prose and unrelated tool calls/results are preserved.

## Key Parameters

- `context`: `"fresh" | "fork"` (agent default, else `fresh`).
- `defaultContext: fork` in agent frontmatter sets the per-agent default;
  explicit `context: "fresh"` still wins.

## When To Use

- The child needs to continue the same thread of work the parent was doing
  (e.g. "continue this thread", review a diff in the parent's working context).
- You want the implementation agents (`worker`, `planner`, `oracle`) to see the
  conversation history — which is why they default to fork.

## Risks & Pitfalls

- `fork` requires a persisted parent session; in-memory or unpersisted sessions
  fail the launch rather than degrade.
- A fork carries more context (and cost) into the child than `fresh`; use
  `fresh` for narrow, self-contained tasks.
- Filtering removes parent orchestration artifacts but keeps unrelated tool
  results, so a forked child may still see large unrelated history.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-session-format]]
- [[concepts/pi-subagent-child-safety-boundary]]
- [[concepts/pi-agent-definition]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
