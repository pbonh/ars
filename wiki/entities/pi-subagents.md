---
title: "pi-subagents"
type: entity
tags: [entity, tool, pi-extension, subagent, multi-agent]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Overview

`pi-subagents` is a third-party [[concepts/pi-extension|extension]] for
[[entities/pi|Pi]], authored by GitHub user `nicobailon`
(github.com/nicobailon/pi-subagents), that lets a parent Pi session delegate
work to focused child agents. It supports code review, scouting, implementation,
parallel audits, saved workflows, and background jobs — "anything that benefits
from a second or third set of model eyes." It is installed with one command and
adds a `subagent` delegation tool plus slash commands; it does not start any
automatic background agent on its own. It is distinct from
[[entities/earendil-works]], which maintains Pi's core.

## Characteristics

- **Install**: `pi install npm:pi-subagents`
- **Primary tool**: `subagent` (single, parallel `tasks`, or `chain` modes) plus
  `/run`, `/chain`, `/parallel`, `/run-chain`, and `/subagents-doctor` commands.
- **Eight builtin agents**: `scout`, `researcher`, `planner`, `worker`,
  `reviewer`, `context-builder`, `oracle`, `delegate` — see
  [[concepts/pi-subagent]].
- **Builtin agents inherit the current Pi default model** unless overridden via
  `subagents.agentOverrides.<name>`.
- **Packaged prompt shortcuts**: `/parallel-review`, `/review-loop`,
  `/parallel-research`, `/parallel-context-build`, `/parallel-handoff-plan`,
  `/gather-context-and-clarify`, `/parallel-cleanup` (add `autofix` to apply
  synthesized fixes).
- **Bundled parent-only skill** that teaches delegation patterns; children never
  receive it (see [[concepts/pi-subagent-child-safety-boundary]]).
- **Companion extensions**: [[entities/pi-intercom]] (child↔parent
  coordination), [[entities/pi-web-access]] (for `researcher`),
  [[entities/pi-mcp-adapter]] (direct MCP tools),
  [[entities/pi-prompt-template-model]] (wrap delegation in prompt templates).
- **Config file**: `~/.pi/agent/extensions/subagent/config.json`
  (`asyncByDefault`, `forceTopLevelAsync`, `parallel`, `defaultSessionDir`,
  `maxSubagentDepth`, `intercomBridge`, `worktreeSetupHook`).

## Common Strategies

- Ask in plain language: "Use reviewer to review this diff", "Ask oracle for a
  second opinion on my current plan", "Run parallel reviewers: one for
  correctness, one for tests, one for unnecessary complexity."
- Run the recommended implementation loop
  `clarify → planner → worker → fresh reviewers → worker` as parent-side
  scaffolding (not a runtime mode).
- Use a [[concepts/pi-subagent-chain|chain]] (`.chain.md`) to save a repeated
  multi-step shape, optionally with parallel fan-out and
  [[concepts/pi-worktree-isolation|worktree isolation]].
- Run audits/implementations in the [[concepts/pi-subagent-execution-mode|background]]
  and let the completion notification arrive instead of polling.
- Run `/subagents-doctor` to diagnose setup problems.

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
