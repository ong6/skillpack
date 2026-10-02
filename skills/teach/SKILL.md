---
name: teach
description: Create a stateful, multi-session course in the learning workspace. Use only when the user invokes teach or asks to start structured learning of a topic. Explicit-only; not for one-off explanations or research reports.
---

# Teach Topic

A stateful request: the user intends to learn this topic over multiple sessions. Treat the current
directory (`learning/<topic>/`) as the workspace.

## Workspace files

- `MISSION.md`: why the user wants this. Grounds every teaching decision. Format: [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `RESOURCES.md`: vetted knowledge sources and communities. Format: [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `GLOSSARY.md`: the workspace's canonical terms, adhered to in every lesson. Format: [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `learning-records/0001-<dash-case>.md`: ADR-style records of what the user demonstrably knows; the input to the ZPD estimate. Format: [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `lessons/0001-<dash-case>.html`: one self-contained HTML lesson each, the primary unit of teaching.
- `reference/*.html`: compressed learnings (cheat sheets, syntax, algorithms, poses, routines) built for quick reference and printing.
- `NOTES.md`: the user's stated teaching preferences and your working notes.

The user never maintains these files. Create directories lazily.

## Philosophy

Deep learning needs **knowledge** (from high-trust resources), **skills** (interactive lessons
built on that knowledge), and **wisdom** (real-world practice with other practitioners). Until
`RESOURCES.md` is well populated, finding high-quality sources is the priority. Never teach from
parametric knowledge.

**Storage strength over fluency.** Fluent in-the-moment retrieval feels like mastery and isn't.
Design for long-term retention through desirable difficulty: retrieval practice, spacing, and
interleaving (skills practice only). For acquiring knowledge, difficulty is the enemy; it eats
working memory. For building skills, difficulty is the tool.

## Session shape: probe, then plan, then teach

Never open by producing. Open by measuring. Phases 1 and 2 are cheap compared to teaching the
wrong node.

### Phase 1: probe

Quiz before you teach. Start broad, then binary-search the edge of understanding on every strand
the lesson depends on, one question per strand, until you find where knowing stops. Two or three
rounds of a few questions is usually enough; the output is a map, not a score.

- Always offer **"I don't know"** and say it is the correct answer when true. A lucky guess corrupts
  the ZPD estimate for every later session.
- If `learning-records/` already pins a strand, read it, don't re-probe.
- Invite front-loading: "tell me what you already know and I'll skip ahead."
- Probe results that change the picture become a learning record.

### Phase 2: plan

Produce a **mermaid dependency graph** from where they are to the lesson's target: nodes are
concepts, edges are prerequisites, nodes the probe showed they hold are marked. Put it at the top
of the lesson. Draw it every time, even for a topic you think you know; you cannot draw it without
working out what depends on what.

**Fan out verification subagents** in parallel (the host's own subagent mechanism) to fact-check
every claim the lesson will make and find the primary source. One confidently wrong explanation
costs more than the session gained.

### Phase 3: teach

- **One reasoning step per message.** Walk the graph node by node and stop. Dumping the whole chain
  reads as understanding and produces none, even when the user seems to be following.
- **Quiz periodically regardless of style.** A fluent AI makes it easy to feel you understood.
  Quizzes recalibrate the ZPD and force the retrieval that builds storage strength.
- `NOTES.md` preferences override the style of this phase, never the pacing rule or the quizzing.

### The load rule

All difficulty goes into the material. Absorb everything else: logistics, sequencing, finding and
vetting resources, deciding what comes next, formatting, file management. Difficulty in the
harness is a defect.

## Mission

If `MISSION.md` is empty or the user is unclear, interview them on why before anything else.
Without it, lessons go abstract and you have no way to judge what comes next. Missions change;
confirm with the user, update `MISSION.md`, and add a learning record.

## Zone of proximal development

Each lesson should feel challenged "just enough". If the user hasn't named what to learn, read the
learning records, pick the most mission-relevant thing that fits the ZPD, teach that.

## Lessons

- Short and quickly completable (working memory is small), one tangible win, tied to the mission,
  inside the ZPD.
- Knowledge first, only what the skill needs, then practice through an interactive feedback loop
  that is as tight and automatic as possible (quizzes, light in-browser tasks, or a guided list of
  real-world steps).
- Cite external sources for every claim.
- Beautiful: clean typography and layout, Tufte-like, since the user returns to review.
- Anchor-link to other lessons and reference documents; recommend one primary source to read or
  watch; remind the user to ask follow-up questions.
- **Quiz answers all the same number of words** (and characters where possible). No formatting
  clues.
- Before delivering lessons and reference documents, remove generic filler, preserve all sourced
  facts and links, and open the file with a CLI command if possible.

## Reference documents

Lessons are rarely revisited; reference documents are. Create them alongside lessons as the
compressed essence in quick-reference form: syntax and snippets, algorithms and flowcharts, poses
and sequences, exercises and routines, glossaries. The glossary is essential for any topic with its
own nomenclature.

## Wisdom

When a question needs real-world experience, answer it, then delegate to a **community** (forum,
subreddit, local class or interest group). Find high-reputation ones; if the user has opted out of
communities, respect it and note it in `RESOURCES.md`.
