---
name: save-video
description: 'Save a YouTube video into the video library of the host repo as a note with overview, key takeaways, category and tags, indexed for later search. Use for "save this video", "add this to my videos", a YouTube link with "keep/remember/save", or "what videos do I have on X" (search the library). Not for a one-off summary the owner only wants to read now (youtube-transcript alone).'
---

# Save Video

Turns a YouTube link into a filed note in the host repo's video library. The host repo's folder
manual (e.g. its `AGENTS.md`) says where notes go; find the library folder from it, then read that
folder's own manual and index (note shape, category table, tag vocabulary) before filing. Below,
`<videos>` is that folder. No library yet → ask where it should live before creating one.

## Save

1. **Fetch the transcript** with the `youtube-transcript` skill (its `scripts/yt_transcript.py`
   `"<url>"`). Get title, channel and duration from `yt-dlp --dump-json --skip-download "<url>"`
   when available; otherwise from the page via `web-extract` or the watch page the browser fallback
   opened, and mark anything unverified with `TODO:`.
2. **Check for a duplicate**: `grep -l "<video id>" <videos>/*.md`. If it exists, append to that
   note instead of creating another.
3. **Pick the category** from the index's category table (one value). **Pick 3–6 tags**, reusing
   the existing vocabulary first (`grep -h '^tags:' <videos>/*.md`). New category → add its index
   row.
4. **Write the note** at `<videos>/<slug>.md` in the shape the folder manual gives: overview,
   5–10 takeaways from the transcript, "Why I saved it" (owner's words, else `TODO:`), optional
   timestamps. Takeaways are the video's claims, not your commentary; keep the note under ~60 lines.
5. **Index it**: add one line under the category heading in the folder index (create the heading
   if it's the category's first video), replacing any "empty" placeholder.
6. **Reply** with the absolute path, category, tags, and the three strongest takeaways. No recap
   of the steps.

Several links in one message → one note each, same pass; run the fetches in parallel.

## Search ("what do I have on X")

`grep -il 'tags:.*X\|title:.*X' <videos>/*.md`, then answer with title, category and the one-line
hook from the index, absolute paths. Zero hits → say so and offer the nearest tags.

## Failure modes

- Transcript unavailable (no captions, IP block): fall through the `youtube-transcript` fallbacks;
  if all fail, still file the note from the description page with `TODO: no transcript` and say so.
- Wrong category is cheap; a duplicate note is not. Always run step 2.
