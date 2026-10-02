# Contributing

Bug fixes and small, reusable improvements are welcome. Open an issue before adding a new skill so
the trigger boundary, portability and overlap with existing skills can be agreed first.

Each skill lives in `skills/<name>/SKILL.md`. Add it to exactly one category in `catalog.yaml` and
give it a one-line entry under `skill_summaries`, then run:

```sh
python3 scripts/build-catalog.py          # regenerate the README tables
python3 scripts/build-catalog.py --check
python3 scripts/test-catalog.py
python3 tests/test_skills_cli.py
bin/skills guard .
python3 skills/skillsmith/scripts/lint_skill.py skills/<name>   # when skillsmith is present
```

Rules:

- Keep personal information out: no home paths, accounts, emails, phone numbers, prices or names.
  `bin/skills guard` enforces this in CI and before `bin/skills publish` pushes.
- Make skills location-independent. Refer to other skills by name. Find the working repo with
  `git rev-parse --show-toplevel`, and never resolve a script's own symlink to find siblings.
- Never shell out to another AI CLI (`claude -p`, `codex exec`) from a skill. Use the host's own
  subagents.
- `bin/skills` stays a single stdlib-only file that runs on Python 3.7.
