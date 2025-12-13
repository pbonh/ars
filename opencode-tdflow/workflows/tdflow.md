# Workflow: tdflow-main

## Stages
1) Intake
   - Confirm issue description, test command, failing tests provided.
   - If failing tests missing: route to @generate-tests (request approval to add).
2) Explore
   - Route to @explore-files with issue, failing tests, repo map, prior attempts summary.
   - Receive patch_diff + rationale.
3) Revise (conditional)
   - If patch cannot apply, route to @revise-patch with error and patch.
4) Apply & Test
   - Ask user for permission to apply patch. After approval, apply patch and run tests (or ask user to run if tools disallow). Collect failing tests list/output.
5) Debug
   - For each failing test, route to @debug-one with test source + error to produce reports.
6) Iterate
   - Summarize attempt (patch id, failing tests, debug notes). Loop back to Explore with history until all tests pass or iteration budget hit.
7) Patch Selection (fallback)
   - If no passing patch after budget, send attempts to @patch-selection. Present best candidate and remaining gaps.

## Context Dependencies
- domain/tdflow-overview.md
- processes/tdflow-loop.md
- standards/test-hacking-guardrails.md
- standards/quality-criteria.md
- templates/prompt-templates.md

## Success Criteria
- All reproduction and regression tests pass.
- No test hacking behaviors.
- Minimal, well-rationalized diff with user-approved edits.
