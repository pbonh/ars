---
title: "Fluid Workflow"
type: concept
tags: [concept, workflow, agile, ai-assisted-development]
created: 2026-05-21
updated: 2026-05-21
sources: ["raw/openspec-docs"]
confidence: high
---

## Definition

A fluid workflow is a project-management style in which work is modeled as a set of discrete *actions* that can be taken in any order, rather than a linear sequence of *phases* that must be completed lock-step. Dependencies between actions are treated as *enablers*—they show what is possible next, not what is required next.

## How It Works

In a fluid workflow, artifacts (proposal, specs, design, tasks) form a directed acyclic graph. An artifact becomes *ready* when all of its dependencies exist, but nothing forces the practitioner to create it immediately. Implementation can start, then pause to revise the design, then resume—without "breaking" a phase gate.

```text
proposal ──► specs ──► design ──► tasks ──► implement
   ▲           ▲          ▲                    │
   └───────────┴──────────┴────────────────────┘
            update as you learn
```

The OpenSpec OPSX workflow embodies this by providing slash commands (`/opsx:explore`, `/opsx:propose`, `/opsx:apply`, `/opsx:archive`) that can be invoked at any time, with the agent querying the current artifact graph state before deciding what to do.

## Key Parameters

| Aspect | Phase-Locked | Fluid |
|--------|--------------|-------|
| Progression | Linear: plan → build → finish | Any order: explore, build, revise, archive |
| Going back | Awkward or officially disallowed | Natural: edit any artifact anytime |
| Dependencies | Gates: "you must do X before Y" | Enablers: "Y is possible once X exists" |
| Discovery during build | Often requires restarting the phase | Absorbed by updating the relevant artifact |

## When To Use

Use a fluid workflow when:
- Requirements are discovered during implementation
- The team wants to iterate on design while coding
- AI agents are generating artifacts and need freedom to refine
- Parallel changes require context switching without penalty

A phase-locked workflow may still be appropriate for:
- Highly regulated environments with formal sign-off gates
- Fixed-bid contracts where scope must be frozen before build
- Very small, well-understood tasks where overhead is unnecessary

## Risks & Pitfalls

- **Unbounded iteration:** Without discipline, a change can remain open indefinitely as scope creeps. The `tasks.md` checklist and `/opsx:verify` command provide guardrails.
- **Archive without review:** Fluidity can tempt teams to archive without thorough review. OpenSpec encourages `/opsx:verify` before archive.
- **Inconsistent artifact quality:** Because artifacts can be updated at any time, they may become inconsistent if multiple people edit them concurrently. Change folders are single-owner by convention.

## Related Concepts

- [[concepts/artifact-dependency-graph]] — The DAG that enables fluidity
- [[concepts/opsx-workflow]] — OpenSpec's concrete implementation
- spec-driven development — The methodology fluid workflow serves

## Sources

- OpenSpec Workflows Guide (`raw/openspec-docs/workflows.md`)
- OpenSpec OPSX Guide (`raw/openspec-docs/opsx.md`)
