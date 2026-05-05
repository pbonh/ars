---
name: ingest-pipeline-batch
description: Sweep a library directory and run ingest-pipeline on every book root that is not already complete. Use when the user asks to "process all books in <dir>", "ingest the library", or "batch convert PDFs to mdBooks".
compatibility: Same as ingest-pipeline (poppler, qpdf, ocrmypdf, mdbook, jq) — invokes ingest-pipeline as a Hermes subagent per book.
---

# Ingest Pipeline — Batch

Walk a library root, identify each book directory, and run `ingest-pipeline`
on the ones that are not already complete. Idempotent across the whole
library: complete books are skipped; failed books retry; in-progress books
resume.

Sequential by default. `--parallel N` opt-in for users who want concurrency
and have the token budget for it.

## Inputs

- **Absolute path** to a library root directory.
- `--force` (optional) — Reprocess every book, even ones marked complete.
- `--parallel <N>` (optional) — Up to N concurrent `ingest-pipeline`
  subagents. Default: `1`.
- `--vision <mode>` (optional) — Forwarded to each per-book `ingest-pipeline`
  invocation; default `auto`.

## Step 0 — Environment self-check

Run:

```bash
command -v pdfinfo pdftotext qpdf ocrmypdf mdbook jq
```

If any are missing, print install hints (same as `ingest-pipeline`) and
abort. The per-book engine will check again, but failing fast at the batch
level avoids spawning N subagents that all immediately abort.

## Step 1 — Load or create `library.json`

Path: `<library_root>/library.json`.

- If exists, load. Use it as the prior-run cache.
- If missing, initialize:
  ```json
  {
    "schema_version": 1,
    "library_root": "<abs path>",
    "last_swept_at": null,
    "books": []
  }
  ```

## Step 2 — Walk the library tree, identify book roots

For every immediate subdirectory of `<library_root>`:

A directory is a "book root" if **any** of the following are true:
- It contains exactly one `.pdf` file at its top level.
- It contains a `pipeline.json` file (already managed).
- It contains a `manifest.json` from `split-textbooks` (mid-process).
- It contains both `book.toml` and `src/SUMMARY.md` (mid-process or done).

Skip directories that match none of the above (likely user-managed
non-book content).

Build the working set: an array of `{ root, abs_path }` entries.

## Step 3 — Filter complete books

For each candidate book root, read `<root>/pipeline.json` if present:
- If `status: "complete"` AND `--force` not passed → drop from working set
  (will be reflected as `complete` in `library.json`).
- Otherwise → keep in working set.

Books with `status: "failed"` are retained — failure was logged, the user
inspected, the rerun is the explicit "try again" signal.

## Step 4 — Dispatch per-book engine

Default sequential (`--parallel 1`):

For each book in the working set, in lexicographic order by root name:

1. Append a stub entry to `library.json` `books`: `{ root, status: "in_progress", pipeline_json: "<root>/pipeline.json" }`.
2. Write `library.json` (so observers see progress).
3. Invoke the `ingest-pipeline` skill via **subagent delegation** with:
   - Restricted toolset: `terminal`, `file`, `image`.
   - Argument: `<abs_path>`.
   - Flags: `--vision <mode>`. If `--force` was passed at the batch level,
     also pass `--force`.
4. When the subagent returns, read `<root>/pipeline.json`:
   - `status: "complete"` → update `library.json` book entry to
     `status: "complete"`.
   - `status: "failed"` → update to
     `status: "failed", failed_phase: <from per-book>`. Continue with
     the next book.
   - any other state → update to `status: "in_progress"` (likely a
     subagent crash mid-phase). Continue.

`--parallel N > 1`:

- Spawn up to N subagents concurrently, drawing from the working set as a
  queue. Cap concurrency at N.
- Use a small write-coalescing window for `library.json` updates: when
  multiple subagents finish at once, batch the writes. Write at least every
  5 seconds and on every state transition.

## Step 5 — Finalize `library.json`

Set `last_swept_at: now`. Sort `books` lexicographically by `root` for
deterministic output. Write the file.

Print a summary:

```
ingest-pipeline-batch: swept <library_root>
- Total books: <N>
- Complete: <X>
- Failed: <Y> (see <library_root>/library.json for details)
- Skipped (already complete): <Z>

Failed books:
- <root>: <failed_phase> — <error_message>
- ...
```

## Failure handling

Batch-level errors **never abort the whole sweep**. Per-book failures are
isolated: one failed book gets its `library.json` entry marked `failed`, and
the next book proceeds.

| Failure | Where | Behavior |
|---------|-------|----------|
| Required tool missing | Step 0 | Print install hints; abort. No `library.json` written if it didn't exist. |
| `library_root` does not exist or is not a directory | Step 1 | Abort with diagnostic. |
| No book roots found (Step 2 returns empty) | Step 2 | Print "no books found in <library_root>" and exit 0 (not an error — just nothing to do). |
| `ingest-pipeline` subagent fails for a book | Step 4 | Mark that book `status: "failed"` in `library.json`. Continue to next book. |
| Subagent invocation infrastructure failure | Step 4 | Mark book `status: "failed"`, `error_message: "subagent invocation failed: <details>"`. Continue. |
| User Ctrl-C | Anywhere | Books marked `in_progress` in `library.json` will be reconciled by the per-book engine on next sweep (filesystem-truth rule). |

## Hooks (optional)

If event hooks are configured:
- `pre_book`: `{ root, abs_path }` before each `ingest-pipeline` invocation.
- `post_book`: `{ root, abs_path, status, duration_ms }` after each.
- `pre_sweep` / `post_sweep`: at the start and end of the whole batch.

## Notes

- The batch wrapper does **not** know how to ingest individual books — it
  only dispatches. All real work happens inside `ingest-pipeline`.
- `library.json` is a *summary* — it is regenerated each sweep from per-book
  `pipeline.json` files. Do not rely on it as a primary store.
- For very large libraries (50+ books), default `--parallel 1` may be slow
  but predictable. Bump cautiously: vision-heavy scanned books burn tokens
  fast.
