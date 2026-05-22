---
title: "Pi Session Format"
type: concept
tags: [concept, pi, session, jsonl, persistence]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/pi-repo/packages/coding-agent/docs/session-format.md"]
confidence: high
---

## Definition

The Pi session format is a JSONL (JSON Lines) file format used to store conversation state. Each line is a typed entry, and entries form a tree structure via `id`/`parentId` fields, enabling in-place branching without creating new files.

## How It Works

1. Session files are stored at `~/.pi/agent/sessions/--<path>--/<timestamp>_<uuid>.jsonl`.
2. The first line is a header with version metadata.
3. Subsequent lines are entries: `HeaderEntry`, `UserEntry`, `AssistantEntry`, `ToolCallEntry`, `ToolResultEntry`, `CompactionEntry`, `BranchSummaryEntry`, `CustomEntry`, etc.
4. Entries link via `id` and `parentId`, forming a directed tree.
5. Existing sessions auto-migrate to version 3 on load.

## Key Parameters

- File extension: `.jsonl`
- Current version: 3 (renamed `hookMessage` role to `custom`)
- Content blocks: `TextContent`, `ImageContent`, `ThinkingContent`, `ToolCall`
- Branching: in-place via `parentId`; no new files created

## When To Use

Understand the session format when:
- Writing extensions that read or manipulate session state.
- Building external tools that parse or visualize conversation history.
- Implementing custom compaction or summarization logic.
- Migrating or archiving sessions programmatically.

## Risks & Pitfalls

- Parsing must use strict JSONL semantics (split on `\n` only); generic line readers may split on Unicode separators.
- Auto-migration from v1 or v2 to v3 happens on load; external parsers should handle all versions.
- Deleting sessions requires removing the `.jsonl` file directly or using the interactive `/resume` UI.

## Related Concepts

- [[concepts/pi-compaction]]
- [[concepts/pi-extension]]
- [[concepts/pi-rpc-mode]]

## Sources

- [Pi Session Format Documentation](raw/pi-repo/packages/coding-agent/docs/session-format.md)
