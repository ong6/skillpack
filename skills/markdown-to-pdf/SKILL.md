---
name: markdown-to-pdf
description: Convert a markdown note into a verified, print-ready A4 PDF. Use for printable notes, meeting handouts, or rebuilding generated PDFs; not for editing existing PDFs or building a LaTeX document.
---

# Markdown → printable PDF

Pipeline: strip frontmatter → pandoc → HTML + print CSS → headless Chrome → verify.

**Requires** `pandoc`, Google Chrome, and poppler (`brew install pandoc poppler`). `build.sh`
names every missing one.

## Workflow

Paths are relative to this skill's folder.

```
- [ ] 1. Build:  ./build.sh <source.md> [out.pdf]
- [ ] 2. Render: ./render.sh <out.pdf>
- [ ] 3. Read the PNGs it prints; look at every page
- [ ] 4. Fix the markdown or print.css, then return to step 1
- [ ] 5. Index the PDF wherever the source note is indexed
```

**Do not skip step 3.** `build.sh` catches font faults; only looking catches bad page breaks,
overflowing tables and dropped glyphs. `render.sh` rasterises with **two** engines because
poppler falls back to system fonts by name and will render a file that is corrupt in a real
reader.

Look for: dropped letters · text past the page edge · tables split mid-row · missing tick-boxes
· a heading stranded at a page foot · a near-empty page from a forced break.

## The font trap

**Never use `-apple-system`, `system-ui`, `Helvetica Neue`, `SF Pro`, or `Menlo`.** macOS ships
them as dfont/`.ttc` collections; Chrome's subsetter emits incomplete `glyf` data from those, so
readers that trust the embedded program drop scattered letters (`significant` → `si ni cant`)
while every terminal check passes.

**Rule: plain, static `.ttf` only.** `/System/Library/Fonts/Supplemental/` is nearly all plain
TTFs; `/System/Library/Fonts/` holds the collections. For this machine, default to **Arial** body
and **Andale Mono** code. A bundled static open font such as Noto Sans or Inter is also acceptable
for a cross-machine artifact, but verify that the exact files exist, embed them explicitly with
`@font-face`, and reject variable-font or OS-fallback substitutions. Never silently switch font
families between builds.

**Not the bug:** several subsets sharing one base name (`ArialMT` ×4). Chrome subsets per page;
don't "fix" it.

In the handoff, name the exact body/code font files used, the Pandoc reader, both rasterizers,
and whether every page was visually checked. A terminal-only font or text-extraction check does
not count as a verified PDF.

## Pandoc gotchas

- **`-tex_math_dollars` is mandatory**, or `S$1,200 … S$60` currency pairs parse as TeX math.
  Use `--from=gfm+task_lists-tex_math_dollars`.
- **Task-list checkboxes need CSS help.** Pandoc's stylesheet pushes the `<input>` off-page;
  `print.css` hides it and draws the box with `li::before`.
- **`--standalone` adds a title block** above the document's own `# H1`; `print.css` hides it.
- Emoji embed as `AppleColorEmoji` Type 3 bitmaps and print fine.

## Customising

Edit [`assets/print.css`](assets/print.css). Current spec:

| Property | Value | Why |
|---|---|---|
| Page | A4, 16mm top/bottom, 18mm sides | ~174mm measure |
| Body | 10pt / 1.45 | Above the ~8–10pt floor where reading speed collapses |
| Measure | prose capped at 150mm (~75 chars) | The 50–75 character rule; tables stay full width |
| Code | 8.5pt Andale Mono | Readable without dominating |
| Headings | H1 19pt · H2 13pt · H3 10.5pt | Hierarchy legible at a glance |
| Tables | 8.9pt, header row repeats across pages | Dense reference data |

Breaks: headings never orphan, table rows and callouts never split, `thead` repeats, paragraphs
keep 2-line orphans/widows.

**To start a section on a fresh page**, add its id to the `break-before: page` rule. Pandoc
strips leading numbers (`## 3. The question sheet` → `#the-question-sheet`) and an em dash
leaves a **double** hyphen. Don't guess the id; print the real ones:

```sh
pandoc --from=gfm+task_lists-tex_math_dollars --to=html <source.md> | grep -o 'id="[^"]*"'
```

## Filing

- The **markdown is the source of truth**; the PDF is a build artifact. Say in the source note
  that it rebuilds with this skill, and index the PDF beside the note.

Typography sources: [Butterick, line length](https://practicaltypography.com/line-length.html) ·
[Baymard, optimal line length](https://baymard.com/blog/line-length-readability).
