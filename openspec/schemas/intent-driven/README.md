# intent-driven schema

OpenSpec schema bundled by the scientia v0.1.0 install.

Each change in `openspec/changes/<tenant>-<change-id>/` produces, in
order:

1. `proposal.md` — the *why*. Gated by `scientia-grill`.
2. `specs/<capability>/spec.md` — Gherkin scenarios (the executable
   specification). One file per capability.
3. `design.md` — implementation approach; reads the in-force ADR
   supersession graph and surfaces open questions.
4. `adr/NNNN-<kebab-title>.md` — immutable architectural decisions.
   To change an accepted decision, write a new ADR that supersedes the
   prior one and leave the predecessor's body frozen.
5. `tasks.md` — checkbox list the `apply` stage ticks off.

After `tasks.md` is complete and verified, run `scientia-kanban-emit` to
turn the Gherkin scenarios into durable kanban tasks. After all tasks
are `done`, run the ingest skills to archive.

This README is informational. The canonical schema is in `schema.yaml`.
