# State Detection Algorithm

> **Implementation note.** This algorithm is the specification that
> `scripts/run_pipeline.py` implements. The LLM agent does **not** run
> the algorithm itself — it invokes the script and reads the script's
> JSON action signal. Read this file when debugging the script or
> proposing classifier changes; do not re-execute the steps by hand
> from a SKILL.md run.

`ingest-pipeline` classifies an input target into one of six states, then
drives it forward to S5 by dispatching to existing skills.

## States

| #   | State              | Detection                                                                                                                             | Next action                                                                              |
|-----|--------------------|---------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
| S0  | Empty / unrelated  | Target absent, OR directory has no `*.pdf`, no `*.md`, and no manifest                                                                | Abort with diagnostic; no partial work.                                                  |
| S1  | Single PDF         | Target is a `.pdf` file, OR directory contains exactly one `.pdf` and zero `.md`                                                      | Run `pdf-to-mdbook` subagent → produces an mdBook directory with `book.toml` and `src/SUMMARY.md`. Reclassify (becomes S4). |
| S3  | Pre-split markdown | Directory contains ≥2 `.md` and zero `book.toml`                                                                                       | Scaffold an mdBook directly (inline; no subagent): write `book.toml`, `src/SUMMARY.md`, copy files into `src/`. |
| S4  | Partial mdBook     | Directory contains both `book.toml` AND `src/SUMMARY.md` AND no `pipeline.json` with `status: complete`                               | Diagnose missing referenced files, fill stubs if needed, run `mdbook build`. On success → S5. |
| S5  | Complete           | `pipeline.json` exists with `status: complete` AND mdBook builds cleanly                                                              | No-op unless `--force`. Print "already complete" and stop.                               |

`S2` is intentionally absent — it was previously used for "pre-split PDFs"
(output of the now-removed `split-textbooks` skill). State numbers are
preserved for compatibility with on-disk `pipeline.json` files; the
filesystem-truth rule means stale `current_state: "S2"` values reclassify
deterministically on the next run.

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
5. Else count files at the top level of `working_dir`:
   - ≥2 `.md` and 0 `.pdf` → **return S3**.
   - exactly one `.pdf` (or the original target itself was a `.pdf`) →
     **return S1**.
6. **Return S0** otherwise.

If a directory contains multiple unrelated `.pdf` files (i.e., several
distinct books), this orchestrator does not split them apart — point the
user at `ingest-pipeline-batch` for library sweeps, or have them merge with
`pdfunite` first if the PDFs are chapters of one book.

## Filesystem-truth rule

Always inspect the filesystem before trusting `pipeline.json`. If the manifest
disagrees with what's actually on disk, trust the filesystem and reclassify.
Append a `notes` entry recording the reconciliation. Never error on
disagreement.

Examples:

| `pipeline.json` says | Filesystem shows                              | Resolution                                         |
|----------------------|-----------------------------------------------|----------------------------------------------------|
| `status: complete`   | `<stem>-mdbook/` directory missing            | Reclassify (probably S1 or S4). Reset to in_progress. |
| `current_state: S2`  | any contents                                  | S2 is no longer a live state. Reclassify per the algorithm above; record the reconciliation in `notes`. |
| `status: in_progress`, last phase `mdbook` `complete` | mdbook dir present, build not yet run | S4 — resume at the build phase.                   |

## State transitions

The classifier re-runs after every phase, giving "drive forward to S5" semantics:

```
S1 ──pdf-to-mdbook──▶ S4 ──mdbook build──▶ S5
S3 ──scaffold inline─▶ S4 ──mdbook build──▶ S5
S4 ──mdbook build───▶ S5
S0 ──abort
```

If any phase fails, the orchestrator sets `pipeline.json` `status: failed`,
populates `failed_phase` and `error_message`, and stops. Rerun resumes by
reclassifying from the current filesystem state.
