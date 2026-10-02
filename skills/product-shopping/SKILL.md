---
name: product-shopping
description: Recommend what product to buy, or find the best legitimate price for a chosen model in the buyer's own region. Use for comparisons, shortlists, "is X worth it", "which X should I get", cheapest price, deal checks, or price history; not for cross-country SG-vs-US comparisons in SGD (compare-price) or just listing which shops carry an item.
---

# Compare Products

Decide **what** to get (Track A), then find the best **price** (Track B). Run whichever the ask needs.

- **Model not pinned down** ("what should I get", "compare these", "is X worth it") → Track A,
  which hands the winner to Track B for the **Before you buy** line.
- **Exact model known** ("where's it cheapest", "is this deal good", "price history", "good time
  to buy") → Track B directly. Skip Track A's interview.

Before shortlisting, read the owner's **brand exclusions** in the host repo's shopping notes (its
folder manual, e.g. `AGENTS.md`, says where notes go) and never recommend an excluded brand, even
as a budget backup.

# Track A: decide what to buy

Interview before researching. Generic research disappoints because it searches before it
understands the decision. **No searching until the Step 3 gate passes.** If the ask isn't a
purchase recommendation, say so and stop.

### 1 · Opening question (one message)
Ask for a brain-dump in their own words: what they're buying (category, models in mind), what for
(the real job, where/how/how often), what they already know or ruled out and why, budget and where
they'll buy (country/currency), what "good" looks like. Close with "...and anything else you think
matters." One friendly block, not a form; say a sentence or just the product name is plenty
because the next step is tap-to-answer.

### 2 · Gap analysis (internal)
Score the request against the decision-dimension checklist in `REFERENCE.md` §1: each dimension
known / unknown / not-applicable. Keep only the unknowns that would change the recommendation.
Those blind spots are the main value-add.

### 3 · Clarify the gaps (gate)
Ask the **2–4 highest-leverage unknowns in one round** with the structured user-input tool when
available, else one compact message. Every question has concrete pre-filled options; never force a
long typed answer.
- Most-likely / recommended option first.
- `multiSelect: true` when several answers can be true at once.
- For a factor the buyer likely didn't know mattered, fold a one-line *why it matters* into the
  question.
- Second round only if an answer opens a fork that changes the shortlist.
- Don't ask what they already answered or anything irrelevant to the category.
- "Other" and "just go" are always available; on "just go", state your assumptions and proceed.

### 4 · Research
Triangulate; never trust a single source.
- Independent hands-on tests, aggregated owner reviews, forum sentiment, spec sheets.
- Hunt failure modes, reliability, common complaints, not just praise.
- Check recency: current model? refresh or seasonal sale imminent?
- Discount affiliate listicles, sponsored placements, astroturf; weight independent testing.
- **Marketing is a claim, not evidence.** For each claim ask "what spec, test, or mechanism backs
  this?" and find it. For measurable products lead with independent measurements, standards,
  teardowns, datasheets; decode buzzwords into the spec that matters (`REFERENCE.md` §3). Scale
  depth to stakes: full workup for spec-driven, expensive or health items, light touch for a mug.
- Narrow to 2–4 contenders scored on *the buyer's ranked priorities*. Never a generic "best overall".

### 5 · Deliver
Use the template in `REFERENCE.md` §4: top pick and why it fits *them*, runner-up ("pick this
instead if you weigh X more"), trade-off table across their priorities, what to avoid / common
regrets, pre-purchase checks, confidence and what would change the call. Then hand off to Track B.

# Track B: find the best price

Lowest legitimate price for a **specific** model/variant, not a category.

### 1 · Pin the exact item
Model number, variant, size/colour where price differs, region and currency. Ask only if missing.

### 2 · Check the local cache first
`price-cache.py`, in this skill's base directory (run it; `--help` lists commands), holds prices
already gathered, dated, with currency, url and condition. The cache is the host repo's data, not
the skill's: it defaults to `resources/shopping/price-cache.json` under the host repo root
(`$PDS_ROOT`, else the Git toplevel of the working directory); `--cache` or `PRICE_CACHE`
overrides it. Below, `PC` is `python3 <skill dir>/price-cache.py`.
- `$PC cheapest "<model>" [--currency <CUR>] --available` gives an instant answer if we've seen it, and warns when results span currencies.
- `$PC stale --days 30` lists what to re-fetch. Re-fetch only stale/missing items; trust the rest.

### 3 · Sweep current listings, structured sources first
Start from the host repo's venue directory if it keeps one (the shopping notes above), then
widen. A CAPTCHA or bot-wall means you're using the hard door; an allowed one almost always
exists. In order:
1. **Official / aggregator data**: retailer or brand API, product feed, RSS, sitemap; aggregators
   (Google Shopping, PriceSpy, PriceRunner, Idealo) and trackers (Keepa, camelcamelcamel). Stable,
   no walls, history for free.
2. **Live web search** across the region's major retailers.
3. **`web-extract`** (Firecrawl) for prices behind JS; it costs credits, so try WebFetch first.
4. **Your own logged-in session** (Playwright) where the owner has an account. Legitimate access,
   not evasion.

Record findings: `$PC record <source> <category> "<title>" <lo> <hi> --currency <CUR> [--url <link>] [--condition new|refurb|used]`.
**Always pass `--currency`**; without it prices can't be compared across regions.

On CAPTCHA / bot-detection / paywall, stop and report (`web-extract`'s hard stop) and try another
source. Never auto-solve CAPTCHAs or rotate identities/proxies.

### 4 · Price history
Amazon: camelcamelcamel / Keepa. Elsewhere: PriceSpy / PriceRunner / Idealo / Google Shopping or the
category's known tracker (`REFERENCE.md` §6.4).

### 5 · Landed cost
Add shipping, taxes/import/duty, subtract valid coupons/cashback. Rank by what you actually pay
(`REFERENCE.md` §6.1).

### 6 · Verify the winner
Open the listing: price, right model, in stock, ships to region, reputable seller (not grey-market
or counterfeit).

### Price report
- **Cheapest legit option:** price, landed cost, retailer, condition, link.
- **Runner-up(s):** especially a more trusted seller if the cheapest is risky.
- **Deal verdict:** *good now / wait / average* against typical and recent low (`REFERENCE.md` §6.5).
- **Watch-outs:** fake "was" prices, expired or region-locked coupons, refurb vs new, model-year
  confusion (`REFERENCE.md` §6.2–6.3).

# Rules

- Honor the buyer's region, currency, and what's actually available to them.
- Cite sources; separate measured fact from reviewer opinion; flag thin evidence.
- Date every price; if unconfirmed, say "verify at checkout".
- Surface refurbished/open-box when the buyer is open to it.
- **Legitimate sources only:** real retailers, official refurb/used marketplaces, valid public
  coupons. No leaked keys, dubious grey-market, coupon fraud, or scraping against a site's terms.

# Companion skills
- **`web-extract`**: Firecrawl for pages a plain fetch can't read; honors its own hard stop.
- **`youtube-transcript`**: mine video reviews for real-world failure modes (Track A).
- **`compare-price`**: the same product across SG, US and other countries in SGD.

See [REFERENCE.md](REFERENCE.md): §1 dimension checklist, §2 category blind spots, §3 source
rubric, §4 output template, §5 worked example, §6 pricing reference.
