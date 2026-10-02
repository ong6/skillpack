---
name: skill-search
description: >-
  Find out whether a skill exists for a job, including skills that are not loaded: rarely used
  skills (idle a month, so not linked), retired skills in the private archive, and external
  skills the catalog lists from saved videos and repos. Use for "do we have a skill for...",
  "find a skill that...", "is there a skill like X", "see if we have a skill like this", or when
  a manual or the user names a skill that is not in the loaded list. Not for writing or revising
  a skill (skillsmith), and not for running a skill that is already loaded.
---

# Skill search

The loaded skill list is only the core tier. Rarely used, retired and external skills stay
invisible until you search for them.

## Search

1. From this skill's folder run `python3 scripts/search.py <3-6 words for the job>` (Python 3.7+,
   stdlib only). It runs the skills repo's `bin/skills find` across every tier and prints ranked
   hits with tier and path or URL. For a named skill, search the name as well.
2. If nothing fits, search once more with synonyms ("deck" → "slides presentation").
3. Read the SKILL.md (or the catalog note, for an external hit) of the top one to three hits
   before answering. A word match is not a fit.
4. If the script can't find `bin/skills`, say so, then list `skills/`, `rarely-used/` and
   `archive/skills/` in the skills checkouts by hand.

## Answer

Lead with the best match, its tier, its path or URL, and the next step:

| Tier | Meaning | Next step |
|---|---|---|
| core | linked, already loaded | use it now |
| rarely used | idle 30+ days, not loaded | read its SKILL.md in place and follow it (a use brings it back at the next daily tidy), or run `bin/skills restore <name>` if the user wants it loaded now |
| retired | in the private repo's `archive/skills/` | say it was retired; bringing it back is the user's call (`git mv`, per that archive's README) |
| external | someone else's skill listed in the catalog | give the URL and where it was seen; offer to adopt it through skillsmith. Never call it installed or vetted |

Nothing in any tier: say so plainly and offer to make one with skillsmith. Don't restore,
install or edit anything unless the user asks.
