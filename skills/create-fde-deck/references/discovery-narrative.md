# Discovery narrative

## Contents

- [Use it for](#use-it-for)
- [Workflow](#workflow)
- [Rules](#rules)
- [Skeleton](#skeleton)

Turn discovery into a decision, not a transcript summary.

## Use it for

Customer discovery synthesis, opportunity framing, an executive recap of interviews and workflow
observations, or deciding whether an opportunity is worth a validation step. Usually 5–7 slides.

## Workflow

1. Establish the audience, the decision, the workflow in scope and the time horizon. Ask for
   permissioned notes with dates, participant roles, the observed workflow and any contradictory
   observations.
2. Build the **evidence ledger** before any slide: claim, source locator, observed or inferred,
   confidence limits, counterexample. Repeated hearsay is one source, not several. Keep customer
   and participant identifiers out unless authorised.
3. Arc: current workflow → friction → impact → bounded opportunity → validation plan → decision.
4. Recommend the **smallest experiment that could disprove the opportunity**: baseline collection,
   success and stop criteria, an accountable owner and a target date. Missing commitments read
   `TBD — confirm`; never assign real people without authority.
5. Keep nuance and counterevidence in notes, but decision-changing caveats stay on the slide.
6. List unresolved evidence gaps outside the deck.

## Rules

| Bad | Required |
|---|---|
| "Search wastes 40% of operator time" with no timings collected | "Impact not yet measured" and a baseline step in the plan |
| A quote assembled from two interviews | Quotes only verbatim from a cited note, or no quote |
| Two operators who disagree merged into one finding | Both observations kept, the disagreement shown |
| "Customers want X" from one interview | Scope stated: "1 of 2 operators, 2026-08-02" |
| A stakeholder asks for a stronger story than the notes support | Keep the uncertainty; offer the experiment that would earn the stronger claim |

Never invent quotes, sample sizes, savings, benchmarks or customer names.

## Skeleton

Replace every placeholder; delete a slide rather than fill it with invented content.

```markdown
---
title: "Discovery: a decision to validate"
audience: Decision owner and workflow team
decision: Whether to run a bounded validation step
deck-type: discovery-narrative
---

<!-- shape: title -->
DISCOVERY / WORKING HYPOTHESIS

# Name the workflow friction worth investigating

State the audience and the decision this discovery should enable.

*Source: TBD — which notes, dates and participants this deck draws on*

---

<!-- shape: findings -->
01 / WHAT WE KNOW

## Separate observations from interpretation

- **Evidence** · An observed workflow step, in the participant's terms. *Source: TBD — locator, participant role, date*
- **Evidence** · A counterexample or unresolved disagreement. *Source: TBD — locator and scope*
- **Assumption** · The inference you draw from them, stated as unvalidated.

<!-- notes: what would disprove this framing? -->

---

<!-- shape: comparison -->
02 / THE OPPORTUNITY

## Compare a bounded intervention with the current path

**Proposal**

### Current workflow
Known steps, constraints and observed friction. Leave impact unquantified without a baseline.

### Smallest experiment
A reversible change, explicit non-goals, and the evidence that would invalidate it.

---

<!-- shape: findings -->
03 / WHAT TO TEST

## Design the next step to challenge the hypothesis

- **Proposal** · Collect a representative baseline before proposing an improvement target.
- **Proposal** · Agree success and stop criteria with the accountable team.

---

<!-- shape: next-steps -->
04 / THE ASK

## Ask for a specific learning commitment

- Confirm workflow scope and evidence gaps. Owner: TBD — decision owner. Date: TBD — agree date
- Review the baseline and decide whether to test. Owner: TBD — workflow lead. Date: TBD — agree date
```
