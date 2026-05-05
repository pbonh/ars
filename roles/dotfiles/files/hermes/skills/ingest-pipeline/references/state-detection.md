# State Detection Algorithm

`ingest-pipeline` classifies an input target into one of six states, then
drives it forward to S5 by dispatching to existing skills.

## States

| #   | State              | Detection                                                                                                                             | Next action                                                                              |
|-----|--------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| S0  | Empty / unrelated  | Target absent, OR directory has no `*.pdf`, no `*.md`, and no manifest                                                                | Abort with diagnostic; no partial work.                                                  |
| S1  | Single large PDF   | Target is a `.pdf` file, OR directory contains exactly one `.pdf` and zero `.md`                                                      | Run `split-textbooks` subagent → produces sliced PDFs + `manifest.json`. Reclassify (becomes S2). |
| S2  | Pre-split PDFs     | Directory contains ≥2 `.pdf` files matching `^\d{2}-[a-z0-9-]+\.pdf$`, OR a `split-textbooks` `manifest.json` with `status: complete` | Run `pdf-to-mdbook` subagent (slice-dir mode). Reclassify (becomes S4).                  |
| S3  | Pre-split markdown | Directory contains ≥2 `.md` and zero `book.toml`, OR `split-textbooks` `manifest.json` with `markdown_generated: true`                | Scaffold an mdBook directly (inline; no subagent): write `book.toml`, `src/SUMMARY.md`, copy files into `src/`. |
| S4  | Partial mdBook     | Directory contains both `book.toml` AND `src/SUMMARY.md` AND no `pipeline.json` with `status: complete`                               | Diagnose missing referenced files, fill stubs if needed, run `mdbook build`. On success → S5. |
| S5  | Complete           | `pipeline.json` exists with `status: complete` AND mdBook builds cleanly                                                              | No-op unless `--force`. Print "already complete" and stop.                               |

## Algorithm

Run on every invocation, including reruns:

1. Resolve the target to an absolute path. Identify whether it's a file or
   directory.
2. Determine `book_root` and `working_dir`:
   - If target is a file: `book_root = dirname(target)`.
   - If target is a directory: `book_root = target`.
   - If `<book_root>/pipeline.json` exists and has `working_dir` set, use that
     value for `working_dir`. Otherwise `working_dir = book_root` (initial state).
   - **All subsequent steps in this algorithm operate on `working_dir`, not
     `book_root`.** The `pipeline.json` file itself always lives at `book_root`,
     but the state being classified can be in a subdirectory.
3. If `book_root/pipeline.json` exists with `status: complete` AND `--force`
   was not passed → **return S5**.
4. Else if `working_dir/book.toml` AND `working_dir/src/SUMMARY.md` both exist →
   **return S4**.
5. Else if `working_dir/manifest.json` exists (the `split-textbooks` manifest):
   - If `markdown_generated: true` → **return S3**.
   - Else if `status: complete` → **return S2**.
   - Else if `status: in_progress` → **return S1** with a note: prior split
     run was interrupted; rerun `split-textbooks` to resume cleanly.
     Append a `notes` entry to `pipeline.json` recording this.
   - Else if `status: failed` → respect `failed_step`; resume there. Reclassify
     based on what files are actually present (fall through to step 6).
6. Else count files at the top level of `working_dir`:
   - ≥2 `.md` and 0 `.pdf` → **return S3**.
   - ≥2 `.pdf` matching `^\d{2}-[a-z0-9-]+\.pdf$` → **return S2**.
   - exactly one `.pdf` (or the original target itself was a `.pdf`) →
     **return S1**.
7. **Return S0** otherwise.

## Filesystem-truth rule

Always inspect the filesystem before trusting `pipeline.json`. If the manifest
disagrees with what's actually on disk, trust the filesystem and reclassify.
Append a `notes` entry recording the reconciliation. Never error on
disagreement.

Examples:

| `pipeline.json` says | Filesystem shows                              | Resolution                                         |
|----------------------|-----------------------------------------------|----------------------------------------------------|
| `status: complete`   | `<stem>-mdbook/` directory missing            | Reclassify (probably S2 or S4). Reset to in_progress. |
| `current_state: S2`  | `book.toml` present                           | Reclassify S4. Update `current_state` on next write. |
| `status: in_progress`, last phase `split` `complete` | Slice files all present, no mdbook dir | S2 — resume at the mdbook phase.                  |

## State transitions

The classifier re-runs after every phase, giving "drive forward to S5" semantics:

```
S1 ──split-textbooks──▶ S2 ──pdf-to-mdbook──▶ S4 ──mdbook build──▶ S5
S3 ──scaffold inline───▶ S4 ──mdbook build──▶ S5
S4 ──mdbook build──────▶ S5
S0 ──abort
```

If any phase fails, the orchestrator sets `pipeline.json` `status: failed`,
populates `failed_phase` and `error_message`, and stops. Rerun resumes by
reclassifying from the current filesystem state.
