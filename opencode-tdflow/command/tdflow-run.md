---
name: tdflow-run
agent: tdflow-orchestrator
---

# /tdflow-run
Run the TDFlow workflow on the current repository.

## Syntax
```
/tdflow-run "<issue_description>" --test-cmd "<test_command>" --failing "<comma_or_space_sep_test_names>" [--notes "extra context"]
```

## Parameters
- `issue_description` (required): The bug/feature to address.
- `test_command` (required): Command to run tests (e.g., `pytest`, `npm test`, `go test ./...`).
- `failing` (recommended): Names or patterns of currently failing tests, if known.
- `notes` (optional): Extra constraints (e.g., language, framework, files to avoid).

## Behavior
- Orchestrator will confirm inputs, then run TDFlow stages (generate tests if missing, propose patch, ask before apply, debug failures, iterate).
- Will request permission before any edits or apply_patch.

## Example
```
/tdflow-run "fix API pagination off-by-one" --test-cmd "pytest" --failing "tests/api/test_pagination.py::test_page_bounds"
```
