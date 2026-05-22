---
title: "Progressive Disclosure (Agent Skills)"
type: concept
tags: [concept, agent-skills, context-window, loading, optimization]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/agentskills-io-home.md"]
confidence: high
---

## Definition

Progressive disclosure is the three-stage loading mechanism by which Agent Skills-compatible agents consume skills. Instead of loading the full content of every available skill into the context window permanently, agents keep only lightweight metadata in memory and fetch full instructions on demand.

## How It Works

1. **Discovery**: At startup, the agent scans configured skill directories and loads only the `name` and `description` of each skill. This gives the agent a catalog of available capabilities with minimal context cost.

2. **Activation**: When a user task matches a skill's description, the agent reads the full `SKILL.md` file (and any referenced resources) into the active context window. The matching is typically done by comparing the task description against skill metadata.

3. **Execution**: The agent follows the loaded instructions, optionally executing bundled scripts or loading additional referenced files as needed. After the task completes, the full skill instructions may be dropped from context, leaving only the catalog metadata.

## Key Parameters

- **Permanent context**: Only skill names and descriptions (a few lines per skill).
- **On-demand context**: Full `SKILL.md` plus any scripts, references, or assets required for the specific task.
- **Matching heuristic**: Typically natural-language similarity between the user request and the skill `description`.
- **Context footprint**: Enables agents to carry dozens or hundreds of skills without exhausting the context window.

## When To Use

Progressive disclosure is built into the Agent Skills standard, so agents that implement the standard use it automatically. As a skill author, you rely on it when:
- You want to ship a large skill library without worrying about context bloat.
- You write skills with long, detailed instructions that would be expensive to keep permanently in context.

## Risks & Pitfalls

- If a skill `description` is vague or too generic, the agent may fail to activate the skill when needed.
- If a skill `description` is overly broad, the agent may activate it for unrelated tasks, wasting tokens and producing irrelevant behavior.
- Skills that depend on external state (e.g., files in `assets/`) must ensure those resources are reachable at execution time, because they are not loaded during discovery.

## Related Concepts

- [[concepts/agent-skills-format]] — the folder and file structure that progressive disclosure operates on
- [[concepts/pi-skill]] — Pi's skill discovery paths and `/skill:name` invocation mechanism
- [[concepts/hermes-skills-system]] — Hermes Agent's skill catalog and on-demand loading

## Sources

- [agentskills.io home page](raw/agentskills-io-home.md)
