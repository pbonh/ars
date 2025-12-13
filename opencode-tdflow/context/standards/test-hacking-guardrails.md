# Test Hacking Guardrails

Prohibited behaviors (fail fast):
- Modifying, skipping, or disabling tests without explicit approval.
- Weakening assertions or altering test data/fixtures to mask failures.
- Hardcoding outputs or magic constants from tests into production paths.
- Adding test-only branches, feature flags, or environment overrides to bypass logic.
- Manipulating test runners/config to narrow scope.
- Changing dependency versions solely to hide failures.

Allowed with caution (and explicit approval):
- Small test fixes when the test is incorrect (must be justified and requested).

Expectations:
- Fix root cause in production code.
- Preserve regression behavior; ensure reproducibility.
- Prefer minimal, localized changes.
