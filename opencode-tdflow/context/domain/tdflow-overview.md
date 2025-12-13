# TDFlow Overview

- Purpose: repository-scale TDD workflow that iterates propose → apply → test → debug until all tests pass.
- Subagents: Explore Files (propose patch), Revise Patch (fix patch context), Debug One (per failing test), Generate Tests (optional reproduction tests), Patch Selection (choose best candidate when no full pass).
- Inputs: issue description, failing tests (names, errors, sources), repo structure, prior attempt history.
- Outputs: repository patch that passes all tests without test hacking.
- Principles:
  - Force decomposition: keep subagent scopes narrow to reduce context burden.
  - Minimal context per call; carry history summary not full logs.
  - Guardrails against test hacking: never disable/skip tests, never edit tests without approval, avoid hardcoded outputs or test-only code paths.
  - Iterative: incorporate debug reports to refine patches; stop when all tests pass or budget reached.
- Success: all reproduction + regression tests pass; no test hacking patterns present.
