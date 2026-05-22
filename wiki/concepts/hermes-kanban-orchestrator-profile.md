---
title: "Hermes Kanban Orchestrator Profile"
type: concept
tags: [concept, ai-agent, kanban, orchestrator, profile, multi-agent]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-kanban-v1-spec.pdf"]
confidence: high
---

## Definition

The Hermes Kanban Orchestrator Profile is a first-class profile template whose sole purpose is to decompose goals into tasks, route them to specialist profiles, and summarize board state—without doing implementation work itself. It is the user-space answer to the recurring problem of an "orchestrator that starts doing the work instead of cleanly routing it."

## How It Works

### Three properties of a well-behaved orchestrator

1. **Disabled execution toolsets**. The orchestrator profile ships with `toolsets: [kanban, gateway, memory]` and explicitly disables `terminal`, `file`, `web`, `browser`, and `code`. It literally cannot do implementation work; its only tools are create/link/assign tasks and read the board.
2. **Orchestrator skill with prescriptive system message**. A `kanban-orchestrator` skill whose system message is short and anti-temptation:
   - "You are a dispatcher, not a worker."
   - "For any concrete task, create a kanban task and assign it to the appropriate specialist profile. Do not attempt to execute it."
   - "Your job is to decompose, route, and summarize — not to research, write, or code."
   - "If no specialist fits, ask the user which profile to create. Do not default to doing it yourself."
3. **Standard specialist roster convention**. The skill documents a canonical starter roster (`researcher`, `writer`, `analyst`, `backend-eng`, `reviewer`, `ops`) with one-line role descriptions. Users fork and edit for their own fleets.

### Shipping implication: installable profile templates

Distribute the orchestrator and specialists as installable profile templates:

```bash
$ hermes profile install orchestrator   # the router
$ hermes profile install researcher       # specialists
$ hermes profile install writer
$ hermes profile install analyst
$ hermes profile install reviewer
$ hermes profile install ops
```

This closes the "portable profile artifact" gap identified in Google Gemini Enterprise, but without the enterprise ceremony.

### Why this is not kernel work

The dispatcher does not know or care that a profile is called "orchestrator." The board has no role field. Everything is user-space convention expressed through two existing primitives: profiles (toolset restrictions) and skills (behavioral guidance).

## Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `toolsets` | `[kanban, gateway, memory]` | Enabled toolsets |
| `disabled_toolsets` | `[terminal, file, web, browser, code]` | Explicitly blocked |
| `skills` | `[kanban-orchestrator]` | Skill providing system message |
| `roster` | `researcher, writer, analyst, backend-eng, reviewer, ops` | Starter convention |

## When To Use

- **Research triage**: Planner decomposes a question into parallel research angles.
- **Coding pipelines**: Planner breaks a feature into worktrees, routes to backend/frontend engineers, then to reviewer.
- **Fleet farming**: A single `insta-manager` profile is not an orchestrator; it is a specialist. Use an orchestrator only when multiple distinct roles must coordinate.

## Risks & Pitfalls

- **Temptation to do work**: Even with disabled toolsets, models may hallucinate execution. The prescriptive skill message plus toolset failure are the defense.
- **Profile misconfiguration**: If a user forgets to disable `terminal`, the orchestrator will silently start coding. Verify toolset lists in `hermes profile show`.
- **Roster mismatch**: The starter roster is convention, not enforcement. A user who renames `backend-eng` to `be-dev` must update the orchestrator skill or tasks will be assigned to a non-existent profile.

## Related Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-profile-isolation]]
- [[concepts/hermes-skills-system]]
- [[concepts/hermes-kanban-dispatcher]]

## Sources

- `docs/hermes-kanban-v1-spec.pdf` §6
