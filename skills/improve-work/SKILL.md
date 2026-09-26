---
name: improve-work
description: >-
  Explicit-only. Improve the latest deliverable (draft, code, plan, note, design)
  through fresh independent reviewer agents until it meets the requested score
  and all explicit constraints, or three refinement rounds pass. Use for "/improve-work",
  "refine this", "run the refine loop", "auto-improve this". Not for a single quick
  edit, a PR or diff review (code-review), or feedback about agent behaviour
  (apply-feedback).
---

# Improve Work

Improve the current deliverable with a reviewer that did not write it. The main agent refines;
fresh reviewer agents score. Never score your own work and call it independent.

## Setup

1. **Target.** The argument names it; otherwise take the most recent deliverable in the
   conversation (a file you wrote, a draft in chat, a diff). Unclear between two → pick the latest
   and say so in one line.
2. **Brief.** Write a short brief for reviewers: the owner's goal, audience, and every explicit
   constraint they gave (length, tone, must-keep items). Constraints outrank reviewer taste.
3. **Threshold.** Default 8 out of 10. A number in the argument (`/improve-work 9`) replaces it.
   Cap: 3 refinements after the initial review; each changed artifact must then be reviewed.
4. **Snapshots.** Preserve the initial artifact and every reviewed version. Bind each review's
   rubric, score, constraint checks, critical issues and fixes to that exact version. Restoring
   a snapshot restores its own review; an edit creates an unreviewed version.

## Loop

```
review v0 → eligible and score ≥ threshold? stop : refine → review v1 → …
```

**Review.** Spawn a **fresh** subagent each round using the host's native mechanism with no
inherited conversation. Pass only the brief, the exact artifact (verbatim or an immutable path)
and, after round 1, the frozen rubric. Never pass your reasoning, earlier drafts or feedback.
If the host cannot provide a fresh reviewer, say so and stop; don't fall back to self-review or
launch another AI CLI. Reviewer prompt:

> You are an independent reviewer. Do not edit files, launch agents, or rewrite the artifact.
> Read-only checks (running tests, linters, opening links) are allowed.
> Round 1 only: choose 3–6 metrics that decide quality **for this task and audience**, with
> weights summing to 100. Later rounds: use the given rubric unchanged.
> Score each metric 0–10 with a short quote or line reference as evidence. Overall = weighted mean,
> one decimal. Check every explicit brief constraint separately, with evidence and pass/fail/unknown.
> Flag a violated constraint as critical. An unknown required check is unresolved, not a pass.
> If overall < {threshold}, any critical issue exists, or a required check is unresolved, list the
> fixes that would help most: critical and unresolved constraints first, then quality, each concrete
> enough to act on. A high score never cancels a critical issue.
> Return: artifact version, rubric table, overall score, constraint checks, critical issues, ranked fixes.

**Decide.** A reviewed version is **eligible** only when it has no critical issues and every
explicit constraint passes. Stop successfully only if that same version is eligible and its
own score meets the configured threshold. A score above threshold with a broken constraint
still needs refinement. Missing checks or a review of different bytes cannot establish success.

**Refine.** Address critical and unresolved constraints before lower-priority polish. Skip a fix
that contradicts the brief and note why. Change what the feedback targets; don't rewrite unrelated
parts. Submit every changed version for a fresh review before reporting its score or success.

**Retain and stop.**
- Keep the highest-scoring **eligible reviewed** version; on a tie prefer the earlier one. A
  higher-scoring ineligible version never displaces it. If a refinement regresses, restore that
  eligible snapshot and its own review before trying another fix set or reporting.
- If none is eligible, keep snapshots for recovery and work on the unresolved constraints within
  the cap. At the cap, retain the last reviewed version as an explicitly incomplete draft and
  list its failures; never describe it as accepted or successfully refined.
- Stop after 3 refinements, or early when two consecutive score changes are each less than 0.5
  **and all three compared versions are eligible**. Unresolved critical issues are not a quality
  plateau. At either stop, select the best eligible version and evaluate success against its own
  score and the configured threshold. If a required repair cannot be made, report the blocker.

## Report

End with the retained artifact (or its path) and a compact table:

| Version | Score | Constraint status | Top fixes applied |
|---|---|---|---|

Identify the retained version, its measured score, the configured threshold and whether it met
both acceptance conditions. Give the actual stop reason (threshold met / 3 refinements / plateau /
blocked review or repair), remaining issues, and any fix declined with why. If the retained score
is below the requested threshold, say so even when it is above 8. Never attach the last attempted
version's score to an earlier restored artifact.
