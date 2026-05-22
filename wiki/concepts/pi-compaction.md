---
title: "Pi Compaction"
type: concept
tags: [concept, pi, context-window, summarization, llm]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/compaction.md"]
confidence: high
---

## Definition

Pi compaction is a context-window management mechanism that summarizes older conversation entries when token usage approaches the LLM's limit. It preserves recent messages and maintains cumulative tracking of file operations across summaries.

## How It Works

1. **Auto-trigger**: When `contextTokens > contextWindow - reserveTokens` (default `reserveTokens` = 16384).
2. **Find cut point**: Walk backward from the newest message, accumulating token estimates until `keepRecentTokens` (default 20k) is reached.
3. **Extract messages**: Collect messages from the previous kept boundary (or session start) up to the cut point.
4. **Generate summary**: Call the LLM to produce a structured summary, passing the previous summary as iterative context when present.
5. **Append entry**: Save a `CompactionEntry` with the summary and `firstKeptEntryId`.
6. **Reload**: The session reloads, using the summary plus messages from `firstKeptEntryId` onward.

Branch summarization uses the same mechanism when switching branches via `/tree` navigation.

## Key Parameters

- `reserveTokens`: configurable in `settings.json` (default 16384)
- `keepRecentTokens`: configurable in `settings.json` (default 20000)
- Manual trigger: `/compact [instructions]`
- Branch trigger: `/tree` navigation

## When To Use

Compaction is automatic, but you can force it with `/compact` when:
- You want to refocus the summary on a specific aspect of the conversation.
- You need to free up context before a large upcoming request.
- You are switching conversation branches and want to preserve context compactly.

## Risks & Pitfalls

- Summaries may lose nuance; important details from earlier messages can be compressed away.
- File operations are tracked cumulatively, but non-file context may still drop.
- Manual compaction with instructions can bias the summary if the instructions are too specific.
- Very short context windows may compact aggressively, leading to frequent reloads.

## Related Concepts

- [[concepts/pi-session-format]]
- [[concepts/pi-extension]]

## Sources

- [Pi Compaction Documentation](raw/pi-repo/packages/coding-agent/docs/compaction.md)
