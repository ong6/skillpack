---
name: datastore
description: >-
  Keep structured, queryable records in a git repository as a SQLite-backed dataset: append-only
  JSONL logs committed to git are the truth, and a local SQLite cache gives fast SQL. Use when data is
  many rows with the same fields that will be filtered, joined, deduplicated or trended over time
  ("track X over time", "store these as a table", "query my jobs/prices/workouts", a script that
  ingests records daily), or when a workflow needs durable machine state. Not for prose notes,
  one-off lists that fit in a Markdown table, or secrets.
---

# Manage Records

Markdown is for things the owner reads. A dataset is for records a script or agent queries.
When a Markdown table would pass ~50 rows, gets rewritten by a script, or needs a join, use a
dataset and keep a Markdown report that summarizes it.

## Layout

```text
<domain folder>/db/           the dataset, inside the theme folder it serves
  schema.sql                  CREATE TABLE statements; every table has a PRIMARY KEY
  log/YYYY-MM.jsonl           append-only writes, committed like any note
<repo>/.datastore/<slug>.db   SQLite cache, gitignored, rebuilt from the log when stale
```

The host repo's folder manual (e.g. its `AGENTS.md`) says which domain folder a dataset belongs
in. Add `.datastore/` to the repo's `.gitignore` before the first write.

Deleting the cache loses nothing. Never commit a `.db` file and never edit the log by hand. The
cache stays read-only too: every write goes through `upsert` or `delete`, so the log stays the
only truth. History is the point: a delete is a logged event, not an erased line.

## Use

`DS` is `scripts/datastore.py` in this skill's base directory. Run it from the host repo; the
cache goes to the Git root above the dataset folder.

```sh
python3 $DS init    <domain>/db                 # then write schema.sql
python3 $DS upsert  <domain>/db <table> --json '{"id": "x", "value": 1}'
python3 $DS upsert  <domain>/db <table> --file rows.jsonl
python3 $DS query   <domain>/db "SELECT * FROM <table> ORDER BY value DESC LIMIT 20"
python3 $DS tables  <domain>/db
```

Scripts import it directly. Find this skill through `$SKILLS_HOME` (the skills checkout) first,
else the host repo's skill link folder; never climb or resolve a script's own path to find it:

```python
import os, subprocess, sys
from pathlib import Path
home = os.environ.get("SKILLS_HOME")
root = os.environ.get("PDS_ROOT") or subprocess.run(["git", "rev-parse", "--show-toplevel"],
    stdout=subprocess.PIPE, universal_newlines=True, check=True).stdout.strip()
scripts = (Path(home) / "skills" if home else Path(root) / ".claude" / "skills") / "datastore" / "scripts"
sys.path.insert(0, str(scripts))
from datastore import Dataset
ds = Dataset("<domain>/db")
ds.upsert("table", rows)          # rows identical to the stored ones are not re-logged
ds.query("SELECT ...", params)    # SELECT / WITH / PRAGMA only
```

## Rules

1. **Schema changes are additive.** New tables or new nullable columns only, because the whole
   log replays through the current `schema.sql`. To rename or restructure, add the new table and
   migrate with upserts. Never rewrite old log lines.
2. **Keys are natural and stable** (normalized name, date plus entity, external ID), so reruns
   upsert rather than duplicate.
3. **Keep rows lean.** Store hashes and short fields, not whole pages or binaries; bulky source text
   belongs in gitignored scratch. The log is in git forever. JSONL compresses about 9x in git;
   keep the raw log under ~50 MB per dataset per year, and log only changed rows (`upsert` skips
   unchanged ones, so never store a field that changes every run, such as last-seen time).
4. **Index the dataset** in its folder's `README.md` like any subfolder, and keep human-facing
   conclusions in Markdown next to it (a report or summary note linking the dataset).
5. **No secrets or credentials in rows.** Same rule as every other file here.
6. **Complex queries** run through `query`. For ad hoc exploration, `sqlite3 .datastore/<slug>.db`
   is fine for reads; writes must go through the script.

## Datasets

Keep a registry of the repo's datasets (path and what each serves) where the host repo's folder
manual says, so agents find an existing dataset before creating a rival one.
