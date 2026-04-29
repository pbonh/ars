You are running the **batch** PDF textbook split workflow.

## Arguments

`$ARGUMENTS` is `<directory> [--force]`.

- The first non-flag argument is the directory containing PDFs.
- `--force` (optional) means re-process books whose `<book>/manifest.json` reports `status: "complete"`.

## What to do

1. Resolve the directory to an absolute path. If it doesn't exist or isn't a directory, abort with an error.
2. Enumerate `*.pdf` in the directory, **excluding** `*.ocr.pdf` sidecars. Use:

   ```bash
   find <abs-dir> -maxdepth 1 -type f -name '*.pdf' ! -name '*.ocr.pdf' | sort
   ```

3. For each PDF:
   - Compute `<book> = <dirname>/<stem>` (output dir alongside the PDF).
   - **Skip-if-done check:** if `--force` is absent and `<book>/manifest.json` exists with `"status": "complete"`, log "skip: already complete" and continue.
   - Otherwise, dispatch to the **`split-textbooks`** skill with the path to this PDF. The skill writes its own manifest and handles its own failures.
   - If the skill reports a failure, log it and continue to the next PDF. **Do not abort the batch.**
4. After all PDFs are processed, print a summary:
   - Number processed, number skipped, number failed.
   - For each failed book, name the `failed_step` from its manifest.

## Constraints

- Run the Step 0 environment self-check from the skill once at the start of the batch (not per book).
- Never modify the original `*.pdf` files.
- Never delete a `*.ocr.pdf` sidecar except per the skill's failure rules.
