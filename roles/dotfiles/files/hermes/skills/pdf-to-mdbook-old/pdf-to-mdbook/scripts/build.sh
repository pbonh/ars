#!/usr/bin/env bash
# build.sh — Run `mdbook build` in a book directory and surface common
# errors with hints. The agent runs this and only reads the output if
# the exit code is nonzero.
#
# Usage:  ./build.sh <book-output-dir>

set -u

DIR="${1:-.}"

if ! command -v mdbook >/dev/null 2>&1; then
    cat >&2 <<EOF
ERROR: mdbook is not installed.

Install with one of:
  cargo install mdbook
  # or download a binary release:
  https://github.com/rust-lang/mdBook/releases
EOF
    exit 127
fi

if [ ! -f "$DIR/book.toml" ]; then
    echo "ERROR: $DIR/book.toml not found. Run init_mdbook.py first." >&2
    exit 1
fi

cd "$DIR" || exit 1

echo "Building mdBook in $(pwd)..."
OUTPUT=$(mdbook build 2>&1)
RC=$?

echo "$OUTPUT"

if [ "$RC" -ne 0 ]; then
    echo
    echo "--- Build failed. Common causes: ---"
    if echo "$OUTPUT" | grep -q "Couldn't find file"; then
        echo "  • A SUMMARY.md link points to a missing file."
        echo "    Compare slugs in src/SUMMARY.md vs filenames in src/:"
        echo "      ls src/*.md"
        echo "      grep -E '\\.md\\)' src/SUMMARY.md"
    fi
    if echo "$OUTPUT" | grep -qi "summary parsing"; then
        echo "  • src/SUMMARY.md has a syntax error (mixed list markers,"
        echo "    bad indentation, or part-heading after numbered chapters)."
    fi
    if echo "$OUTPUT" | grep -qi "invalid heading"; then
        echo "  • A chapter file doesn't start with '# Title'."
        echo "    Each chapter must begin with a level-1 heading."
    fi
    exit "$RC"
fi

echo
echo "Build succeeded. Output:"
echo "  $(pwd)/book/index.html"
echo
echo "For live preview with auto-reload:"
echo "  cd $DIR && mdbook serve --open"
