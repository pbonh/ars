---
title: "Artifact Dependency Graph"
type: concept
tags: [concept, workflow, dag, project-management]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

An artifact dependency graph is a directed acyclic graph (DAG) in which nodes represent project artifacts (documents such as `proposal.md`, `spec.md`, `design.md`, `tasks.md`) and edges represent creation dependencies—artifact B requires artifact A to exist before B can be generated meaningfully.

## How It Works

A schema declares artifacts and their `requires` lists. The OpenSpec engine performs a topological sort to determine creation order and detects the current state of each artifact by checking filesystem existence.

```yaml
# openspec/schemas/spec-driven/schema.yaml
artifacts:
  - id: proposal
    generates: proposal.md
    requires: []
  - id: specs
    generates: specs/**/*.md
    requires: [proposal]
  - id: design
    generates: design.md
    requires: [proposal]
  - id: tasks
    generates: tasks.md
    requires: [specs, design]
```

**State transitions:**

```
BLOCKED ──────────────────► READY ──────────────────► DONE
   │                         │                       │
Missing dependencies      All dependencies        File exists
                         are DONE               on filesystem
```

When a user runs `/opsx:continue`, the agent queries `openspec status --json` to see which artifacts are `ready`, reads their dependencies for context, creates one artifact, and reports what newly becomes unlocked.

## Key Parameters

| Field | Purpose |
|-------|---------|
| `id` | Unique artifact identifier used in rules and commands |
| `generates` | Output path or glob pattern |
| `requires` | List of artifact IDs that must exist first |
| `template` | Markdown template injected into the AI prompt |
| `instruction` | Extra AI guidance for this artifact |

## When To Use

Use an artifact dependency graph when:
- AI agents need to know what to create next without human micromanagement
- Workflows have natural information-flow dependencies (design needs proposal context)
- Teams want to customize which artifacts exist and in what order
- Incremental artifact creation is preferred over all-at-once generation

Avoid when:
- The workflow is genuinely linear with no branching (a simple list suffices)
- All artifacts are always created together (graph overhead is unnecessary)

## Risks & Pitfalls

- **Circular dependencies:** The schema validator rejects cycles, but a poorly designed custom schema can create them.
- **Overly granular graphs:** Too many artifacts with tight dependencies can make the workflow feel bureaucratic. Most teams only need 3–5 artifact types.
- **Filesystem as source of truth:** Because state is inferred from file existence, manually deleting an artifact file can break the graph without warning.

## Related Concepts

- [[concepts/fluid-workflow]] — The philosophy the DAG enables
- [[concepts/custom-workflow-schema]] — How teams define their own graphs
- [[concepts/opsx-workflow]] — The concrete engine that interprets the graph

## Sources

- OpenSpec OPSX Guide (`raw/openspec-docs/opsx.md`)
- OpenSpec Customization Guide (`raw/openspec-docs/customization.md`)
