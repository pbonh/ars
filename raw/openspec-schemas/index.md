# openspec-schemas — repository & schema index

> Fetched extraction of https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas
> and the repository root. Retrieved 2026-05-23 via web fetch (summarized, not a
> byte-for-byte copy).

## Repository metadata

- **Repository:** `intent-driven-dev/openspec-schemas`
- **Owner / org:** intent-driven-dev (the GitHub org behind intent-driven.dev)
- **Visibility:** public
- **License:** MIT
- **Approx. popularity at fetch time:** ~37 stars, ~6 forks

## What it is

A collection of custom workflow schemas that extend the OpenSpec framework. It
demonstrates how to customize OpenSpec for different work styles and delivery
contexts. OpenSpec ships a general-purpose default `spec-driven` schema; this
repo provides specialized alternatives.

## Installation / usage (per README)

1. Copy a schema folder from `openspec/schemas/` to a project-local or
   user-level schemas directory.
2. Update `openspec/config.yaml` to activate the schema.
3. Run `openspec schema validate`.

AI agents are told to verify OpenSpec is installed (version ≥ 1.0.0) before
proceeding.

## Schemas in `openspec/schemas/`

| Schema | Purpose |
|--------|---------|
| `minimalist` | Fast path from spec to execution using user-story requirements and Gherkin acceptance criteria. |
| `event-driven` | Event Storming discovery workflow for async systems, with AsyncAPI specs. |
| `behaviour-driven` | Gherkin-style GIVEN/WHEN/THEN requirement workflow. |
| `intent-driven` | Multi-artifact workflow: proposals, specs, design, ADRs, and tasks. |
| `linearized` | Linear (issue tracker) integration while keeping OpenSpec specs as source of truth. |
| `spec-driven-with-adr` | Standard proposal-to-tasks flow plus durable Architecture Decision Records. |

## References

The repo points to intent-driven.dev and a blog post about custom schemas.
