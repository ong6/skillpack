# Technical architecture

## Contents

- [Use it for](#use-it-for)
- [Workflow](#workflow)
- [Rules](#rules)
- [Skeleton](#skeleton)

Explain a system's responsibilities and boundaries before naming products.

## Use it for

Solution architecture decks, integration proposals, data-flow explanations, security-boundary
reviews and technical trade-off presentations. Usually 5–8 slides: decision framing, constraints,
architecture, boundary and failure findings, alternatives, validation steps.

## Workflow

1. Identify the audience, the decision, existing systems, constraints, the identity model, the
   deployment boundary and non-goals. Ask for the missing constraints that would change the
   design; mark the rest as assumptions.
2. Build the **fact inventory**: each supplied fact with a source locator and date, and each
   component marked existing, proposed or unknown.
3. Trace **one representative request end to end**: caller, identity, authorisation, data
   retrieval, processing, response, audit. Cover sensitive data movement, retention, deletion,
   tenant separation and external egress, and name the component that enforces each boundary.
4. Draw the flow as a linear `architecture` slide of at most five stages (three or four reads
   best): `1. **Stage** — responsibility and trust boundary`. Branches, async paths and failure
   routes (queues, dead letters, retries) get their own slide; adjacency on a slide must never
   imply an integration nobody verified.
5. Compare viable alternatives, including the current approach, on the same criteria: security,
   operational ownership, failure handling, reversibility, effort, cost assumptions. Say why the
   recommendation is conditional.
6. State timeout, retry, idempotency, fallback or abstention, observability and rollback behaviour
   where relevant. Missing access enforcement is a **blocking design gap** on a slide, not prose.
7. Close with validation actions (owner, date) and one specific approval request.

## Rules

| Bad | Required |
|---|---|
| "Sub-100 ms p95" with no workload data | "Latency target: proposal; workload volumes unknown" |
| "SOC 2 compliant" inferred from a vendor logo | Certifications only from a cited document, else unknown |
| Retrieval before the authorisation check in the flow | Authorise tenant and role before any data is read |
| A fork drawn as a straight line to fit the shape | Main path on one slide, the branch and failure path on the next |
| "Integration tested" with no test run | "Integration not yet tested" plus a validation action |

Stage names under about 35 characters and details under about 180; with five stages, details under
120 or split. Two options compare best (55 words each at most); three options, 35 words each.

## Skeleton

```markdown
---
title: "Architecture: boundaries before integrations"
audience: Platform, security and delivery owners
decision: Approve a testable design for review
deck-type: technical-architecture
---

<!-- shape: title -->
ARCHITECTURE / PROPOSAL

# Define the decision the design must support

Name the workload, the trust model and the non-goals.

*Source: TBD — supplied constraints, with dates*

---

<!-- shape: findings -->
01 / CONSTRAINTS

## Make unverified constraints explicit

- **Assumption** · Data classification, identity and authorisation requirements. *Source: TBD — security owner*
- **Assumption** · Latency, capacity, availability and cost needs, with no invented guarantees. *Source: TBD — workload evidence*

---

<!-- shape: architecture -->
02 / REQUEST FLOW

## Assign a responsibility to every boundary

1. **Caller** — authenticate identity; define caller trust
2. **Access boundary** — authorise tenant and role before data retrieval
3. **Processing** — scope data; define timeout and fallback
4. **Response and audit** — expose provenance; minimise retained data

*Source: Proposal — validate against the actual system contracts*

<!-- notes: retention and deletion, retry and idempotency, monitoring, rollback. Branches go on the next slide. -->

---

<!-- shape: comparison -->
03 / TRADE-OFFS

## Compare options against the same constraints

### Current approach
Operating ownership, security boundaries, failure recovery and constraints, from evidence.

### Proposed change
Benefits as hypotheses, integration obligations, failure modes, reversibility, validation gaps.

---

<!-- shape: next-steps -->
04 / VALIDATION

## Approve a testable design, not an implied guarantee

- Review identity, tenant boundary, retention and failure cases. Owner: TBD — security lead. Date: TBD — agree date
- Validate contracts and workload assumptions before implementation. Owner: TBD — platform lead. Date: TBD — agree date
```
