# Drill formats and question bank

## Contents

- [Scoring an answer](#scoring-an-answer)
- [Number defense](#number-defense)
- [Behavioral and STAR](#behavioral-and-star)
- [System walkthrough](#system-walkthrough)
- [Company-fit and interviewer persona](#company-fit-and-interviewer-persona)
- [Stakeholder simulation](#stakeholder-simulation)
- [Full mock](#full-mock)

Times are guides, not rules.

## Scoring an answer

| Verdict | Meaning |
|---|---|
| hire-signal | specific, quantified where supported, owns the decision, lands in 60–90 s |
| neutral | true but vague or team-level ("we did X"); push for *their* action |
| red-flag | rambles past 2 min, blames others, claims without backing, dodges the follow-up |

Follow-ups to keep ready: "what was *your* part?", "what would you do differently?", "how did you
measure that?", "what pushback did you get?", "what broke?".

## Number defense

Pick a stat off the resume ("where does +35% come from?"). Unprompted, they should produce:
**metric definition** → **baseline** → **intervention** → **measurement window and method** (A/B
test, dashboard, finance report) → **caveats** (seasonality, attribution). Check each step against
the number-source document and review records. Missing two or more steps: log it. Cannot name the
source at all: `TODO: verify`.

## Behavioral and STAR

Mine competency questions from the accomplishments log and review records. Coach to 60–90 s:
minimal Situation and Task, most of the time on *their* decision and Action, an observed Result;
quantify only when a record supports it. Always follow up.

Rotate competencies:

- Conflict: disagreement on scope or design; how it resolved, what shipped
- Failure: an incident or launch that went wrong; their part, the fix, the prevention
- Leadership without authority: driving cross-team work to done
- Ambiguity: a vague requirement turned into a shipped system; how they scoped it
- Craft: pushing for quality (tests, refactor, review) under delivery pressure
- Growth: the hardest feedback received and what changed after

## System walkthrough

Interview a system from the resume bullets. Descend until they hit a decision they personally made:

1. Draw the architecture in words.
2. Why this stack or shape versus the obvious alternative?
3. The hardest technical decision and the options considered.
4. Failure modes, and what the on-call page looks like.
5. At 10x load, what breaks first?
6. With hindsight, what would they redesign?

Good sign: trade-offs with numbers. Bad sign: only describes what exists, no "because".

## Company-fit and interviewer persona

Build the persona once per company from the target-company notes and role: likely style (formal or
conversational), what this hire must prove, deal-breakers they screen for, questions they ask
everyone. Play it consistently; a consultancy tech lead interviews differently from a startup CTO.

Shape questions by the company: a consultancy selling engineering practice → testing, TDD and
pairing philosophy; AI-enabled delivery → concretely how they use AI tooling day to day;
client-facing work → stakeholder stories. Drill "why us?" and prepare two or three questions for
the candidate to ask.

## Stakeholder simulation

For customer-facing or deployed-engineer hiring-manager rounds. The interviewer plays the hiring
manager *and* the customers they simulate: a security chief, a sceptical engineering director, a
CFO, a non-technical VP.

- Rotate personas without announcing them; 12–15 questions in 30 minutes.
- Interrupt any answer at its fourth sentence.
- Seed two questions whose answer is not public, to test the don't-know protocol: say what is
  known, what is not, and how they would find out.
- Score each answer 0–2 on answer-first, mechanism, provenance, length and honesty under pressure
  (10 points). Retry anything under 8.
- Product-specific cards, rubric and question bank come from the round's own prep notes in the
  company folder.
- Debrief: the score table plus three carries, logged in the company folder.

## Full mock

45–60 minutes, run like the real thing with realistic pacing and transitions:

1. Small talk and "tell me about yourself" (5 min; coach a 90 s arc: now → proof → why here)
2. Three or four behavioral questions, STAR, with follow-ups (20 min)
3. Two or three role-specific or technical questions off the resume (15 min)
4. One or two culture or motivation questions (5 min)
5. "Any questions for me?": the candidate asks two or three real ones (5 min)
6. Debrief: verdicts, top three fixes, practice-log entries
