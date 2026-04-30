You are running the **single-book retry** of the PDF textbook split workflow.

## Arguments

`$ARGUMENTS` is `<path-to-pdf> [--markdown] [--llm-cleanup]`.

- The first non-flag argument is the path to one PDF.
- `--markdown` (optional, default off) — produce `.md` sidecars alongside each PDF slice.
- `--llm-cleanup` (optional, default off) — per-page LLM cleanup. **Implies `--markdown`.**

The user opted in to overwrite by invoking the retry, so do **not** prompt before deleting prior output.

## What to do

1. Resolve the path to an absolute path. If it doesn't exist or isn't a file ending in `.pdf` (and is not a `*.ocr.pdf` sidecar), abort with an error.
2. Compute `<book> = <dirname>/<stem>`. Inspect any existing `<book>/manifest.json`:
   - If `status: "failed"` and the user has manually edited `page_offset`, **preserve that offset** for the recipe (the skill respects manifest overrides per its "Manual override path" section).
   - Otherwise, delete the entire `<book>/` directory and the `<dirname>/<stem>.ocr.pdf` sidecar (if present) before running.
3. Run the Step 0 environment self-check from the **`split-textbooks`** skill.
4. Dispatch to the `split-textbooks` skill on this single PDF, with `markdown` and `llm_cleanup` booleans derived from the flags (`--llm-cleanup` implies `markdown: true`).
5. Print the resulting manifest's `status`, `markdown_generated`, and `cleanup_method`. If `status: "failed"`, also print `failed_step` and `error_message`. If `cleanup_fallbacks` is non-empty, list them.

## Constraints

- Single-book scope only: never iterate over a directory.
- The override-preserving branch (step 2) is the one path that does NOT wipe prior state. Everything else is a fresh run.
