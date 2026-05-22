---
title: "OPSX Workflow"
type: concept
tags: [concept, workflow, ai-assisted-development, openspec]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

OPSX (OpenSpec eXtended workflow) is the modern, schema-driven workflow system for OpenSpec. It replaces the legacy phase-locked workflow with a fluid, action-based model in which AI agents and humans create, revise, and archive change artifacts incrementally or all-at-once via slash commands.

## How It Works

OPSX is surfaced through slash commands recognized by AI coding assistants. The default `core` profile provides a fast path:

```text
/opsx:propose ──► /opsx:apply ──► /opsx:sync ──► /opsx:archive
```

An expanded profile adds granular control:

```text
/opsx:new ──► /opsx:continue or /opsx:ff ──► /opsx:apply ──► /opsx:verify ──► /opsx:archive
```

Key commands:

| Command | Purpose |
|---------|---------|
| `/opsx:propose` | Create a change and all planning artifacts in one step |
| `/opsx:explore` | Investigate the codebase and think through ideas before committing to a change |
| `/opsx:new` | Scaffold a change folder without creating artifacts |
| `/opsx:continue` | Create the next ready artifact based on the dependency graph |
| `/opsx:ff` | Fast-forward: create all ready artifacts at once |
| `/opsx:apply` | Implement tasks, checking them off as completed |
| `/opsx:verify` | Validate implementation against specs across completeness, correctness, and coherence |
| `/opsx:sync` | Merge delta specs into main specs without archiving |
| `/opsx:archive` | Finalize a change: merge deltas, move folder to `changes/archive/` |
| `/opsx:bulk-archive` | Archive multiple completed changes, resolving spec conflicts |

Under the hood, OPSX queries the OpenSpec CLI for structured status (`openspec status --json`) and rich instructions (`openspec instructions --json`) so the AI agent knows what exists, what is ready, and what template to follow.

## Key Parameters

| Parameter | Options |
|-----------|---------|
| Profile | `core` (default quick path) or `custom` (expanded workflow selection) |
| Delivery | `skills`, `commands`, or `both` (how agent integration files are installed) |
| Schema | `spec-driven` (default) or any custom schema |

## When To Use

Use OPSX when:
- You want AI agents to participate in structured planning and implementation
- Your team works on an existing codebase and needs delta-based specs
- You want customizable workflows without rebuilding tooling
- You use Claude Code, Cursor, Windsurf, GitHub Copilot, or another supported assistant

The legacy `/openspec:*` commands still work for backward compatibility, but OPSX is recommended for all new work.

## Risks & Pitfalls

- **Beta workspace commands:** Cross-repo `openspec workspace *` commands are explicitly marked beta and should not be used for production automation.
- **Profile confusion:** Switching between `core` and `custom` profiles changes which slash commands are available. Run `openspec update` after changing profiles.
- **Tool-specific syntax:** Different AI tools use slightly different command syntax (e.g., `/opsx:propose` vs `/opsx-propose` vs `/skill:openspec-propose`). The semantics are the same, but muscle memory may suffer.

## Related Concepts

- [[concepts/fluid-workflow]] — The philosophy behind OPSX
- [[concepts/artifact-dependency-graph]] — The engine that drives OPSX commands
- [[concepts/custom-workflow-schema]] — How to change the artifact set OPSX uses
- [[concepts/delta-spec]] — The format OPSX manipulates

## Sources

- OpenSpec OPSX Guide (`raw/openspec-docs/opsx.md`)
- OpenSpec Commands Reference (`raw/openspec-docs/commands.md`)
- OpenSpec Workflows Guide (`raw/openspec-docs/workflows.md`)
