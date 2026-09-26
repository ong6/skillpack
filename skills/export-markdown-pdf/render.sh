#!/usr/bin/env bash
# markdown-to-pdf — rasterise a PDF for visual inspection.
# Renders with BOTH engines: poppler resolves fonts by name and hides embedding
# faults; CoreGraphics (what Preview uses) trusts the embedded program. They
# disagree exactly where the bugs are, so always look at both.
# Usage: render.sh <file.pdf> [outdir]
set -euo pipefail

PDF="${1:-}"
if [ -z "$PDF" ]; then echo "usage: render.sh <file.pdf> [outdir]" >&2; exit 2; fi
if [ ! -f "$PDF" ]; then echo "no such file: $PDF" >&2; exit 2; fi
command -v pdftoppm >/dev/null || { echo "missing pdftoppm (brew install poppler)" >&2; exit 2; }

OUTDIR="${2:-$(mktemp -d)}"
mkdir -p "$OUTDIR"
rm -f "$OUTDIR"/poppler-*.png "$OUTDIR"/coregraphics-*.png

pdftoppm -png -r 100 "$PDF" "$OUTDIR/poppler"
qlmanage -t -s 1500 -o "$OUTDIR" "$PDF" >/dev/null 2>&1 || true
for f in "$OUTDIR"/*.pdf.png; do
  [ -e "$f" ] && mv "$f" "$OUTDIR/coregraphics-page1.png"
done

echo "Rendered to $OUTDIR:"
ls "$OUTDIR"/*.png
echo
echo "Read every poppler-*.png, plus coregraphics-page1.png. Check for:"
echo "  dropped letters · text past the page edge · tables split mid-row"
echo "  missing tick-boxes · heading stranded at a page foot · near-empty page"
