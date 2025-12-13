# Prompt Templates (Snippets)

## Patch Proposal (Explore Files)
- Inputs: issue, failing tests (names/errors/sources), repo paths, prior attempts summary.
- Output: unified diff (apply_patch ready), rationale, expected effect per test.
- Constraints: view/search only; do not edit; avoid tests unless approved.

## Debug Report (Debug One)
- What failed: test name + error excerpt.
- Where: file/function/line(s) implicated.
- Why: root cause analysis.
- Fix hint: minimal change suggestion (no edits).

## Reproduction Test (Generate Tests)
- Each test: single behavior, one assert, deterministic data.
- Provide path, test name, content, and command to run.

## Patch Selection
- Inputs: [{patch_id, test_passed, test_failed, regression_failures, notes}]
- Output: selected_patch_id, rationale, next steps if still failing.
