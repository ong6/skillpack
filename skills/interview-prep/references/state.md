# State: vocabulary and file formats

## Contents

- [Element ids](#element-ids)
- [Marks and verdicts](#marks-and-verdicts)
- [bank.md](#bankmd)
- [rep-log.md](#rep-logmd)
- [interviews/](#interviews)
- [practice-log.md](#practice-logmd)

Everything is plain Markdown in the state folder: readable, editable, deletable with `rm -rf`. No
database, no scheduler, no queue file. What is due is recomputed from `bank.md` by
`scripts/due.py`, so nothing can drift out of sync.

## Element ids

One global vocabulary for plan grading, the bank and interview debriefs. Global, not per-pattern,
so the bank can show `base-case` missing on five structurally unrelated patterns. Each
`references/pattern-*.md` lists the subset it requires in `required_elements`.

| id | The probe it answers |
|---|---|
| `problem-restated` | Did they restate the problem and its return shape before planning? |
| `discriminator` | Did they name the property that selects this pattern, not just the pattern? |
| `state-definition` | Is the tracked thing defined exactly: index, count, set, table cell? |
| `invariant` | What is true at every step, and what restores it when it breaks? |
| `base-case` | Which entries are seeded, with what value, before the loop runs? |
| `transition` | Is the recurrence or update rule a formula, not "then I update it"? |
| `iteration-order` | Why this order: what must already be computed at each step? |
| `boundary-update` | How does each pointer, window edge or bound move, and why does it terminate? |
| `termination` | What ends the loop or recursion, and why can it not run forever? |
| `dedup` | How are repeats, revisits or already-seen states excluded? |
| `complexity-target` | Was a time and space target stated before coding, with the brute force named? |

## Marks and verdicts

Per required element, from the plan as first stated:

| Mark | Rule |
|---|---|
| **present** | You can quote their own words stating it, specifically enough to implement from. |
| **vague** | They gestured at it. "I'll build up the table" is a vague `transition`. |
| **missing** | No quotable span. |

No quote, not present. Write the quoted span beside each mark before deciding the verdict; grading
from an impression of the conversation drifts into rewarding confidence. Calibrate against the
pattern file's complete-versus-vague columns.

| Verdict | When | Next due |
|---|---|---|
| `failed` | wrong pattern, or any required element missing | +3 days |
| `half` | right pattern, all present, one or more vague | +3 days |
| `coded` | all present and the code ran | +14 days |
| `named-clean` | all present on the first statement, unprompted | +14 days |

A prompted recovery does not change the verdict: it records what they produced unprompted, which is
what an interview measures. Intervals are tunable (`due_failed_days`, `due_clean_days` in the
rep-log frontmatter); they come from one person's search, not a study.

## bank.md

Append-only pipe table, one row per graded rep or failed interview question. Write `due` at grading
time. `missing` is comma-separated element ids, or `-`.

```markdown
| date | pattern | verdict | missing | due | notes |
|---|---|---|---|---|---|
| 2026-08-27 | monotonic-stack | half | iteration-order | 2026-08-30 | proposed a stack of end times, needed a min-heap; said O(n), it was O(n log n). Regression from named-clean 08-19. |
```

The notes cell is prose on purpose: what broke in the reasoning and what it regressed from. Never
write the problem statement or a paraphrase of it.

## rep-log.md

```markdown
---
target_date: 2026-12-31   # the search ends; stop suggesting reps after it
tone: neutral             # neutral | blunt
due_failed_days: 3
due_clean_days: 14
---

## Live carries
- asks the value range before choosing a search bound (missed 3 sessions)

| date | minutes | reps | notes |
|---|---|---|---|
| 2026-08-27 | 24 | 3 | two-pointers, sliding-window, dp-1d |
| 2026-08-28 | 45 | 1 | timed round 7/10 FAIL: predicate direction unstated |
| 2026-08-29 | MISSED | 0 | travel |
```

- **Live carries**: at most five specific habits to re-test. Pick each problem so it tests one;
  clear a carry when a rep shows it fixed unprompted, add one when a rep exposes it.
- A day counts only if the minutes cell has a digit and does not say `MISSED`. Day boundary is 3am.
- The floor is 20 minutes and a 20-minute day counts. A missed day is logged as `MISSED`; no
  make-up doubling, because a doubled target costs the next three days.

## interviews/

`interviews/<date>-<company-slug>.md`, one per real or mock interview. The slug is whatever the
candidate calls the company.

```yaml
---
date: 2026-09-14
kind: real            # real | mock
round: phone-screen   # phone-screen | onsite | final | take-home | behavioral | system-design
outcome: rejected     # passed | rejected | pending | withdrawn
asked:
  - pattern: monotonic-stack     # pattern id, or a short topic for non-DSA questions
    result: failed               # solved | partial | failed
    broke_on: [iteration-order, complexity-target]
  - pattern: graph-bfs
    result: solved
    broke_on: []
---
```

Below the frontmatter, the candidate's own words: what was asked, what broke, what they would say
differently. Never rewrite or summarise them.

## practice-log.md

Dated entries for non-DSA drills. `TODO: verify` items are the next session's first job: find the
source or drop the claim.

```markdown
## 2026-09-14: number defense + STAR
- Weak: "conflict with PM" story rambled (2.5 min); retry next session
- TODO: verify: claims on-call MTTR halved; not in reviews or the number source
- Strong: revenue-impact narration tight and sourced
- Ask them: how do delivery teams split frontend and backend ownership?
```
