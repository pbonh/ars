# `pipeline.json` Schema

`pipeline.json` is the orchestrator's manifest, written at the book root by
`ingest-pipeline`. It is layered on top of (never replaces) the per-skill
manifests written by `split-textbooks` and `pdf-to-mdbook`.

## Schema (schema_version: 1)

```json
{
  "schema_version": 1,
  "skill": "ingest-pipeline",
  "book_root": "/abs/path/to/book-root",
  "input_target": "/abs/path/to/book.pdf",
  "initial_state": "S1",
  "current_state": "S5",
  "status": "complete",
  "started_at": "2026-05-04T10:00:00Z",
  "updated_at": "2026-05-04T10:47:33Z",
  "phases": [
    {
      "name": "split",
      "skill": "split-textbooks",
      "status": "complete",
      "manifest": "manifest.json",
      "started_at": "2026-05-04T10:00:00Z",
      "completed_at": "2026-05-04T10:18:02Z",
      "subagent_invocation_id": "sa-7f3a"
    },
    {
      "name": "mdbook",
      "skill": "pdf-to-mdbook",
      "status": "complete",
      "manifest": "calculus-mdbook/manifest.json",
      "started_at": "2026-05-04T10:18:05Z",
      "completed_at": "2026-05-04T10:47:30Z",
      "subagent_invocation_id": "sa-9c12"
    },
    {
      "name": "build",
      "skill": null,
      "status": "complete",
      "started_at": "2026-05-04T10:47:30Z",
      "completed_at": "2026-05-04T10:47:33Z"
    }
  ],
  "failed_phase": null,
  "error_message": null,
  "notes": []
}
```

## Field semantics

| Field | Type | Meaning |
|-------|------|---------|
| `schema_version` | int | Always `1` for this recipe. |
| `skill` | string | Always `"ingest-pipeline"`. |
| `book_root` | string (abs path) | Directory holding the book; never moves on rerun. |
| `input_target` | string (abs path) | What the user invoked the engine with. May be a file (single PDF) or `book_root` itself. |
| `initial_state` | enum `S0`–`S5` | State on first invocation; **never overwritten** on rerun. |
| `current_state` | enum `S0`–`S5` | State on most recent invocation. Updated each run. |
| `status` | enum `pending` \| `in_progress` \| `complete` \| `failed` | The marker `--force`-less reruns check. |
| `started_at` / `updated_at` | ISO 8601 UTC | Clock from the host. |
| `phases` | array | **Append-only** log of work done. Reruns append; do not overwrite prior entries. |
| `phases[].name` | enum `split` \| `mdbook` \| `scaffold` \| `build` | Which logical phase this entry represents. |
| `phases[].skill` | string \| `null` | Name of the sub-skill invoked, or `null` for in-orchestrator inline work. |
| `phases[].status` | enum `pending` \| `in_progress` \| `complete` \| `failed` | Phase-local status. |
| `phases[].manifest` | string (relative path) | Path to the sub-skill's `manifest.json` (relative to `book_root`). |
| `phases[].subagent_invocation_id` | string | Opaque ID returned by Hermes' subagent delegation. Retained for log retracing. |
| `failed_phase` | enum \| `null` | When `status: failed`, which phase tipped over. |
| `error_message` | string \| `null` | Free-form error from the failed phase. |
| `notes` | array of strings | Free-form reconciliations (e.g., `"filesystem reclassified to S2 from S5; user deleted mdbook dir"`). |

## Crash safety

Before invoking each subagent: write `pipeline.json` with `status: in_progress` and the new phase as `pending`. After the subagent returns: update the phase entry to `complete` or `failed`. If the run is interrupted mid-phase, the next run reads partial `pipeline.json`, reconciles with filesystem state, and resumes.

## Filesystem-truth rule

If `pipeline.json` claims `status: complete` but the corresponding output
directory (`<stem>-mdbook/` or referenced files) is missing, **trust the
filesystem**. Reclassify state via the algorithm in `state-detection.md`,
append a `notes` entry recording the reconciliation, and reset `status` to
`in_progress`. Do not error.

## `library.json` schema (batch)

Single file at the library root, written by `ingest-pipeline-batch`.

```json
{
  "schema_version": 1,
  "library_root": "/abs/path/to/library",
  "last_swept_at": "2026-05-04T10:47:33Z",
  "books": [
    { "root": "calculus", "status": "complete", "pipeline_json": "calculus/pipeline.json" },
    { "root": "probability", "status": "in_progress", "pipeline_json": "probability/pipeline.json" },
    { "root": "discrete-math", "status": "failed", "failed_phase": "split", "pipeline_json": "discrete-math/pipeline.json" }
  ]
}
```
