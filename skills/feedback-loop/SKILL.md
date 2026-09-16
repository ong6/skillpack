---
name: feedback-loop
description: Capture the owner's feedback about how the agent, a skill, a hook, a rule, or a reply behaved, log it in feedback.md, and patch whatever it targets in the same session so the behaviour changes by default. Fires on "don't do X", "stop doing", "why does it", "next time", "I prefer", "that was wrong", "that's annoying", "can I turn this off", "always" or "never" about agent behaviour, or a correction to a reply; not for feedback on the owner's own writing, on other people, or a one-off instruction for the current task.
---

# Feedback loop

Feedback is a change request. Log it, then change the thing it is about, in this session. The
owner never repeats feedback and never maintains the log.

## Procedure

1. **Quote it.** Keep the owner's words, trimmed of filler. Do not sharpen them into a stronger claim.
2. **Name the target.** One row of this table. When two fit, take the narrower one.

   | Feedback is about | Target | What "applied" means |
   |---|---|---|
   | What a skill did or failed to do | that skill's `SKILL.md` | smallest edit that changes behaviour: a checklist line, a ❌/✅ row, a trigger phrase in `description` |
   | How every reply should read, or a rule for the whole repo | `CLAUDE.md` (or `AGENTS.md` if that is canonical) | one line in the section that already covers it |
   | Something that should happen automatically on an event | the hook script and its registration | edit script, mirror registration for every client, run its tests |
   | A tool's own behaviour (Claude Code, the IDE, a CLI) | that tool's config | make the config change; note if it is per-machine |
   | This loop itself | this `SKILL.md` | same as any skill |
   | Only this task, or the owner's own content | none | log it, change nothing |

3. **Apply it.** Edit the target now. Do not ask permission for in-repo edits. Do not add a
   "feedback" section to a skill; fold the change into the step it affects. If the new feedback
   contradicts an earlier entry, apply the new one and mark the old entry `superseded`.
4. **Verify.** Run the repo's skill validator (`.agents/sync-skills.sh --check` in the store) after
   a skill edit, the hook tests after a hook edit. A failing check means go back to step 3.
5. **Log it** in `feedback.md` at the repo root, appended in date order. Create the file from the
   skeleton below if it is missing. Never rewrite or delete earlier entries.
6. **Reply in one or two lines:** what changed and the absolute path of the file.

## Log entry

```markdown
## YYYY-MM-DD · short label
- **Said:** "owner's words"
- **About:** target from the table (skill name, CLAUDE.md, hook name, tool)
- **Applied:** what was edited, one line; or "nothing, one-off"
- **Status:** applied | pending | superseded by YYYY-MM-DD
```

`pending` is for a target that cannot be edited from this session (another machine's config, a
locked file). Say so in the reply and leave the entry pending until it is done.

## Skeleton for a new `feedback.md`

```markdown
# Feedback log

What the owner said about how the agent, a skill, a hook, or a reply behaved, and what changed
because of it. Append-only; the `feedback-loop` skill writes here.
```

Add the repo's usual frontmatter above the heading if its notes require one.

## Examples

| ❌ | ✅ |
|---|---|
| "Noted, I'll keep that in mind." (nothing edited) | Edit the skill, log the entry, reply with the path. |
| Append "Owner feedback 2026-09-15: be shorter" to the end of a skill | Change the line in the skill that produced the long output. |
| Paraphrase "why does it do X" as "owner hates X" | Quote it and log the actual question. |
| Ask "should I update the skill?" | Update it. Feedback is the instruction. |
| Log a one-off ("use the other branch this time") as a rule | Log it with `About: none`, change nothing. |

## Keeping this skill in sync across repos and machines

This skill ships in the [`ong6/skillpack`](https://github.com/ong6/skillpack) collection, which host repos
install as a `git subtree`. The collection's `scripts/sync.sh` moves changes both ways and is wired
into the host repo's hooks:

- `--start` at SessionStart: merges what the last background fetch brought in, then fetches again
  in the background. No network on the startup path except the first run on a clone.
- `--stop` at Stop: if this folder changed locally since the last sync, merges upstream first, then
  pushes. Exit 2 on a merge conflict, with the resolve command in the message.
- `--status` prints the sync state. Run `scripts/test-sync.sh` after editing the script.

Edits to any skill in the collection, made in any repo that uses it, reach every other one on their
next session. Edit in place; never keep a second copy.
