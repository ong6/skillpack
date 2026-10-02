---
name: compare-price
description: Compare what one product (or a tier spread of competing products) costs across Singapore, the US, and any other named country, reported in SGD with live FX and landed cost. Use for /compare-price, "where in the world is it cheapest", "SG vs US price", or "should I buy this overseas"; not for single-region deal hunting or picking which model to buy (product-shopping).
---

# Compare Prices

What a thing costs in the places the user can buy it, in SGD, with a verdict on where to buy and
whether it's worth it.

`/compare-price <product or category> [--add jp kr]`. A category ("air purifier for 12m2 room")
means build the spread yourself.

## Regions and currency

- **Always SG and US.** Add any country the user names (`--add jp kr cn hk` or plain words).
- **Report in SGD**, local price → SGD alongside. SGD is the decision currency.
- **Fetch live FX every run**; never reuse rates from a previous session or file. State rates and
  date at the bottom.

## Two axes

Do both unless the request is obviously one-sided.

1. **Geography:** same product, different countries.
2. **Product spread:** the tier ladder, so the user sees what the money buys. **Budget** (cheapest
   that does the job), **Value** (the pick, best spec per dollar), **Premium** (what more money
   gets), **Overpriced** (the popular bad-value option, named). Cover variants within a line
   (Lite/Pro/Max, wired/wireless, regional SKUs): the cheapest region often stocks only a different
   variant, and that trap is what the comparison exists to catch.

## Rules

**Landed cost, not sticker.** Always account for and state:
- US prices exclude sales tax (0–10% by state); SG prices include 9% GST, and imports attract it.
- Shipping and forwarder fees if not hand-carried.
- Plug/voltage: US 110V / Type A, SG 230V / Type G. Flag anything needing a transformer, not just
  an adapter; this kills many US appliance buys outright.
- Warranty: grey/parallel imports usually have none locally. Say so for anything with a motor,
  battery, or compressor.

**Consumables are the real cost.** For filters, cartridges, pods, blades: price the consumable and
its interval and give a 3-year total. The cheap unit with expensive filters loses.

**Mark confidence on every price:** `verified` (loaded the retailer page this session), `approx`
(review, roundup, aggregator), `unverified` (recalled or inferred). Never present approx as fact.
No price found in a region → "not found"; never interpolate.

**Name the retailer.** "S$165, Challenger" is actionable; "S$180 in Singapore" is not. Prefer
official/authorised stores and say when a price is marketplace-only.

**Say when it doesn't matter.** Spread under ~15% → "buy it locally, the difference isn't worth
the hassle".

## Method

1. Live FX for every currency involved.
2. Search per region with local retailers, **in parallel**. SG: Lazada, Shopee, Challenger, Courts,
   Harvey Norman, brand SG store. US: Amazon, Best Buy, brand direct, B&H. JP: Amazon.co.jp,
   Yodobashi, Rakuten. KR: Coupang, Naver. CN: JD, Tmall. HK: Price.com.hk.
3. Build the spread, 3–5 products.
4. Landed cost plus 3-year consumable cost.
5. Verdict.

## Output

Verdict in two sentences (what to buy, where), then the work. One table per product, or regions as
columns for a spread:

| Product | 🇸🇬 SG | 🇺🇸 US | 🇯🇵 JP | Cheapest | Notes |
|---|---|---|---|---|---|
| Levoit Core 300S | S$169 `verified` | US$99 → S$134 `approx` | — | US +26% | 110V, needs transformer, kills the saving |

Always close with: 3-year total for the top 2–3 picks; **what I'd actually do**, one paragraph, a
decision not a menu; FX rates and date. Date-stamp the output.

Offer an Artifact when the comparison exceeds ~3 products or the user will keep it; never for a
quick one-off.

## Notes

- If the host repo keeps a travel buying list (its folder manual, e.g. `AGENTS.md`, says where
  notes go), offer to add the item, ask first, and follow that list's own conventions.
