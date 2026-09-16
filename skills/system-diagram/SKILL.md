---
name: system-diagram
description: >-
  Draw a polished system or architecture diagram as hand-authored inline SVG: request flows, RAG
  and agent pipelines, ingest queues, service maps, before/after comparisons. Use for "system
  diagram", "architecture diagram", "draw the flow", "diagram how X works", or a figure for
  a website, a case study, a README, or a research note. Not for charts of data (dataviz), UI
  mockups (design), or a one-hop relationship that a sentence explains faster.
---

# System diagram

Hand-drawn SVG, showcase quality. The bar is a figure you would put in a conference talk: a cold
reader sees the mechanism in ten seconds, and nothing on the canvas is there for decoration.

Built-in `artifact-diagramming` covers the basics (draw the mechanism, label arrows, `currentColor`,
markers, `viewBox`). This skill adds the taste spec, the workflow, and the output targets used
here. Read that skill too when it is available; do not restate it.

## Workflow

1. **Write the claim first.** One sentence: what the reader should see. "A question fans out to
   five knowledge bases in parallel and only chunks above 0.35 similarity reach the model." If you
   cannot write it, you do not know what to draw yet.
2. **List the parts the claim hinges on** and nothing else. Every box must appear in the claim or
   in an arrow label. Cut the rest. Eight to twelve nodes is the usual ceiling for one figure; past
   that, split into two figures with two claims.
3. **Choose a layout.** Left-to-right for a flow through time, top-to-bottom for layers, swimlanes
   when two actors or two environments matter, side-by-side when comparing options.
4. **Lay out on a grid** (spec below). Compute positions in code or a scratch table; never nudge by
   eye.
5. **Render and look at it.** Screenshot at the size it will be shown, in light and dark. Then ask
   the four questions in [Review](#review). Fix, re-render, repeat. Two passes minimum.
6. **Caption.** A `figcaption` stating the claim in one sentence. Explanations live there, not in
   the drawing.

## Taste spec

Numbers are for a `viewBox` roughly 960 wide. Scale proportionally.

| Element | Rule |
|---|---|
| Grid | 8px base. Node x/y, widths, and gaps are multiples of 8. Columns share x; rows share y. |
| Node | `rect` with `rx="6"`, stroke 1.25 `currentColor` at 0.55 opacity, no fill (or the page surface token). Height 56 for a single label, 72 with a sub-label. |
| Gap | 40 between nodes in a flow, 64 between groups. Never under 32; arrows need room for labels. |
| Type | Label 13px, weight 600. Sub-label 11px monospace, 0.7 opacity. Arrow label 11px monospace. Group title 11px monospace uppercase, letter-spacing .08em. |
| Arrows | `stroke-width 1.25`, `marker-end`, arrowhead 8 long. Straight or one right-angle bend. No curves unless a swimlane forces it. Label sits 6px above the line, centred, with a page-colour underlay so it never crosses the stroke. |
| Groups | Dashed `rect` at 0.35 opacity, `rx="10"`, padding 24, title top-left inside. Use for an environment, a tenant boundary, an async region. |
| Accent | One hue, the site's theme accent, on the single path the claim is about. Everything else `currentColor`. |
| Numbering | Small circled digits (r=9, 10px) on steps when order matters. Refer to them in the caption. |
| Whitespace | 40px margin all round inside the `viewBox`. Crowded reads as careless. |
| Scale | Type sizes above assume the SVG renders at about its `viewBox` width. Decide the render width first (column width, or a breakout), then size the `viewBox` to it. A 1120 `viewBox` squeezed into a 680 column puts 13px labels at 8px. |
| Text | Two or three words per label. If a label wraps, the node is doing two jobs. |

❌ / ✅

| ❌ | ✅ |
|---|---|
| Box labelled "RAG pipeline" | Chunk → Embed → pgvector, three boxes, arrows labelled `~1000 chars`, `1536-dim` |
| Arrow with no label | `cosine · floor 0.35` |
| Five colours, one per service | `currentColor` everywhere, accent on the retrieval path only |
| Curved connectors crossing each other | Re-order the nodes until arrows are straight or one bend |
| Legend explaining dashed = async | `async · QStash` written on the dashed arrow |
| A diagram that inventories every table | Only the tables the request touches |
| Sentence inside a node | Sentence in the caption |

## Output targets

**A React site.** Use [`ong6/uipack`](https://github.com/ong6/uipack) (`npm install github:ong6/uipack`):
`Figure` (mono `FIGURE 01 · EYEBROW`, title, one-line caption, legend, Pause and Replay), `Lane`,
`Group`, `Node` (icon, label, mono sub), `Chip`, `Connector` (orthogonal, arrowheads) and `Packet`
(a legend-shaped token animated along a connector, static at its midpoint under reduced motion).
The visual reference is the figure style in OpenAI's Habitat storage post. Put packets on the
flows the claim is about, one kind per direction (request, response, change), never on every
line. Test motion in a real browser: position changes while playing, holds after Pause, static
under `prefers-reduced-motion`.

**A site with its own diagram components and no uipack.** Follow the conventions the invoking skill or the
repo supplies: component location, shared primitives, colour tokens, and how the narrow variant is
switched in. Never put `<style>`, `<script>`, or external refs inside the SVG. If labels drop under
~10px at 390 wide, provide a stacked variant rather than shrinking.

**Markdown notes and READMEs.** A standalone `.svg` beside the note, referenced with a
relative image link. `currentColor` does not inherit through `<img>`, so set explicit strokes and
text fill for a light page and keep them readable on GitHub's dark theme (mid greys, not pure
black).

**Artifacts.** Inline `<svg>` in the HTML page per `artifact-diagramming`.

## Review

Before handing over, answer each in writing:

1. Can a stranger state the claim from the picture alone, without the caption?
2. Is every arrow labelled, and does every box appear in the claim or an arrow label?
3. Do all x and y values sit on the 8px grid, and does every column and row align?
4. Does it read in dark mode at 390px wide?

A "no" means go back to step 4 of the workflow, not ship with a note.
