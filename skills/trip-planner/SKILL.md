---
name: trip-planner
description: Plan or replan trips using live research for routes, hours, parking, food, tolls, and pacing. Use for itineraries and on-the-road questions about stops, parking, or eating.
---

# Plan Trip

Two modes. Both follow the same iron rule: **never recommend a place you haven't just
researched online.** Guessed opening hours, gate times, or parking rules ruin travel days.

## Mode 0 — Load context (always, first)

The host repo's folder manual (e.g. its `AGENTS.md`) says where trip notes and the trip-planning
lessons file live; read it first. If the repo keeps neither, work from the conversation and offer
to start them.

1. Read the trip-planning lessons file; the pacing rules and past mistakes live there. Apply them
   silently.
2. Read the active trip note (status, group size, vehicle, booking refs) and any shared trip doc
   (Google Sheet) the user links.
3. Note the group profile: size, vehicle (a 9-seater changes parking!), pacing multiplier.

## Mode 1 — Plan (pre-trip or next-day)

1. **Interview lightly**: dates, region, group, vehicle, anchors already booked. Don't ask
   what the lessons file already answers.
2. **Research the surroundings before drafting** (live web search and page reading, per candidate area):
   - the main streets/neighbourhoods worth walking, and what clusters together
   - drive/walk times between candidates (cluster by area; no backtracking)
   - opening hours **for the specific day of week**, entry prices, booking requirements
   - parking: surface vs multi-storey (height barriers vs the vehicle), gate/closing
     times, evening charges
   - hidden costs: tolls, congestion/drop-off charges (airports!), event-day closures
   - sunset time when evening plans matter
3. **Draft the day**: ONE anchor activity per day + a menu of nearby options, drive times
   padded per the lessons file (default +50%). Book only true anchors; keep the rest
   cancellable/flexible.
4. **Write it down**: update the trip note's diary section (plan + alternatives considered),
   and commit if the host repo's rules allow it.

## Mode 2 — Reroute (on the road)

The user is in a car/at a stop and needs an answer NOW. Optimize for phone-readable speed.

1. Establish **current time, position, ETA, and the next hard deadline** (booking, car
   return, flight). Check the actual local time; don't trust the stated schedule.
2. Research ONLY what the decision needs, but always verify the killers:
   - **kitchen closing times** (UK pubs stop food 21:00–21:30, so an ETA after 20:30 changes
     the answer)
   - **parking that actually works**: fits the vehicle, no gate lock-in, evening rules
   - whether the venue is even open on arrival
3. Answer in this shape: **one recommendation + one fallback + the action to take from the
   car right now** (usually "call X and book for N people at HH:MM"). Then timings as a
   numbered run-sheet. Apply the pacing buffer to travel legs, then protect an additional
   30-minute margin before any hard check-in, boarding, closing, or return deadline. If the
   resulting plan has less than 30 minutes of margin, recommend skipping the optional stop.
4. Log the decision (and what was rejected, briefly) into the trip diary afterwards.

## Recommendation quality bar

- Every timed claim (hours, closing, charge amounts) verified online this session, or
  explicitly marked as "check the sign / call ahead".
- Every stop names its parking. Every dinner names a booking action.
- State the arrival-time consequence of every option ("lands you in Burford ~23:10").
- Groups >6: restaurants must be called ahead; note which cuisines absorb big tables late
  (Indian/Italian > village gastropub).
- Data gaps are listed honestly. Never invent a price, an opening hour, or a distance.

## After the trip

Harvest new lessons into the lessons file (append, tag with the trip) and mark the trip note's
diary as the final record. Then archive the trip note the way the host repo's folder manual says
(typically a move to its archive with a tombstone link).
