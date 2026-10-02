---
name: review-a-quote
description: Review and file a vendor or construction quotation, assess commercial terms and line items, and separate immediate asks from parked items. Use for "check/review this quote" or quote PDFs.
---

# Review Quote

The output is never just an opinion. It is (1) an updated project note, (2) a decision list for
the owner, and (3) a short list of asks ready to become an email.

## Step 0 — File the document before reading it

File the PDF where the host repo keeps source documents (its folder manual, e.g. `AGENTS.md`,
says where; a project's `source-docs/` folder is a common shape) under a dated name such as
`YYYY-MM-<what>-<vendor>[-<headline-price>].pdf`, add its row to that folder's index, and extract
text (`pdftotext -layout`) into the scratchpad. Never quote a number from memory of the
PDF — re-extract and check.

## Step 1 — Pin the mappings FIRST

Before any analysis, build the authoritative lookup table in the project note: item → tag → room
→ floor → qty, whatever the document's unit of meaning is. Mark it **authoritative, do not
re-derive from the PDF**, and record any trap explicitly (e.g. two vendors using the same room
name for different rooms). This is the single highest-value step: downstream errors commonly
come from re-deriving this mapping per session. Owner confirmation outranks
inference: if the owner corrects a row, the correction wins and gets dated.

## Step 2 — The commercial frame (before any line item)

These four questions decide whether line-item work is even worth doing:

1. **What's the allowance?** Quote vs PC sum / budget line, incl-vs-excl GST stated explicitly.
2. **Who keeps a saving?** Under a PC sum, savings may credit the main contract, not the owner.
   If unknown, that's a QS question that gates every money ask; flag it to the owner before
   drafting anything.
3. **Bundle terms.** If discounts are bundle-conditional, never recommend deleting line items.
   Ask for a revised bundle quote instead, and back-solve suspicious prices (a price that is
   exactly list×discount is a spec argument, not a discount argument).
4. **Timeline.** Quote validity vs the owner's decision date vs lead times. A quote that lapses
   before the decision is a real ask; log it even if it's parked.

**Re-tender or not:** if the quote sits on/near the allowance and the discounts are auditable,
savings live in *spec* (cheaper item on unimportant doors/rooms), not in switching vendor. Say so
plainly and stop suggesting tenders.

## Step 3 — Line items, compared like-for-like

- Compare items by **function**, not price bracket. A face handle competes with a face handle; a
  recessed edge pull is a different object. (This mistake once produced a wrong four-figure saving
  claim.)
- Check finishes/materials **against the adjacent packages** already decided (sanitary, lighting,
  joinery). Cross-package clashes (nickel handle in a bronze room) are findings the vendor
  can't see and the owner will.
- Every number in the write-up traces to the extracted text. Cells you can't trace get `TODO`,
  not a guess.

## Step 4 — Record decisions, not analysis

When the owner rules ("the utility rooms can take a cheaper lever", "keep the theme in the
baths"), write the decision into the note **verbatim as a quote block with a date**, then the derived table
(item, change, ± amount). Owner decisions are append-only history; never silently revise one.

## Step 5 — Split the output

Two lists, kept apart:

- **Asks now** → hand to the email draft (the host's email-writing skill, if it has one). Only
  decisions and blocking questions.
- **Parked** → a "deliberately left out" block in the note: corrections, typos, stale rates,
  validity, payment terms, raised when the revised quote comes back, not before. The email is
  what we want; the note is what we know.

## Related

- An email-drafting skill, if the host has one, turns the asks list into the reply.
- The shape to aim for in the project note: a door or item map, an asks table, and a "parked
  items" block, with the reply draft filed beside it.
