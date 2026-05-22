---
title: "Hermes Kanban v1 Design Specification"
type: summary
tags: [summary, ai-agent, kanban, multi-agent, coordination, sqlite, nous-research]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/hermes-kanban-v1-spec.pdf"]
confidence: high
---

## Overview

The *Hermes Kanban v1 design spec* is the architectural blueprint for durable multi-agent coordination inside [[entities/hermes-agent]]. Written by Nous Research and dated April 2026, it defines a minimal-footprint kernel—one SQLite file, one CLI subcommand, one skill, one cron job—upon which arbitrary collaboration shapes can be expressed through profiles, skills, and plugins. The spec is explicit about what belongs in the kernel versus what belongs in user-space, and it draws lessons from four contemporary systems: Cline Kanban, Paperclip, NanoClaw, and Google Gemini Enterprise.

The design thesis is a synthesis: adopt Cline’s board + links + ephemeral workspaces shape; adopt Paperclip’s atomic claim and persistent agent identity (mapped onto Hermes profiles); reject NanoClaw’s fragile in-process subagent swarms; and borrow Google’s portable profile artifacts and @mention delegation syntax. The result is a three-plane architecture (control / state / execution) where every coordinating worker is a full OS process, and all coordination flows through the SQLite board.

The spec covers the full data model (four tables, three indexes), six task statuses with single-owner transitions, three workspace kinds (`scratch`, `dir:<path>`, `worktree`), eight collaboration patterns (P1–P8), an orchestrator profile template, a single-column tenant primitive for multi-tenant fleets, a worked example of 50-account fleet farming, four end-to-end user stories, and a twelve-dimension comparison against the existing `delegate_task` primitive.

## Key Claims

- The kernel stays small on purpose: governance, budgets, smart routing, and dashboards are user-space concerns, not schema primitives. [[concepts/hermes-kanban-board]]
- Every worker is a full OS process with its own `HERMES_HOME`; there are no in-process subagent swarms. [[concepts/hermes-subagent-delegation]]
- The dispatcher is deliberately dumb: recompute ready, atomic claim via SQLite CAS, spawn worker, stale-claim recovery. [[concepts/hermes-kanban-dispatcher]]
- An orchestrator profile template (disabled execution toolsets + prescriptive skill) prevents the router from doing work itself. [[concepts/hermes-kanban-orchestrator-profile]]
- A single nullable `tenant` column plus filesystem convention gives per-client data isolation without duplicating profiles. [[concepts/hermes-kanban-tenant]]
- `delegate_task` and Kanban are not competitors but complements: the former is a function call, the latter is a durable work queue. [[concepts/hermes-kanban-board]]

## Source Metadata

| Field | Value |
|-------|-------|
| Type | PDF design specification |
| Owner | Nous Research |
| URL | https://github.com/NousResearch/hermes-agent/blob/main/docs/hermes-kanban-v1-spec.pdf |
| License | Repository license (see GitHub) |
| Ingested on | 2026-05-21 |

## Relevant Concepts

- [[concepts/hermes-kanban-board]]
- [[concepts/hermes-kanban-dispatcher]]
- [[concepts/hermes-kanban-orchestrator-profile]]
- [[concepts/hermes-kanban-tenant]]
- [[concepts/hermes-subagent-delegation]]
- [[concepts/hermes-cron-scheduler]]
- [[concepts/hermes-profile-isolation]]
- [[concepts/hermes-skills-system]]
