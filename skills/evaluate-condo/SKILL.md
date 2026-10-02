---
name: evaluate-condo
description: Evaluate a Singapore condo listing or development and file a cited Buy/Neutral/Avoid note. Use for PropertyGuru, 99.co, EdgeProp, "evaluate this condo", or "is this unit worth it".
---

# Evaluate Condo

The full candidate-evaluation loop. Rule: condo research always pairs live listing data with a
structured valuation pass, never web research alone.

## 1 · Buyer context first

Read the buyer's financing constraints from the host repo's home-buying notes (its folder manual,
e.g. `AGENTS.md`, or the root index says where they live): loan envelopes and caps, purchase
mandate and exit window, crash-defensibility rules, current candidates. If the repo has no such
notes, ask the buyer for budget, financing and purpose before scoring anything. Confirm purpose:
**investment** is the default; if the buyer hints own-stay, ask, since it changes the rubric.

## 2 · Gather data (three sources, in parallel where possible)

**Listing page**, through Firecrawl (see the `web-extract` skill):
```bash
firecrawl scrape "<url1>" "<url2>" -f markdown,json --only-main-content -o "$SCRATCHPAD/"
```
Pass every listing URL in one call. PropertyGuru and 99.co sit behind Cloudflare; if a page
comes back thin, retry with `--wait-for 5000`, then stop and say so. Listing sites ship JSON-LD,
which is cleaner than the rendered text. Record: type, sqft, asking, psf, floor/stack, TOP
date, and **who is selling**: "developer's appointed sales team / VVIP discount" = unsold
developer stock, not a subsale.

**realsmart.sg** (preferred: cleanest structured project data). The **public page**
carries everything the logged-in view does:
```bash
firecrawl scrape "https://realsmart.sg/p/<slug>" -f markdown,json --only-main-content
# slug unknown? search the site rather than enumerating its sitemap:
firecrawl search "site:realsmart.sg/p <project name>" --limit 3
```
This carries REALSCORE, annualized profit, % profitable, transaction counts, holding period,
rental psf/yield, unit-size mix, per-block section and nearest-MRT. Only fall back to the
login-walled map SPA (`/map?id=<PROJECT>&mode=c`) through the Playwright MCP browser, with the
buyer logging in themselves, when a *specific* number is missing. Personal use only: low
volume, no bulk enumeration.

**Web research**: launch psf + take-up, last-12mo prints for the *same unit type*, nearest
completed comp, competing supply pipeline at the exit window, TOP date (listing vs marketing
vs news often disagree; pin it down, it moves the carry math by years).

## 3 · Run a valuation pass

If the host repo's manual names a property-analysis tool or repository, run it in an isolated
subagent (the host's own subagent mechanism, not another AI CLI) with the verified listing facts,
the realsmart data, the buyer context, the purpose and the standing alternatives to beat. Save its
result wherever that tool keeps its memory. Otherwise score the unit in this session against the
rules in §4, and say that no structured valuation tool was available.

## 4 · Analysis rules (lessons already paid for)

- **GFA harmonisation**: post-Jun-2023-application projects quote all-liveable sqft; older
  comps carry ~4–5% phantom area. Gross pre-harmonised comp psf **÷0.95** before comparing.
  realsmart/URA psf is raw lodged psf; always check which side each comp is on.
- **Never invent a price.** Every psf/quantum cited must trace to a print, a listing, or the
  buyer. Booking-day/asking prices are indicative until transacted.
- Compare within the **same size band** (small units structurally print higher psf) and
  against the **completed comp** (the tool's core question: why not buy that instead?).
- Deep discount = verify-first signal: same-type recent prints, seller motivation, defect risk.
- If the verdict is buy-adjacent, compute the **buy-price ladder**: fix exit psf by scenario
  (bear = comp flat / base / bull), solve entry for bear≈breakeven ("good") and
  base-beats-T-bills ("acceptable"); net of BSD, 2.18% agent+GST, legal.

## 5 · File it (reconcile in the same session)

Where each record lives is the host repo's call; its folder manual says where notes go. The usual
shape:

- A research note per development (frontmatter, verdict + confidence, cited sources, open
  questions), or a new dated § in the existing note.
- **Add/update the row in the condo research list** kept with the home-buying notes: verdict, our
  decision (no-buy is a first-class outcome), and the re-look trigger (the price/event that would
  reopen it). Never delete rows; when a decision lands later (e.g. booking-day outcome), update the
  row's Outcome.
- Update the home-buying index: Candidates one-liner + dated Decision line if a call was made. Fix
  cross-links both directions. Commit if the host repo's rules allow it without asking.
