---
name: wait-what
description: Re-explain the last answer in plain language. Use only when the user invokes wait-what or says the reply was confusing, unclear, too technical, or did not land.
---

Re-pitch the last answer with the missing context, using short sentences and plain English.
Prefer the project's own vocabulary when a `CONTEXT.md` or equivalent domain glossary exists.
Do not defend, extend, or merely summarize the previous answer; explain it again from a better starting point.
Preserve exact evidence tokens, paths, citations, numbers, and uncertainty. Expand a project term only
from the supplied glossary or repository context; if its meaning is unavailable, say what role it
plays without inventing a definition. Add no architecture, conclusion, or next action that was not
already supported by the prior answer.
