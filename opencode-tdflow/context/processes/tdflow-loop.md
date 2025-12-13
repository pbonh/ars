# TDFlow Loop (Process)

1) Gather inputs: issue description, test command, failing tests (names, errors, sources). If no reproduction tests, call Generate Tests.
2) Explore Files: view/search repo; propose global patch diff (do not apply).
3) Revise Patch (if needed): fix context so patch applies cleanly; keep inserted code unchanged.
4) Apply patch (after user approval) and run tests (or ask user to run). Collect failing tests.
5) For each failing test: Debug One using debugger to find root cause; produce reports.
6) Feed reports + prior attempts back to Explore Files; iterate until all tests pass or max iterations.
7) Patch Selection: if no full pass, pick best patch maximizing reproduction passes without regression failures.

Controls
- Ask before edits. Avoid touching tests unless explicitly permitted.
- Prefer minimal diffs. Record attempt summaries (patch id, failing tests, key findings).
- Stop conditions: all tests pass; iteration budget exhausted; user stops.
