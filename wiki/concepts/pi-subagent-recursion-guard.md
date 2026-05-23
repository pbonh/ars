---
title: "Pi Subagent Recursion Guard"
type: concept
tags: [concept, pi, subagent, safety, depth-limit]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

The Pi subagent recursion guard is the depth limit that prevents unbounded
nesting of [[concepts/pi-subagent|subagents]]. A child may call `subagent` only
when its resolved builtin tools explicitly include `subagent`, and even then a
configurable maximum depth blocks runs that would nest too deeply.

## How It Works

- By default nesting is limited to two levels:
  `main session → subagent → sub-subagent`. Deeper calls are blocked with
  guidance to complete the current task directly.
- Only an agent whose resolved builtin `tools` include `subagent` receives a
  child-safe `subagent` tool for delegated fanout; ordinary `worker`/`reviewer`
  children cannot delegate. An `mcp:` entry named `subagent` does **not**
  authorize fanout — only the builtin tool name does.
- Nested runs appear in the parent status tree, and `status`, `interrupt`, and
  `resume` can target a nested run by its id.
- The limit is configured, in increasing specificity:
  1. `PI_SUBAGENT_MAX_DEPTH` environment variable before starting Pi
  2. `config.maxSubagentDepth`
  3. `maxSubagentDepth` in agent frontmatter — which can only **tighten** the
     inherited limit, never relax it.
- `PI_SUBAGENT_DEPTH` is internal and propagated automatically; it must not be
  set manually.

## Key Parameters

| Setting | Effect |
|---------|--------|
| `PI_SUBAGENT_MAX_DEPTH=0` | No subagents at all. |
| `PI_SUBAGENT_MAX_DEPTH=1` | Flat: parent spawns children; children cannot delegate. |
| `PI_SUBAGENT_MAX_DEPTH=3` | Up to three nesting levels. |
| agent `maxSubagentDepth` | Tightens (only) the limit for that agent's children. |

At the cap, execution fanout is **blocked** rather than silently hiding nested
work.

## When To Use

- Keep the default (depth 2) for normal use.
- Lower it (`0`/`1`) to forbid or flatten delegation for untrusted or
  cost-sensitive runs.
- Raise it deliberately only for genuine multi-stage orchestration, mindful of
  combinatorial cost.

## Risks & Pitfalls

- Cost and concurrency multiply with depth: deep nesting combined with high
  parallel `concurrency` can spawn a large tree of concurrent children.
- A child expecting to delegate but lacking `subagent` in its tools will be
  blocked — declare `tools: subagent` for intentional fanout agents.
- Per-agent limits can only tighten; you cannot widen an inherited stricter cap
  from frontmatter.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-subagent-child-safety-boundary]]
- [[concepts/pi-agent-definition]]
- [[concepts/hermes-subagent-delegation]] — depth-limited delegation in a different harness

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
