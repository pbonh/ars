---
title: "Agent Schema Document"
type: concept
tags: [concept, knowledge-management, llm, configuration]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/llm-wiki.md"]
confidence: high
---

## Definition

An **agent schema document** is a configuration file that tells an LLM agent how a wiki is structured, what conventions to follow, and what workflows to use when ingesting sources, answering questions, or maintaining the wiki. It transforms a generic chatbot into a disciplined wiki maintainer.

## How It Works

The schema document is co-evolved by the user and the LLM over time. It typically lives at the root of the wiki directory with a recognizable name such as `CLAUDE.md` (for Claude Code), `AGENTS.md` (for OpenAI Codex), or as a loaded skill file (for agents like Pi).

The schema specifies:
- **Directory structure:** Where raw sources, summaries, concepts, entities, and syntheses live.
- **Page templates:** Required frontmatter fields, body section headings, and formatting rules.
- **Ingest workflow:** Steps to read a source, extract claims, write pages, update the index, and log changes.
- **Query workflow:** How to search the wiki, synthesize answers, and file reusable answers back.
- **Lint workflow:** What health checks to run, how often, and how to report findings.
- **Naming conventions:** Slug rules, tag vocabularies, and link syntax.
- **Tool inventory:** Which plugins and CLI tools are available (e.g., [[entities/marp]], [[entities/qmd]], [[entities/dataview]]).

When the agent starts a session, it reads the schema first. This ensures consistency across multiple sessions and different agents.

## Key Parameters

| Parameter | Typical Value |
|-----------|---------------|
| Filename | `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, or `.pi/skills/wiki/SKILL.md` |
| Scope | Entire wiki directory |
| Evolution | Incremental: user and LLM add rules as edge cases are discovered |
| Versioning | Often tracked in the same git repo as the wiki |

## When To Use

Create or extend a schema document when:
- You are starting a new LLM wiki and need to bootstrap agent behavior.
- You discover an inconsistency (e.g., pages with different frontmatter formats) and want to prevent recurrence.
- You add a new tool (e.g., [[entities/qmd]] for search) and want the agent to know it exists.
- You change directory structure or page templates and need the agent to follow the new rules.
- You share the wiki with another agent or user and need a single source of truth for conventions.

A schema may be unnecessary when:
- The wiki is tiny (< 5 pages) and exploratory.
- You are using a single agent for a one-time ingest and do not need cross-session consistency.

## Risks & Pitfalls

- **Schema rot:** The schema may fall behind actual practice. If the LLM starts writing pages that deviate from the schema, the schema should be updated rather than enforced rigidly.
- **Over-specification:** A schema that is too detailed can be brittle and hard to maintain. Start minimal and grow organically.
- **Agent lock-in:** A schema named `CLAUDE.md` may confuse a non-Claude agent. Use generic naming or maintain per-agent variants if you switch between models.
- **Secret leakage:** If the schema includes API keys or private prompts, it should not be committed to a public git repo. Keep secrets in a separate, ignored file.
- **Ignored schema:** Some agents may not reliably read the schema on every session. Embedding critical rules in a loaded skill or system prompt is more reliable than a standalone markdown file.

## Related Concepts

- [[concepts/llm-wiki-pattern]] — the pattern that relies on a schema as its governance layer
- [[concepts/skill-validation]] — analogous discipline for agent skills; a schema is essentially a domain skill
- [[entities/obsidian]] — the viewer; the schema governs what the LLM writes, not how Obsidian displays it
- [[entities/andrej-karpathy]] — describes the schema as "the key configuration file"

## Sources

- [LLM Wiki](raw/llm-wiki.md) — Andrej Karpathy's description of the schema layer
