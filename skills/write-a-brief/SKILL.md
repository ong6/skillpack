---
name: write-a-brief
description: Write or tighten a one-to-two-page meeting brief for a professional (contractor, consultant, doctor, vendor). Use for "meeting brief", "prep doc", "questions to ask", or fixing a brief that is too long or AI-sounding; not for email drafts or general notes.
---

# Write Brief

The reader is the owner, in a room, under time pressure, with a professional waiting. A thing
you glance at, not a report.

## Step 0: frame it

Answer three questions from the background note or by asking:

1. **What does the owner walk out holding?** A quote, a drawing, a date, a decision. Name the
   artefacts in the first three lines.
2. **How good is this person?** Assume competent and experienced until shown otherwise.
3. **What expires?** Anything that gets expensive or impossible after a date: a roof closing,
   a membrane going down, an application still open, a return window. Usually the real reason
   the meeting is now; it gets its own block.

## Step 1: the competence split

This is the whole skill. Every candidate item goes in exactly one bucket:

| Bucket | Contains | Written as |
|---|---|---|
| **Where I stand** | Decisions the owner has made and intends to hold, with the one-line reason. | Statements, not questions. Include what a pushback must contain to change the answer. |
| **Ask them** | Only items passing the test below. | Numbered questions. **Hard cap ~8.** |
| **Assume they handle it** | Everything a competent pro does by default. | One dense scan paragraph, prefaced with "not quizzing you on this, but it has to show up in the quote." |

**A question earns a slot only if it is one of:**

- **Site-specific**: unanswerable without seeing our drawings, our bills, our roof.
- **A position to hold**: the answer is a decision the owner might be talked out of.
- **Expiring**: cheap now, expensive later.
- **A quiet upsell or a quiet corner-cut**: never comes up unless asked.

Everything else is hand-holding. Reciting standards at a tradesperson signals distrust, burns
minutes, and buries the questions that matter. Over ~8 questions, cut; don't reformat. A
30-question sheet is an unsorted one.

**Name the one question that matters most and say why**, one line under the list. It's what
the owner falls back on when the meeting runs short.

## Step 2: write it like a person

The failure mode is a doc that is correct and obviously machine-made. Fixes, by payoff:

- **Bottom line up front.** First three lines: what the meeting is, what to walk out with. No
  restating the background note.
- **Bold only what the eye should catch**: a number, a position, a deadline.
- **Kill decoration.** ✅/🚩 legends, emoji headers, "The Three Numbers" capital-letter framing.
- **A table needs two real columns.** A second column of sentences is a list in costume.
  Numbers, ranges and comparisons stay in tables; reasoning becomes prose.
- **Vary sentence length.** Follow a long sentence with a short one.
- **Short Anglo-Saxon words.** Use not utilise, start not commence, buy not procure. Cut just,
  really, simply, actually, basically.
- **Say it once.** A fact in the background note and the brief stays in one.
- **Contractions are fine.** This is the owner talking to themselves.
- **Em dashes: at most one or two on the page.** Most become a period.

## Step 3: standard shape

Adapt freely, but this order works:

```
Title, date, what this is                    2 lines
Walk out with:                               1 sentence, the artefacts
Link to the background note                  1 line; brief ≠ background
Where I stand                                3–5 bullets
The numbers to check their sums against      small table, only if there are numbers
Ask them                                     ≤8 numbered, + which one matters most
Time-critical / expires on <event>           the reason the meeting is now
Assume they handle it, flag if not           one paragraph + the 1–2 worth paying for
Bring                                        tick-boxes
Leave with                                   tick-boxes
Also worth saying out loud                   adjacent issues, things that aren't theirs to fix
Related                                      links back to the background notes
```

**Bring and Leave with survive contact with a real meeting.** Tick-boxes, kept last so a thumb
finds them.

## Step 4: check before handing over

Return to Step 1 on any fail.

- [ ] Count the questions. Over 8 → cut, don't merge.
- [ ] Every question passes one of the four tests. Any that don't → move to *Assume*.
- [ ] The first three lines alone say what to walk out with.
- [ ] Bold spans in the longest section ≤ ~5.
- [ ] Every fact traces to the background note or a source. Never invent a price, a
      standard, a lead time.
- [ ] Two pages or fewer at print size.
- [ ] One paragraph read aloud sounds like the owner.

Then cut generic framing and filler while preserving every fact, number, link, and owner-authored
word.

## Afterwards

- Fix inbound links: the parent `README.md` and the background note both describe the brief,
  and a question count or subtitle there goes stale the moment you cut.
- If a PDF was built from the old version, mark it stale in the README and offer to rebuild
  with the `markdown-to-pdf` skill. Don't rebuild unasked.
- After the meeting the brief is a record: append what they answered, don't overwrite the
  questions.
