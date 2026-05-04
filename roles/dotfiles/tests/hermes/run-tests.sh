#!/usr/bin/env bash
# Test harness for the ingest-pipeline Hermes skill.
#
# By default: runs cheap fixture-validity checks (no Hermes invocation).
# With HERMES_TEST=1 in env: also invokes `hermes` to drive each fixture and
# asserts on the resulting pipeline.json.
#
# Exit 0 on all-pass; non-zero on first failure.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX="$SCRIPT_DIR/fixtures"

PASS=0
FAIL=0

pass() { printf '\033[0;32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
fail() { printf '\033[0;31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

require_tools() {
  for tool in jq pdfinfo; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "run-tests: missing required tool: $tool" >&2
      exit 2
    fi
  done
}

# ── Fixture-validity checks (always run) ──────────────────────────────────

check_pdf_valid() {
  local label="$1" path="$2"
  if pdfinfo "$path" >/dev/null 2>&1; then
    pass "PDF valid: $label"
  else
    fail "PDF invalid: $label ($path)"
  fi
}

check_pdf_corrupt() {
  local label="$1" path="$2"
  if pdfinfo "$path" >/dev/null 2>&1; then
    fail "PDF should be corrupt but parses cleanly: $label"
  else
    pass "PDF is intentionally corrupt: $label"
  fi
}

check_json_valid() {
  local label="$1" path="$2"
  if jq empty "$path" >/dev/null 2>&1; then
    pass "JSON valid: $label"
  else
    fail "JSON invalid: $label ($path)"
  fi
}

check_file_exists() {
  local label="$1" path="$2"
  if [ -e "$path" ]; then
    pass "File exists: $label"
  else
    fail "File missing: $label ($path)"
  fi
}

run_fixture_checks() {
  echo "── Fixture validity ──"

  # PDFs that must be valid
  check_pdf_valid "s1-single-pdf/book.pdf"            "$FIX/s1-single-pdf/book.pdf"
  check_pdf_valid "s2 slice 1"                         "$FIX/s2-pre-split-pdfs/01-intro.pdf"
  check_pdf_valid "s2 slice 2"                         "$FIX/s2-pre-split-pdfs/02-body.pdf"
  check_pdf_valid "s5-complete/book.pdf"               "$FIX/s5-complete/book.pdf"
  check_pdf_valid "stale-pipeline-json/book.pdf"       "$FIX/stale-pipeline-json/book.pdf"
  check_pdf_valid "library/calculus/book.pdf"          "$FIX/library/calculus/book.pdf"
  check_pdf_valid "library/probability/book.pdf"       "$FIX/library/probability/book.pdf"

  # PDF that must be intentionally corrupt
  check_pdf_corrupt "library/discrete-math/book.pdf"   "$FIX/library/discrete-math/book.pdf"

  # JSON files that must parse
  check_json_valid "s2 manifest.json"                  "$FIX/s2-pre-split-pdfs/manifest.json"
  check_json_valid "s5 pipeline.json"                  "$FIX/s5-complete/pipeline.json"
  check_json_valid "stale-pipeline-json"               "$FIX/stale-pipeline-json/pipeline.json"
  check_json_valid "library/probability pipeline.json" "$FIX/library/probability/pipeline.json"

  # Markdown / TOML existence
  check_file_exists "s3 markdown 1"                    "$FIX/s3-pre-split-md/01-intro.md"
  check_file_exists "s3 markdown 2"                    "$FIX/s3-pre-split-md/02-body.md"
  check_file_exists "s4 book.toml"                     "$FIX/s4-partial-mdbook/book.toml"
  check_file_exists "s4 SUMMARY.md"                    "$FIX/s4-partial-mdbook/src/SUMMARY.md"
  check_file_exists "s5 book-mdbook/book.toml"         "$FIX/s5-complete/book-mdbook/book.toml"

  # S0 must be empty (only .gitkeep)
  if [ "$(find "$FIX/s0-empty" -type f ! -name '.gitkeep' | wc -l)" = "0" ]; then
    pass "s0-empty contains only .gitkeep"
  else
    fail "s0-empty should be empty (no PDFs / markdown)"
  fi

  # S2 manifest must say status: complete
  if [ "$(jq -r '.status' "$FIX/s2-pre-split-pdfs/manifest.json")" = "complete" ]; then
    pass "s2 manifest.json status == complete"
  else
    fail "s2 manifest.json status should be 'complete'"
  fi

  # S5 pipeline.json must say status: complete
  if [ "$(jq -r '.status' "$FIX/s5-complete/pipeline.json")" = "complete" ]; then
    pass "s5 pipeline.json status == complete"
  else
    fail "s5 pipeline.json status should be 'complete'"
  fi

  # Stale fixture: pipeline.json says complete but no book-mdbook dir
  if [ ! -d "$FIX/stale-pipeline-json/book-mdbook" ]; then
    pass "stale-pipeline-json has no book-mdbook dir (intentional)"
  else
    fail "stale-pipeline-json should NOT have a book-mdbook dir"
  fi
}

# ── Hermes invocation (opt-in via HERMES_TEST=1) ──────────────────────────

run_hermes_invocation() {
  echo "── Hermes integration (HERMES_TEST=1) ──"

  if ! command -v hermes >/dev/null 2>&1; then
    echo "HERMES_TEST=1 set but \`hermes\` not on PATH; skipping integration tests" >&2
    return 0
  fi

  # Prepare a working-copy of the s1 fixture (do not mutate the committed one).
  local work
  work="$(mktemp -d -t ingest-pipeline.XXXXXX)"
  cp -a "$FIX/s1-single-pdf/." "$work/"

  echo "running ingest-pipeline against $work …"
  if hermes -p "Run the ingest-pipeline skill on the directory $work. Use --vision never. Do not invoke any other skills beyond what the orchestrator dispatches." >/tmp/ingest-pipeline-test.log 2>&1; then
    if [ -f "$work/pipeline.json" ] && [ "$(jq -r '.status' "$work/pipeline.json")" = "complete" ]; then
      pass "Hermes drove s1 fixture to status: complete"
    else
      fail "Hermes ran but pipeline.json missing or status != complete; see /tmp/ingest-pipeline-test.log"
    fi
  else
    fail "Hermes invocation failed; see /tmp/ingest-pipeline-test.log"
  fi

  rm -rf "$work"
}

# ── Main ──────────────────────────────────────────────────────────────────

main() {
  require_tools
  run_fixture_checks
  if [ "${HERMES_TEST:-0}" = "1" ]; then
    run_hermes_invocation
  fi

  echo
  echo "──────────────"
  echo "$PASS passed, $FAIL failed"
  if [ "$FAIL" -gt 0 ]; then
    exit 1
  fi
}

main "$@"
