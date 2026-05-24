# openspec-schemas / spec-driven-with-adr

> Fetched extraction of
> https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas/spec-driven-with-adr
> Retrieved 2026-05-23 via web fetch (summarized, not a byte-for-byte copy).

## Directory contents

- `README.md` — documentation for the schema.
- `schema.yaml` — the schema (artifact DAG) definition.
- `templates/` — template files for the workflow's artifacts.

## What the schema does (per README)

Implements a **`proposal → specs → design → adr → tasks`** workflow — "for
changes that need the standard proposal-to-tasks OpenSpec flow plus durable
Architecture Decision Records."

Artifacts produced, in sequence:

1. `proposal`
2. `specs`
3. `design`
4. `adr` (Architecture Decision Records)
5. `tasks`

## ADR storage & persistence

- ADR files are generated under the **target repository's top-level `adr/`
  folder**, not only inside the OpenSpec change folder. They live at the repo
  root, separate from `openspec/`.
- **Persistence rule:** "Accepted ADRs are immutable. If a future decision
  changes a prior ADR, create a new ADR that supersedes the old one and leave the
  original file unchanged."

## ADR template

The schema defers to external ADR skills: "For ADR skills please refer to:
Intent-Driven-Template Skills" — the `intent-driven-template` repository's
`.agents/skills/architectural-decision-records` folder. The specific ADR
template format is managed by those skills.
