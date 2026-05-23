---
title: "pi-subagents README"
type: summary
tags: [summary, pi, subagent, multi-agent, delegation, extension]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Overview

`pi-subagents` is a third-party [[concepts/pi-extension|extension]] for
[[entities/pi|Pi]] (by GitHub user `nicobailon`) that lets a parent Pi session
delegate work to focused child agents — [[concepts/pi-subagent|subagents]]. A
subagent is itself a Pi session with its own job: the parent starts the child,
gives it a task, and brings the result back. The extension is installed with one
command (`pi install npm:pi-subagents`) and adds a `subagent` tool plus slash
commands; crucially, installing it does **not** start any automatic background
behavior — it only gives Pi a delegation capability the parent chooses when to
use.

The README's central message is that most usage should be conversational: the
user asks in plain language ("Use reviewer to review this diff", "Ask oracle for
a second opinion", "Run parallel reviewers for correctness, tests, and
complexity"), and Pi decides whether to delegate, which agent to use, and
whether a single, [[concepts/pi-subagent-execution-mode|parallel, chained, or
background]] run makes sense. Eight builtin specialists ship ready to use:
`scout`, `researcher`, `planner`, `worker`, `reviewer`, `context-builder`,
`oracle`, and `delegate`. Custom specialists are declared as
[[concepts/pi-agent-definition|agent definition]] Markdown files, and repeatable
multi-step workflows as [[concepts/pi-subagent-chain|`.chain.md`]] files.

Much of the document is reference material for the power features: forking real
branched sessions into children ([[concepts/pi-forked-context]]); running
parallel implementers in isolated git worktrees
([[concepts/pi-worktree-isolation]]); bounding nested delegation with a
[[concepts/pi-subagent-recursion-guard|recursion guard]]; and the runtime
[[concepts/pi-subagent-child-safety-boundary|child-safety boundaries]] that keep
children from acting as orchestrators. An optional companion,
[[entities/pi-intercom]], lets children call back to the parent for decisions
instead of guessing.

## Key Claims

- A subagent is a focused child Pi session; the parent delegates and integrates
  results back. Installing the extension adds a tool, not an automatic agent.
  ([[concepts/pi-subagent]])
- Delegation is preferably driven by natural language; direct `subagent` tool
  calls and `/run`, `/chain`, `/parallel`, `/run-chain` commands exist for exact
  control. ([[concepts/pi-subagent-execution-mode]])
- Agents are Markdown + YAML-frontmatter definitions discovered across builtin,
  user, and project scopes, narrow by default, and tunable via
  `subagents.agentOverrides`. ([[concepts/pi-agent-definition]])
- Chains are reusable `.chain.md` workflows with `{task}`/`{previous}`/`{chain_dir}`
  variables and fan-out/fan-in parallel groups. ([[concepts/pi-subagent-chain]])
- Runs are foreground (streaming) or background/async (detached, with completion
  notifications), and are inspected/steered with `status`, `interrupt`,
  `resume`, and `doctor`. ([[concepts/pi-subagent-execution-mode]])
- `context: "fork"` starts children from a real branched parent session and
  fails fast rather than silently downgrading to `fresh`.
  ([[concepts/pi-forked-context]])
- Nesting is bounded (default depth 2) and a child can delegate only if its
  resolved tools include `subagent`. ([[concepts/pi-subagent-recursion-guard]])
- Children never receive the bundled orchestration skill, have parent-only
  artifacts filtered out, and cannot run subagents by default — enforced at
  runtime. ([[concepts/pi-subagent-child-safety-boundary]])
- `worktree: true` isolates each parallel child in its own git worktree branched
  from `HEAD`, capturing per-agent diffs. ([[concepts/pi-worktree-isolation]])
- The optional [[entities/pi-intercom]] companion gives children a
  `contact_supervisor` channel to request decisions and delivers grouped
  completion results to the parent.

## Source Metadata

- **Type**: Project README (Markdown)
- **Owner**: `nicobailon` (third-party Pi extension author)
- **URL**: https://github.com/nicobailon/pi-subagents/blob/main/README.md
- **License**: Not stated in the README
- **Ingested on**: 2026-05-23

## Relevant Concepts

- [[concepts/pi-subagent]]
- [[concepts/pi-agent-definition]]
- [[concepts/pi-subagent-chain]]
- [[concepts/pi-subagent-execution-mode]]
- [[concepts/pi-forked-context]]
- [[concepts/pi-subagent-recursion-guard]]
- [[concepts/pi-subagent-child-safety-boundary]]
- [[concepts/pi-worktree-isolation]]
</content>
