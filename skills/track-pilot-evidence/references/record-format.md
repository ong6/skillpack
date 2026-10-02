# Pilot record format

## Contents

- [Layout](#layout)
- [Sections](#sections)
- [Example](#example)
- [Using the datastore skill instead](#using-the-datastore-skill-instead)

## Layout

```text
<pilots folder>/<pilot-slug>/
  pilot.json        the whole record; scripts/pilot.py reads and writes it
  attachments/      files the evidence cites, verified by SHA-256
  handover-*.md     customer-safe handovers written by `pilot.py handover`
```

Dates are `YYYY-MM-DD`. Every record has an `id` unique across the whole file (`c-`, `e-`, `a-`,
`r-`, `d-`, `h-` prefixes read well) and a `visibility` of `internal` (the default) or `customer`.

## Sections

| Section | Fields | Notes |
|---|---|---|
| `charter` | `customer`, `title`, `objective`, `owners`, `start`, `end`, `internal_notes` | `internal_notes` never leaves the full view |
| `criteria` | `id`, `name`, `metric`, `baseline`, `threshold`, `target_date`, `owner`, `visibility` | all required; no `status` field: status comes from the latest human review |
| `evidence` | `id`, `name`, `summary`, `source`, `owner`, `collected`, `stale_after_days` (1–3650, default 30), `criteria` (ids), `visibility` | an observation, not a verdict |
| `attachments` | `id`, `evidence` (id), `path` (relative, inside the pilot folder), `sha256`, `bytes`, `added`, `visibility` | shown to the customer only when its evidence is too |
| `risks` | `id`, `name`, `detail`, `owner`, `severity` (low, medium, high), `status` (open, mitigated, accepted, closed), `mitigation`, `criteria`, `visibility` | open and accepted risks stay on the check |
| `decisions` | `id`, `name`, `detail`, `owner`, `date`, `criteria`, `visibility` | scope and approach decisions; not proceed, hold or stop |
| `checklist` | `id`, `name`, `detail`, `owner`, `due`, `done`, `visibility` | the operational handover |
| `proposals` | written by `pilot.py propose` only | agent assessments; always internal, never a review |
| `reviews` | written by `pilot.py record` only | human criterion reviews (met, unmet, blocked) and decisions (proceed, hold, stop) |

A review or proposal stores `fingerprint`, the SHA-256 of the exact inputs it judged: for a
criterion, its definition plus every linked evidence record and attachment entry; for a decision,
the whole record (charter, criteria, evidence, attachments, risks, decisions, checklist and the
criterion reviews). Change any of them and it reads `changed` and needs re-review. A review also
stores `customer_fingerprint` over the customer view, so edits to internal records never change
what the customer handover says.

Reviews and proposals are append-only: never edit or delete history. To retire a pilot, move its
folder to the host's archive rather than clearing records.

## Example

Fictional; trimmed to one record per section.

```json
{
  "version": 1,
  "charter": {"customer": "Example Co (fictional)", "title": "Faster intake triage",
              "objective": "Route requests in under two minutes without losing auditability.",
              "owners": "Pilot lead; customer sponsor", "start": "2026-09-01", "end": "2026-10-15",
              "internal_notes": "Commercial notes stay here."},
  "criteria": [{"id": "c-triage", "name": "Triage under two minutes",
                "metric": "Median intake-to-route time", "baseline": "4m 20s over 120 requests",
                "threshold": "Under 2m 00s over at least 100 requests",
                "target_date": "2026-10-05", "owner": "Pilot lead", "visibility": "customer"}],
  "evidence": [{"id": "e-run", "name": "Routing benchmark", "summary": "120 requests; median 102 s.",
                "source": "Benchmark run 024, 2026-09-28", "owner": "Pilot lead",
                "collected": "2026-09-28", "stale_after_days": 14, "criteria": ["c-triage"],
                "visibility": "customer"}],
  "attachments": [{"id": "a-bench", "evidence": "e-run", "path": "attachments/benchmark.csv",
                   "sha256": "<64 hex characters from shasum -a 256>", "bytes": 50,
                   "added": "2026-09-28", "visibility": "customer"}],
  "risks": [{"id": "r-access", "name": "Operator access not approved",
             "detail": "Recovery rehearsal is blocked.", "owner": "Customer sponsor",
             "severity": "high", "status": "open", "mitigation": "Approve a least-privilege role.",
             "criteria": ["c-triage"], "visibility": "customer"}],
  "decisions": [{"id": "d-scope", "name": "One intake queue only",
                 "detail": "Keeps the before and after comparable.", "owner": "Pilot lead",
                 "date": "2026-09-02", "criteria": ["c-triage"], "visibility": "customer"}],
  "checklist": [{"id": "h-rehearse", "name": "Witness the recovery rehearsal",
                 "detail": "Record operator, duration and result.", "owner": "Customer sponsor",
                 "due": "2026-10-10", "done": false, "visibility": "customer"}],
  "proposals": [],
  "reviews": []
}
```

## Using the datastore skill instead

When the host keeps many pilots and wants to query across them (which criteria are overdue on every
active pilot), keep one append-only record per row with the datastore skill in the host repo:
tables for criteria, evidence, attachments, risks, decisions, checklist, proposals and reviews, each
row carrying `pilot` and `id`. The rules do not change: fingerprints over the same inputs,
proposals and reviews append-only, reviews written only by a person, the handover built from
customer-visible rows only. `pilot.py` reads only `pilot.json`, so export a pilot's rows to that
shape before running its check or handover.
