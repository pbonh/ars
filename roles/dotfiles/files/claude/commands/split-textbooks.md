You are running the **batch** PDF textbook split workflow.

## Arguments

`$ARGUMENTS` is `<directory> [--force] [--markdown] [--llm-cleanup]`.

- The first non-flag argument is the directory containing PDFs.
- `--force` (optional) — re-process books whose `<book>/manifest.json` reports `status: "complete"`.
- `--markdown` (optional, default off) — produce `.md` sidecars alongside each PDF slice. Without this flag, only PDF slices and the manifest are written.
- `--llm-cleanup` (optional, default off) — use the per-page LLM cleanup pass for markdown. **Implies `--markdown`** (treat `--llm-cleanup` alone as if `--markdown --llm-cleanup` were passed). Cost-significant on long books — only set when the user explicitly asked.

## What to do

1. Resolve the directory to an absolute path. If it doesn't exist or isn't a directory, abort with an error.
2. Enumerate `*.pdf` in the directory, **excluding** `*.ocr.pdf` sidecars. Use:

   ```bash
   find <abs-dir> -maxdepth 1 -type f -name '*.pdf' ! -name '*.ocr.pdf' | sort
   ```

3. For each PDF:
   - Compute `<book> = <dirname>/<stem>` (output dir alongside the PDF).
   - **Skip-if-done check:** if `--force` is absent and `<book>/manifest.json` exists with `"status": "complete"`, log "skip: already complete" and continue.
   - Otherwise, dispatch to the **`split-textbooks`** skill with the path to this PDF, plus `markdown` and `llm_cleanup` booleans derived from the command-line flags (`--llm-cleanup` implies `markdown: true`). The skill writes its own manifest and handles its own failures.
   - If the skill reports a failure, log it and continue to the next PDF. **Do not abort the batch.**
4. After all PDFs are processed, print a summary:
   - Number processed, number skipped, number failed.
   - The cleanup mode used for the run (`none` | `rules` | `llm`).
   - For each failed book, name the `failed_step` from its manifest.
   - If any book had non-empty `cleanup_fallbacks`, list them (book name + section index + reason) so the user knows which sections fell back from LLM to rules.

## Constraints

- Run the Step 0 environment self-check from the skill once at the start of the batch (not per book).
- Never modify the original `*.pdf` files.
- Never delete a `*.ocr.pdf` sidecar except per the skill's failure rules.
