---
name: interview-prep
description: >-
  Run interview practice grounded in the candidate's own resume and target-company notes: mock
  interviews, behavioral STAR answers, number defense, walkthroughs of systems they built,
  stakeholder simulations, reference system-design walkthroughs, timed DSA coding rounds and plan
  reps graded and scheduled by due pattern, and debriefs of real interviews that queue what broke.
  Use for "interview prep", "mock interview", "run a DSA rep", "give me a rep", "what's due",
  "walk me through a system design", "I just had an interview", "log my onsite"; not for editing a
  resume or cover letter, finding or applying to jobs, answering recruiters, or building a
  customer presentation.
---

# Interview prep

Coach from the candidate's own records. Every question anchors to something they did; never invent
history, and never polish a claim you cannot trace to a record.

## 1. State and context

**State lives in one folder:** `$INTERVIEW_PREP_HOME` when set, otherwise the interview-prep folder
the host repo's agent manual names. The manual may map any file below onto one it already keeps.

| Path | Holds |
|---|---|
| `bank.md` | one append-only row per graded DSA rep or failed interview question, with its due date |
| `rep-log.md` | settings, Live carries (max five), one row per practice day |
| `practice-log.md` | dated notes from non-DSA drills, including `TODO: verify` items |
| `interviews/` | one file per interview sat, real or mock |
| `companies/<slug>/` | company-specific scripts, round formats, questions and feedback |
| `practice/` | timed-round buffers |

Formats and the shared element vocabulary: [references/state.md](references/state.md). No folder
yet: ask where to create it, and never inside a repo with a public remote (`git remote -v`). It will
hold a resume, a target list and a record of weaknesses; on an employer-managed machine, suggest a
personal volume. Past `target_date` in `rep-log.md`, stop suggesting reps.

**Context.** Before any non-DSA drill, read what the host repo's manual points to:

1. The target company's notes: role, process stage, what the hire must prove. None for this
   company: ask which company and role, and have them recorded before drilling.
2. The resume actually sent to that company: a retained snapshot if the sources changed since. For
   an unsent application, the prepared version, labelled prepared.
3. Evidence, in order: the story bank, standing Q&A, the topic notes for this round type, the
   accomplishments log, performance-review records, and the document that sources every resume
   number (the number-defense answer key). Reuse existing defense prep.

The manual names none of these: ask for the resume and the role, and drill only from what they give.
DSA reps read `bank.md`, `rep-log.md` and the pattern references only, never the resume.

## 2. Pick a drill

The candidate chooses, or suggest by stage: early screen → company-fit and "tell me about
yourself"; technical rounds booked → number defense, system walkthrough, system design, DSA;
behavioral or final round → STAR; an interview just happened → debrief. A session runs 30–45 min.
Formats, scoring and question banks: [references/drill-formats.md](references/drill-formats.md).

- **Number defense.** Pick a resume stat; they narrate its provenance (system, method, window,
  baseline). Check it against the answer key; log any number they cannot back.
- **Behavioral / STAR.** Questions mined from the accomplishments log and reviews, coached to
  60–90 s with most time on *their* decision. Always follow up.
- **System walkthrough.** Interview a system from their resume down the probe ladder until they
  reach a decision they personally made.
- **Company-fit.** Questions shaped by the company notes and an interviewer persona; drill "why
  us?" and prepare two or three questions for them to ask.
- **Stakeholder simulation.** For customer-facing hiring rounds: rotating unannounced personas,
  interrupts, two unanswerable questions to test the don't-know protocol, 0–2 scoring per answer.
- **Full mock.** 45–60 minutes end to end, then a debrief.
- **System design**: section 5. **DSA**: section 4. **Debrief**: section 6.

## 3. Coaching stance

- **Timed drills use the real clock.** Record the end time with `date`, set background alerts for
  five minutes left and time up, and compute time left from `date` before every interviewer turn.
  Never decrement a guessed amount per reply.
- Sceptical interviewer, not cheerleader: interrupt rambles, ask the obvious follow-up, refuse "we
  improved performance" until you get an observed result and the mechanism. A number is optional
  when none exists.
- After each answer: a one-line verdict (hire-signal, neutral, red-flag), then the one or two fixes
  that matter most. Model answers only after they have attempted.
- An unbacked assertion gets `TODO: verify` in the practice log, not polish.
- Tone is neutral unless `rep-log.md` sets `tone: blunt`.

## 4. DSA reps

Start every rep with the queue, run from this skill's folder (stdlib only):

```bash
python3 scripts/due.py "$INTERVIEW_PREP_HOME"   # or the state folder path
```

It prints the next pattern (overdue Tier A, overdue Tier B, never drilled, then most failed in 30
days, never the previous row's pattern), the due list, and which plan element went missing most in
60 days. Pick a problem in that pattern that also tests a Live carry. Procedure, timed-round spec and
grading layout: [references/dsa-reps.md](references/dsa-reps.md).

- **Plan rep** (20 minutes is complete): generate the problem from the pattern's discriminator,
  ask for the plan in words before code, and mark each required element present, vague or missing
  with the quoted span. No quote, not present.
- **Timed round** (45 minutes): sparse prompt, clarification, design, full code in a plain-text
  buffer, hand dry-run, a requirement-changing follow-up, close, then re-install. Five axes, 0–2.
- **Never** name the pattern before grading, reuse a known problem's title or setup, or write the
  generated problem to disk.
- After time, run their code and a fresh reference solution:
  `python3 scripts/run_cases.py solution.py cases.json` (files in a temp dir, never the state folder).
- Grade in chat. Append the `bank.md` row with its due date (`failed`/`half` +3 days,
  `coded`/`named-clean` +14), the `rep-log.md` row, and update the Live carries.
- When `due.py` reports one element missing on three or more different patterns, say so once:
  it is the one cross-session claim worth interrupting for.

Pattern references (discriminator, confusables, required elements with complete-versus-vague
statements, failure modes, template):

- Tier A: [two-pointers](references/pattern-two-pointers.md),
  [sliding-window](references/pattern-sliding-window.md),
  [binary-search-on-answer](references/pattern-binary-search-on-answer.md),
  [hashing](references/pattern-hashing.md), [graph-bfs](references/pattern-graph-bfs.md),
  [graph-dfs](references/pattern-graph-dfs.md), [dp-1d](references/pattern-dp-1d.md),
  [heap-top-k](references/pattern-heap-top-k.md)
- Tier B: [prefix-sum](references/pattern-prefix-sum.md),
  [monotonic-stack](references/pattern-monotonic-stack.md),
  [intervals](references/pattern-intervals.md),
  [linked-list-pointers](references/pattern-linked-list-pointers.md),
  [topological-sort](references/pattern-topological-sort.md),
  [union-find](references/pattern-union-find.md),
  [backtracking](references/pattern-backtracking.md), [dp-2d](references/pattern-dp-2d.md)

## 5. System-design walkthrough

Reference designs: [url-shortener](references/design-url-shortener.md),
[rate-limiter](references/design-rate-limiter.md),
[notification-system](references/design-notification-system.md),
[twitter-feed](references/design-twitter-feed.md),
[whatsapp-chat](references/design-whatsapp-chat.md),
[video-streaming](references/design-video-streaming.md),
[uber-dispatch](references/design-uber-dispatch.md),
[distributed-kv-store](references/design-distributed-kv-store.md).

Take the one named, or pick one that matches the target role. Walk it in file order: requirements,
capacity, high-level architecture, API, storage, deep dives, trade-offs, curveballs. At each section
the candidate answers first; reveal the reference only after, then name the gap. Draw in Mermaid or
text when a diagram helps. A walkthrough is not a rep (it has no falsifiable unit), so it never
enters `bank.md` or `rep-log.md`; note weak sections in `practice-log.md`.

## 6. Interview debrief

Run it the same day: recall of *why* an answer broke fades within hours.

1. Take the account, in order, and stop when you have it; do not interrogate someone just
   rejected. Date, round, real or mock, outcome (`pending` is normal). Per question: the pattern or
   topic it wanted, and solved, partial or failed. Per question that broke: "What did you say you
   were going to do, and what was wrong with it?"
2. Map each break onto element ids from [references/state.md](references/state.md#element-ids).
   Nothing fits: leave `broke_on: []` and keep the reason in prose. Do not force a fit.
3. Write `interviews/<date>-<slug>.md` with the schema's frontmatter and their own words below it,
   never rewritten or summarised.
4. Every DSA question with `failed` or `partial` becomes a `bank.md` row dated the interview date:
   verdict `failed`, `missing` = its `broke_on`, due three days after the interview, the note
   marked as a real interview. A real failure is better evidence than a practice one, so it is
   scheduled the same way.
5. Non-DSA questions that broke go to `companies/<slug>/` and become the first drill of the next
   practice session.
6. Close by naming what entered the queue and when. If an element already appears in the bank, say
   so with dates: "this is the third time `base-case` has been the thing."

## 7. Log the session

- Non-DSA drills: a dated entry in `practice-log.md` ([format](references/state.md#practice-logmd)).
  Resolve `TODO: verify` items first next session: find the source or drop the claim.
- Company-specific scripts, round formats, questions and feedback go in `companies/<slug>/`,
  linked from the company notes. Reusable rehearsal results go in `practice-log.md`.
- Keep pages short: one screen of current answer, detail split by question. Replace a superseded
  script instead of appending to it. Preserve the candidate's factual claims and voice.
- If prep shows the resume needs changing, say what and hand it to the host's resume workflow;
  do not edit the resume here.
- No LaTeX math delimiters anywhere; put variables and complexities in backticks.
