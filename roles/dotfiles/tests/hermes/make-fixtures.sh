#!/usr/bin/env bash
# Regenerate the synthetic-PDF fixtures used by the ingest-pipeline test harness.
# Usage: ./make-fixtures.sh
# Requires: python3 with reportlab installed (pip install reportlab) OR pandoc.
set -euo pipefail

FIX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/fixtures"

generate_pdf() {
  local out_path="$1" title="$2"
  if python3 -c 'import reportlab' 2>/dev/null; then
    python3 - "$out_path" "$title" <<'PY'
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

out_path, title = sys.argv[1], sys.argv[2]
c = canvas.Canvas(out_path, pagesize=letter)
for i in range(1, 5):
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, 720, f"{title} — Page {i}")
    c.setFont("Helvetica", 12)
    c.drawString(72, 690, f"This is synthetic page {i} of {title}.")
    c.drawString(72, 670, "Generated for ingest-pipeline test fixtures.")
    c.showPage()
c.save()
PY
  elif command -v pandoc >/dev/null 2>&1; then
    local tmp
    tmp="$(mktemp -t fixmd.XXXXXX.md)"
    {
      echo "# $title"
      for i in 1 2 3 4; do
        echo
        echo "## Page $i"
        echo
        echo "This is synthetic page $i of $title."
      done
    } > "$tmp"
    pandoc -o "$out_path" "$tmp"
    rm -f "$tmp"
  else
    echo "make-fixtures: need python3+reportlab or pandoc on PATH" >&2
    exit 1
  fi
}

mkdir -p "$FIX_DIR/s1-single-pdf" \
         "$FIX_DIR/s2-pre-split-pdfs" \
         "$FIX_DIR/s5-complete" \
         "$FIX_DIR/stale-pipeline-json" \
         "$FIX_DIR/library/calculus" \
         "$FIX_DIR/library/probability" \
         "$FIX_DIR/library/discrete-math"

# Single-PDF fixtures
generate_pdf "$FIX_DIR/s1-single-pdf/book.pdf" "Single Large PDF"
generate_pdf "$FIX_DIR/s5-complete/book.pdf" "Complete Book"
generate_pdf "$FIX_DIR/stale-pipeline-json/book.pdf" "Stale Pipeline JSON"

# Slice fixtures (S2)
generate_pdf "$FIX_DIR/s2-pre-split-pdfs/01-intro.pdf" "Chapter 1 — Introduction"
generate_pdf "$FIX_DIR/s2-pre-split-pdfs/02-body.pdf" "Chapter 2 — Body"

# Library fixtures
generate_pdf "$FIX_DIR/library/calculus/book.pdf" "Calculus"
generate_pdf "$FIX_DIR/library/probability/book.pdf" "Probability"

# Library — discrete-math is intentionally a corrupt PDF (zero-byte)
: > "$FIX_DIR/library/discrete-math/book.pdf"

echo "Fixtures regenerated under $FIX_DIR"
