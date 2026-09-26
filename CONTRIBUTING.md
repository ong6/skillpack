# Contributing

Name skills by their job using the [verb-object convention](NAMING.md). Run
`python3 scripts/check-names.py` and `python3 scripts/test-names.py` alongside the catalog checks.

Bug fixes and small, reusable improvements are welcome. Open an issue before adding a new skill so
the trigger boundary, portability and overlap with existing skills can be agreed first.

Each skill lives in `skills/<name>/SKILL.md`. Add it to exactly one category in `catalog.yaml`, then
run:

```sh
python3 scripts/build-catalog.py
python3 scripts/build-catalog.py --check
python3 scripts/test-catalog.py
bash scripts/test-sync.sh
```

Keep private paths, accounts and prices out of this repository. A skill should work outside the
repo where it was written.
