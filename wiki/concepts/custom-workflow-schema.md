---
title: "Custom Workflow Schema"
type: concept
tags: [concept, workflow, customization, schema]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

A custom workflow schema is a user-defined YAML configuration that declares the artifact types, their dependencies, and their AI-generation templates for an OpenSpec project. Schemas enable teams to adapt the default `spec-driven` workflow (proposal → specs → design → tasks) to their own processes.

## How It Works

Schemas live in `openspec/schemas/<name>/` (project-local, version-controlled) or `~/.local/share/openspec/schemas/<name>/` (user-global). Each schema contains:

```text
openspec/schemas/my-workflow/
├── schema.yaml           # Artifact DAG definition
└── templates/
    ├── proposal.md       # Template per artifact
    ├── specs.md
    ├── design.md
    └── tasks.md
```

Example `schema.yaml`:

```yaml
name: research-first
artifacts:
  - id: research
    generates: research.md
    requires: []
  - id: proposal
    generates: proposal.md
    requires: [research]
  - id: tasks
    generates: tasks.md
    requires: [proposal]

apply:
  requires: [tasks]
  tracks: tasks.md
```

Templates are markdown files with HTML-comment guidance that the OpenSpec engine injects into AI prompts when creating that artifact.

**Schema resolution precedence:**
1. CLI flag: `--schema <name>`
2. Change metadata: `.openspec.yaml`
3. Project config: `openspec/config.yaml`
4. Default: `spec-driven`

## Key Parameters

| Field | Purpose |
|-------|---------|
| `id` | Artifact identifier used in rules and dependency lists |
| `generates` | Output filename or glob |
| `requires` | Dependency list (empty for root artifacts) |
| `template` | Filename in `templates/` directory |
| `instruction` | Inline AI guidance appended to the template |

## When To Use

Create a custom schema when:
- Your team needs an artifact not in the default set (e.g., a security-review checklist or architecture-decision record)
- Your workflow order differs from the default (e.g., research before proposal)
- You want to skip artifacts entirely (e.g., proposal → tasks, skipping specs and design for experimental spikes)
- You want to standardize template content across multiple projects (fork and share)

Avoid when:
- The default `spec-driven` workflow already matches your process
- The team is new to OpenSpec (learn the default first, then customize)

## Risks & Pitfalls

- **Template bloat:** Overly long templates increase token usage and may degrade AI output quality. Keep templates concise and focused on structure, not content.
- **Circular dependencies:** `openspec schema validate` catches cycles, but they can still be introduced by hand-editing `schema.yaml`.
- **Schema drift across projects:** User-global schemas are convenient but not version-controlled with the repo. Project-local schemas are recommended for reproducibility.
- **Community schema maintenance:** Community schemas (e.g., `superpowers-bridge`) live in separate repositories with independent release cadence. Vetting and pinning versions is the user's responsibility.

## Related Concepts

- [[concepts/artifact-dependency-graph]] — The DAG a schema defines
- [[concepts/opsx-workflow]] — The engine that consumes schemas
- [[concepts/fluid-workflow]] — Custom schemas are how teams encode their own fluidity

## Sources

- OpenSpec Customization Guide (`raw/openspec-docs/customization.md`)
- OpenSpec CLI Reference (`raw/openspec-docs/cli.md`)
