---
name: ux-design
description: >-
  Audit or design the user experience of a web page or app: navigation, states, touch targets,
  focus, contrast, motion, responsive layout, copy in the interface. Runs a checklist pass
  against its bundled UX guidelines, then hands the visual direction to the frontend-design
  plugin skill. Use for "UX pass", "audit the UX", "does this page feel right", "make this
  usable on mobile", "accessibility check", or any new UI before it ships. Not for the
  aesthetic alone (frontend-design), charts (dataviz), diagrams (system-diagram), or adding a
  case-study page.
---

# Design UX

Two halves. This skill owns **usability**: can the reader find, read, tap, and understand it.
The `frontend-design` plugin skill owns **looks**; call it after step 3 whenever the task
creates or reshapes UI, not for a pure audit.

Rule list: [references/ux-guidelines.md](references/ux-guidelines.md), 119 rules with severity.
Only Critical, High and Medium rules on the relevant platform are in scope by default.

## Steps

1. **Design read, one line.** State what the page is, who reads it, on what device, and what
   the one job of the page is. Every finding below is judged against this line, so a
   recruiter-facing portfolio and an internal dashboard fail different rules.
2. **Audit against the list, in the browser, not from the code.** Start the app, use Playwright
   at 1440 and 390 in both themes, and check with scripts rather than by eye:
   - horizontal overflow: `document.documentElement.scrollWidth > innerWidth`
   - target size: every `a, button, [role=button]` bounding box ≥ 44 px on the short side at 390
   - focus: Tab through the page; every stop must be visible
   - contrast: compute muted-text and link ratios against their actual background, 4.5:1 body
   - anchors under a sticky header: `scroll-margin-top` set
   - `prefers-reduced-motion` honoured for anything that moves on its own
   - images: alt, intrinsic size, lazy below the fold
   - text under 12 px; body lines over ~80 ch
   Skip categories the page has no surface for (Forms on a page without forms).
3. **Findings table**: rule number, location, severity, fix or leave. Fix every Critical and High
   and every mechanical Medium in the same session. Leave taste calls and copy for the owner,
   listed.
4. **Looks**: if building or reshaping, invoke `frontend-design` now with the design read from
   step 1 as the brief. Its token plan must not undo a fix from step 3.
5. **Verify**: lint and build green, re-screenshot at both widths, re-run the step 2 scripts.
   A fix that isn't re-checked isn't done; go back to step 3 on any regression.

## Bad, then good

| ❌ | ✅ |
|---|---|
| "Accessibility looks fine" after reading the JSX | Contrast ratios and target sizes printed from a browser script |
| Fixing a hover-only affordance by adding a tooltip | Making the affordance visible at rest and reachable by keyboard |
| Loosening the whole type scale to fix one small label | Fixing that label and leaving the scale alone |
| Auditing at 1440 only | 390 first, since that is where overflow and targets fail |
| Rewriting the owner's copy to satisfy a Content rule | Flagging the line and leaving the words to the owner |

## Host repo hooks

- The host repo's folder manual (e.g. its `AGENTS.md`) says where a site's design rules and tokens
  live. Read them before step 3, and fold any new rule or token into them after a pass; no
  changelog.
- Findings that need the owner go in the reply, not in an inbox or capture file.
