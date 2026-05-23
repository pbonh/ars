---
title: "Pi Subagent"
type: concept
tags: [concept, pi, subagent, delegation, multi-agent]
created: 2026-05-23
updated: 2026-05-23
sources: ["raw/pi-subagents-readme.md"]
confidence: high
---

## Definition

A Pi subagent is a focused child [[entities/pi|Pi]] session with its own job,
launched by a parent Pi session to handle a delegated task. The parent starts
the child, gives it the task, and brings the result back into the conversation.
Subagents are provided by the [[entities/pi-subagents]] extension rather than
by Pi's core.

## How It Works

1. The user asks the parent Pi session for delegation in plain language
   ("Use reviewer to review this diff"), or calls the `subagent` tool, or runs
   a slash command (`/run`, `/chain`, `/parallel`).
2. Pi decides whether to call `subagent`, which named [[concepts/pi-agent-definition|agent]]
   to use, and whether a single, parallel, or chained run is appropriate.
3. The child runs as a separate Pi process, then returns a result that is
   integrated back into the parent conversation.
4. Installing the extension does **not** start any automatic background
   reviewer; it only gives Pi a delegation *tool*. Recurring behavior ("review
   every implementation") must be requested in the prompt or project
   instructions.

Subagents are narrow by default: a custom agent starts with a clean system
prompt and only the context intentionally given to it (see
[[concepts/pi-subagent-child-safety-boundary]]).

### Built-in specialist agents

The extension ships eight builtin agents usable immediately:

| Agent | Use it for |
|-------|------------|
| `scout` | Fast local codebase recon: relevant files, entry points, data flow, risks. |
| `researcher` | Web/docs research with sources (requires [[entities/pi-web-access]]). |
| `planner` | A concrete implementation plan from existing context; reads and plans, does not edit. |
| `worker` | Implementation work; edits files, validates, escalates unapproved decisions. |
| `reviewer` | Code review and small fixes against the task/plan, tests, edge cases. |
| `context-builder` | A stronger setup pass that writes handoff material (`context.md`, `meta-prompt.md`). |
| `oracle` | A second opinion before acting; challenges assumptions, recommends a next move, does not edit. |
| `delegate` | A lightweight general delegate that behaves close to the parent session. |

Rule of thumb: `scout` before you understand the code, `researcher` before you
trust external facts, `planner` before a bigger change, `worker` to implement,
`reviewer` to check, and `oracle` when the decision itself feels risky. The
recommended scaffolding loop for implementation is
`clarify → planner → worker → fresh reviewers → worker`.

## Key Parameters

- Install: `pi install npm:pi-subagents`
- Tool name: `subagent` (single, parallel `tasks`, or `chain` modes)
- `oracle` and `worker` are designed for an explicit decision loop: ask
  `oracle` for diagnosis and a recommended execution prompt, then run `worker`
  only after the main agent approves that direction.

## When To Use

- A task benefits from "a second or third set of model eyes": code review,
  scouting, parallel audits, background jobs.
- You want to isolate exploratory or noisy work (large refactors, audits) so
  intermediate tool output does not bloat the parent's context window.
- You want a repeatable workflow shape (review loop, parallel reviewers) via
  [[concepts/pi-subagent-chain|chains]] or the packaged prompt shortcuts.

## Risks & Pitfalls

- Subagents do not inherit the parent's full context by default; under-specified
  tasks ("fix the error") leave the child with no idea what the error is.
- Installing the extension changes nothing automatically — delegation only
  happens when the parent decides (or is instructed) to delegate.
- Cost and latency multiply with parallel and nested runs; see
  [[concepts/pi-subagent-recursion-guard]].

## Related Concepts

- [[concepts/pi-agent-definition]]
- [[concepts/pi-subagent-chain]]
- [[concepts/pi-subagent-execution-mode]]
- [[concepts/pi-forked-context]]
- [[concepts/pi-subagent-child-safety-boundary]]
- [[concepts/hermes-subagent-delegation]] — analogous delegation mechanism in a different harness
- [[concepts/pi-extension]]

## Sources

- [pi-subagents README](raw/pi-subagents-readme.md)
</content>
</invoke>
