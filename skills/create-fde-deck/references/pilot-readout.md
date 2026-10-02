# Pilot readout

## Contents

- [Use it for](#use-it-for)
- [Workflow](#workflow)
- [Rules](#rules)
- [Skeleton](#skeleton)

Report what changed, what is still unknown, and what decision the evidence permits.

## Use it for

Proof-of-concept readouts, pilot scorecards, executive outcome reviews, evaluation summaries and
go/no-go recommendations. Usually 5–7 slides: decision headline, pilot scope, measured outcomes,
failures and limitations, alternatives or gates, next steps. When the pilot is kept with the
track-pilot-evidence skill, build only from its customer-safe handover, never from internal records.

## Workflow

1. Gather the original hypothesis, the pre-agreed success and stop gates, baseline, cohort, sample
   size, time window, exclusions, measurement method, operating cost and incidents. Separate actual
   results from targets and forecasts before writing a slide.
2. Build the **measurement ledger**: metric, numerator and denominator, unit, baseline, observed
   value, window, source, uncertainty, caveat. Ask for missing denominators; absent data is
   `Not measured`, never zero.
3. Check comparability: cohort shifts, cherry-picked tasks, missing failures, different windows and
   manual assistance can each invalidate an apparent gain. No causal or population-wide claim from
   an uncontrolled or small pilot. Show any computed change's formula and inputs in notes.
4. Give unfavourable evidence equal visibility when it changes the decision.
5. Recommend a **bounded** outcome: stop, extend, or expand to a named cohort, paired with security
   and quality gates, accountable owners, rollback criteria and a review date. An unauthorised
   disclosure or an unmet hard safety gate stays a visible blocker.
6. Verify every number against the ledger; list unresolved gaps outside the deck.

## Rules

| Bad | Required |
|---|---|
| "Success rate up 15%" (60% → 75%) | "Up 15 percentage points (25% relative)", and whether the cohorts match |
| "2x faster" with no matched baseline | "Speed-up not measured: no matched manual baseline" |
| "Statistically significant", "ROI 4x" with no study design or cost data | Neither claim; request sample and cost evidence |
| 32/40 shown as "strong accuracy" against a 90% gate | "32 of 40 (80%), Aug 1–7; 90% gate not met" |
| Disclosure failures moved to notes | Blocker on the outcome slide and in the recommendation |
| A positive demo presented as production readiness | Readiness only with its gates met and cited |

Result slides hold two or three metrics (four at most: value under 18 characters, label under 70,
source under 120). Keep the unit with the value and the baseline, sample and window visible in the
label or source, not only in notes. Split a dense ledger across slides rather than hide them.

## Skeleton

```markdown
---
title: "Pilot readout: evidence before expansion"
audience: Pilot sponsor and operating owners
decision: Stop, extend, or expand to a named cohort
deck-type: pilot-readout
---

<!-- shape: title -->
PILOT / READOUT

# State the bounded decision the pilot supports

Do not imply a positive outcome until the data supports it.

*Source: TBD — pilot protocol and results, with dates*

---

<!-- shape: findings -->
01 / TEST SCOPE

## Define what was tested and what was excluded

- **Assumption** · Cohort, baseline, measurement window, task selection, manual assistance. *Source: TBD — experiment protocol*
- **Assumption** · The pre-agreed success and stop gates; mark any set after the fact. *Source: TBD — signed pilot criteria*

---

<!-- shape: results -->
02 / OUTCOMES

## Report measured outcomes with their limits

| Value | Metric | Source |
|---|---|---|
| Not measured | Primary metric · baseline and window unknown | Source: TBD — sample, method, exclusions |
| Not measured | Quality or safety gate · denominator unknown | Source: TBD — evaluation rubric, failure review |

<!-- notes: replace only with verified values; show calculations; percentage points versus relative change. -->

---

<!-- shape: findings -->
03 / LIMITATIONS

## Keep failure modes in the decision

- **Assumption** · Failures, adverse outcomes and unrepresentative cases, not hidden in notes. *Source: TBD — incident and evaluation evidence*
- **Proposal** · No causal, statistical, ROI or production-readiness claim the design cannot support.

---

<!-- shape: next-steps -->
04 / NEXT DECISION

## Choose stop, extend, or bounded expansion

- Resolve evidence gaps and unmet hard gates before expansion. Owner: TBD — pilot owner. Date: TBD — review date
- Approve cohort, rollback criteria and the operating owner. Owner: TBD — sponsor. Date: TBD — agree date
```
