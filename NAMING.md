# Skill names

Name the job: **verb-object** in lowercase kebab-case. A reader should understand the task before
opening its description. Prefer two to four words; five tokens and 64 characters are the limits.

- Use familiar actions consistently: `write-email`, `plan-trip`, `review-quote`, `build-skill`.
- Use one artifact in the singular and a set in the plural: `write-brief`, `find-jobs`.
- Add a source or domain when it removes ambiguity: `fetch-youtube-transcript`.
- Drop filler articles and invented brands: `review-quote`, not `review-a-quote` or `quoteforge`.
- Keep folder, frontmatter name, invocation examples and agent metadata aligned.
- Keep one canonical skill; do not retain duplicate discoverable folders as aliases.
- Name the primary job; explain secondary duties and exclusions in the description.
- Search the catalog first. Extend an existing skill instead of adding a synonym.

The recognized verbs and limits live in [naming.json](naming.json). Add a new verb there only when
an existing one misstates the job, and document a concrete example. Mechanical validation cannot
prove that a name is understandable or that a skill improves behavior.

```sh
python3 scripts/check-names.py
python3 scripts/check-names.py --skills-dir /path/to/repo/.claude/skills
python3 scripts/test-names.py
```

For new libraries use subject-capability names (for example `agent-fact-checks`); for collections,
use domain-skills or domain-toolkit. These are different from invokable skill commands. Existing
repository URLs and imports are compatibility contracts and require a coordinated migration.

## September 2026 migration

| Old command | Current command |
|---|---|
| `3d-design` | `design-3d` |
| `blender-authoring` | `build-blender-scene` |
| `web-extract` | `read-webpage` |
| `youtube-transcript` | `fetch-youtube-transcript` |
| `system-diagram` | `draw-system-diagram` |
| `markdown-to-pdf` | `export-markdown-pdf` |
| `handoff` | `write-handoff` |
| `feedback-loop` | `apply-feedback` |
| `refine` | `improve-work` |

Update explicit slash/dollar commands and hand-maintained skill links to the current names.
The natural-language trigger phrases and workflow requirements retain their meaning. Previous
evaluation receipts keep their original skill names and hashes; this migration changes identity,
not the tested decision rules.
