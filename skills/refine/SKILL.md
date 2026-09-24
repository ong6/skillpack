---
name: refine
description: Explicit-only. Improve the latest deliverable (draft, code, plan, note, design) through a loop of fresh independent reviewer agents that pick task-fit metrics, score it out of 10 and return feedback, refining until it scores 8+ or three rounds pass. Use for "/refine", "refine this", "run the refine loop", "auto-improve this". Not for a single quick edit, a PR or diff review (code-review), or feedback about agent behaviour (feedback-loop).
---

# Refine

Improve the current deliverable with a reviewer that did not write it. The main agent refines;
fresh reviewer agents score. Never score your own work and call it independent.

## Setup

1. **Target.** The argument names it; otherwise take the most recent deliverable in the
   conversation (a file you wrote, a draft in chat, a diff). Unclear between two → pick the latest
   and say so in one line.
2. **Brief.** Write a short brief for reviewers: the owner's goal, audience, and every explicit
   constraint they gave (length, tone, must-keep items). Constraints outrank reviewer taste.
3. **Threshold.** Default 8. A number in the argument (`/refine 9`) replaces it. Cap: 3
   refinement rounds.

## Loop

```
review v0 → score ≥ threshold? stop : refine → review v1 → … (max 3 refinements)
```

Every refinement gets its own review, so the final score is always measured.

**Review.** Spawn a **fresh** subagent each round (Claude Code: the Agent tool; Codex: its native
subagent mechanism). Pass only the brief, the artifact (verbatim or its path) and, from round 2,
the frozen rubric. Never pass your reasoning, earlier drafts, or earlier feedback. If the host has
no subagent mechanism, say so and stop; don't fall back to self-review. Reviewer prompt:

> You are an independent reviewer. Do not edit files, launch agents, or rewrite the artifact.
> Read-only checks (running tests, linters, opening links) are allowed.
> Round 1 only: choose 3–6 metrics that decide quality **for this task and audience**, with
> weights summing to 100. Later rounds: use the given rubric unchanged.
> Score each metric 0–10 with a short quote or line reference as evidence. Overall = weighted mean,
> one decimal. If overall < {threshold}, list the fixes that would raise it most, highest impact
> first, each concrete enough to act on. Flag anything that breaks a brief constraint as critical.
> Return: rubric table, overall score, critical issues, ranked fixes.

**Refine.** Apply the fixes in rank order. Skip a fix that contradicts the brief and note why.
Change what the feedback targets; don't rewrite unrelated parts or chase polish past it.

**Guardrails.**
- Keep the best-scoring version. If a round scores lower, revert to the best one and try the next
  fix set, or stop if it was the last round.
- Stop early when two rounds move the score by < 0.5; the reviewer signal is noise now.

## Report

End with the final artifact (or its path) and a compact table:

| Round | Score | Top fixes applied |
|---|---|---|

Then one line: stop reason (threshold met / 3 rounds / plateau), and any fix you declined with why.
Under 8 after the cap → say so plainly and name the one issue still holding it back.
