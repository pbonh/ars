#!/usr/bin/env bash
set -euo pipefail

MAX_ITERATIONS="${1:-5}"
# CRITICAL: Working directory is PROJECT-LOCAL (./.harness/)
HARNESS_DIR="${PWD}/.harness"
PROJECT_DIR="${PWD}"
# System prompts are GLOBAL (from ~/.pi/harness/)
SYSTEM_PROMPT_DIR="${HOME}/.pi/harness"

# Ensure project-local harness directory exists
mkdir -p "$HARNESS_DIR"

echo "=== Adversarial Loop: max $MAX_ITERATIONS iterations ==="
echo "=== Working in: $HARNESS_DIR ==="

for i in $(seq 1 "$MAX_ITERATIONS"); do
	ITER_DIR="$HARNESS_DIR/iteration-$i"
	mkdir -p "$ITER_DIR"

	echo ""
	echo "--- Iteration $i/$MAX_ITERATIONS: Generator ---"

	# Build the generator's prompt
	GEN_PROMPT="Read your instructions at ${SYSTEM_PROMPT_DIR}/generator-prompt.md. This is iteration $i. Work in the project directory: ${PROJECT_DIR}"
	if [ "$i" -gt 1 ]; then
		PREV=$((i - 1))
		GEN_PROMPT="$GEN_PROMPT Read the evaluator's feedback at .harness/iteration-$PREV/evaluation.md before starting."
	fi

	# Spawn generator subagent
	# Note: pi --print runs from PROJECT_DIR, system prompt from SYSTEM_PROMPT_DIR
	(cd "$PROJECT_DIR" && pi --print "$GEN_PROMPT" \
		--system-prompt "$(cat "${SYSTEM_PROMPT_DIR}/generator-prompt.md")" \
		--no-session) \
		>"$ITER_DIR/generator-log.txt" 2>&1 || true

	echo "--- Iteration $i/$MAX_ITERATIONS: Evaluator ---"

	# Spawn evaluator subagent
	EVAL_PROMPT="Read your instructions at ${SYSTEM_PROMPT_DIR}/evaluator-prompt.md. Evaluate iteration $i. The generator's notes are at .harness/iteration-$i/generator.md. Work in project directory: ${PROJECT_DIR}"

	(cd "$PROJECT_DIR" && pi --print "$EVAL_PROMPT" \
		--system-prompt "$(cat "${SYSTEM_PROMPT_DIR}/evaluator-prompt.md")" \
		--no-session) \
		>"$ITER_DIR/evaluator-log.txt" 2>&1 || true

	# Check verdict
	if [ -f "$ITER_DIR/evaluation.md" ]; then
		if grep -qi "^### Overall Verdict" "$ITER_DIR/evaluation.md" 2>/dev/null &&
			grep -qi "PASS" <(sed -n '/^### Overall Verdict/,/^###/p' "$ITER_DIR/evaluation.md" 2>/dev/null); then
			echo ""
			echo "=== PASSED at iteration $i ==="
			echo "=== Results in: $HARNESS_DIR ==="
			exit 0
		fi
	fi

	echo "    FAIL — continuing to next iteration"
done

echo ""
echo "=== Reached max iterations ($MAX_ITERATIONS) without PASS ==="
echo "=== Results in: $HARNESS_DIR ==="
exit 1
