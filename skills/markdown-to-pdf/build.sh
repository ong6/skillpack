#!/usr/bin/env bash
# markdown-to-pdf — markdown note -> print-ready A4 PDF, with font verification.
# Usage: build.sh <source.md> [output.pdf]
set -euo pipefail

SRC="${1:-}"
if [ -z "$SRC" ]; then echo "usage: build.sh <source.md> [output.pdf]" >&2; exit 2; fi
if [ ! -f "$SRC" ]; then echo "no such file: $SRC" >&2; exit 2; fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSS="$HERE/assets/print.css"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# --- dependencies: name everything missing at once, don't fail one at a time ---
missing=()
command -v pandoc   >/dev/null || missing+=("pandoc (brew install pandoc)")
command -v pdffonts >/dev/null || missing+=("pdffonts (brew install poppler)")
[ -x "$CHROME" ]                || missing+=("Google Chrome at $CHROME")
if [ ${#missing[@]} -gt 0 ]; then
  printf 'missing dependency: %s\n' "${missing[@]}" >&2
  exit 2
fi

OUT="${2:-$(dirname "$SRC")/$(basename "${SRC%.md}").pdf}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# 1. strip YAML frontmatter — pandoc would render it as a duplicate title block
awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$SRC" > "$WORK/doc.md"
cp "$CSS" "$WORK/print.css"

# 2. markdown -> HTML.  -tex_math_dollars is REQUIRED: without it pandoc reads
#    "S$1,200 ... S$60" currency pairs as TeX math and mangles every price.
pandoc "$WORK/doc.md" \
  --from=gfm+task_lists-tex_math_dollars \
  --to=html5 --standalone \
  --metadata title="$(basename "${SRC%.md}")" \
  --css=print.css \
  --output="$WORK/doc.html"

# 3. HTML -> PDF.  virtual-time-budget lets layout and font loading settle before
#    the snapshot; 4s is far more than a local file needs and costs nothing.
"$CHROME" --headless --disable-gpu --no-sandbox --no-pdf-header-footer \
  --run-all-compositor-stages-before-draw --virtual-time-budget=4000 \
  --print-to-pdf="$WORK/doc.pdf" "file://$WORK/doc.html" 2>/dev/null

[ -s "$WORK/doc.pdf" ] || { echo "FAIL: Chrome produced no PDF" >&2; exit 1; }

# 4. verify --------------------------------------------------------------
fail=0

# 4a. Fonts from macOS dfont/TTC collections subset badly and drop glyphs in some
#     viewers while looking perfect in poppler. See SKILL.md 'the font trap'.
#     (Multiple same-named subsets are NORMAL — Chrome subsets per page. Not a fault.)
banned="$(pdffonts "$WORK/doc.pdf" | grep -Ei '\.SF|SFNS|HelveticaNeue|Menlo' || true)"
if [ -n "$banned" ]; then
  echo "FAIL: collection-sourced font embedded — fix the font stack in assets/print.css" >&2
  echo "$banned" >&2; fail=1
fi

# 4b. A non-embedded font means the viewer substitutes whatever it likes.
notemb="$(pdffonts "$WORK/doc.pdf" | tail -n +3 | awk '$5=="no"{print $1}' || true)"
if [ -n "$notemb" ]; then
  echo "FAIL: font(s) not embedded:" >&2
  echo "$notemb" >&2; fail=1
fi

[ "$fail" -eq 0 ] || exit 1

cp "$WORK/doc.pdf" "$OUT"
pages=$(python3 -c "import re,sys;print(len(re.findall(rb'/Type\s*/Page[^s]',open(sys.argv[1],'rb').read())))" "$OUT")
echo "OK  $OUT  (${pages} pages)  — font checks passed"
echo "NEXT: $HERE/render.sh '$OUT'   then read the PNGs. Do not skip this."
