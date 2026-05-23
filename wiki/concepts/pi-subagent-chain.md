---
title: "Pi Subagent Chain"
type: concept
tags: [concept, pi, subagent, workflow, orchestration]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

A Pi subagent chain is a reusable multi-step workflow that runs several
[[concepts/pi-agent-definition|agents]] in sequence and/or in parallel, passing
each step's output to the next. Chains are stored as `.chain.md` files,
separate from agent files, and can also be expressed inline via the `subagent`
tool's `chain` parameter or the `/chain` slash command.

## How It Works

### Chain files

| Scope | Path |
|-------|------|
| User | `~/.pi/agent/chains/**/*.chain.md` |
| Project | `.pi/chains/**/*.chain.md` |

Each `## agent-name` section is a step. Config lines (`output`, `outputMode`,
`reads`, `model`, `skills`, `progress`) go immediately after the header,
separated from the task text by a blank line. Config is three-state: omitted
inherits from the agent, a value overrides, and `false` disables. Chains also
support the optional `package` frontmatter; project wins runtime-name
collisions.

### Variables

Task templates interpolate:

| Variable | Meaning |
|----------|---------|
| `{task}` | Original task from the first step. |
| `{previous}` | Output from the prior step, or aggregated output from a parallel step. |
| `{chain_dir}` | Path to the chain artifact directory. |

Parallel step outputs are aggregated with clear separators
(`=== Parallel Task N (agent) ===`) before being passed to the next step.

### Fan-out / fan-in

A chain step can be a `parallel:` group with `concurrency`, `failFast`, and
`worktree` options, letting several agents run concurrently between sequential
steps:

```ts
{ chain: [
  { agent: "scout", task: "Gather context" },
  { parallel: [
    { agent: "worker", task: "Implement feature A from {previous}" },
    { agent: "worker", task: "Implement feature B from {previous}" }
  ], concurrency: 2, failFast: true },
  { agent: "reviewer", task: "Review all changes from {previous}" }
]}
```

### Per-step tasks and config

In slash commands, `->` separates steps; `--` gives a shared task to listed
agents. Steps without a task inherit `{previous}` (chains) or the first
available task (parallel). Inline `[key=value,...]` after an agent name
overrides defaults for that step (`output`, `outputMode`, `reads`, `model`,
`skills`, `progress`).

## Key Parameters

- Create chains by writing `.chain.md` directly or via
  `subagent({ action: "create", config: { steps: [...] } })`.
- Run with `/run-chain <chainName> -- <task>` or natural language.
- Chains open a clarify UI by default to preview/edit before running.

## When To Use

- You repeat the same multi-agent shape often (e.g. scout → plan → implement →
  review) and want it saved.
- You need fan-out/fan-in: parallel implementation or review with a synthesis
  step afterward.
- Use the packaged shortcuts (`/parallel-review`, `/review-loop`, etc.) when you
  want the same shape without authoring a chain file.

## Risks & Pitfalls

- Parallel workers editing the same checkout can clobber each other; combine
  with [[concepts/pi-worktree-isolation]].
- `failFast` aborts the whole parallel group on first failure — omit it when
  partial results are still useful.
- Output passed via `{previous}` can be large; use `outputMode: file-only` so
  later steps receive a compact file reference instead of full content.

## Related Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-agent-definition]]
- [[concepts/pi-subagent-execution-mode]]
- [[concepts/pi-worktree-isolation]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
