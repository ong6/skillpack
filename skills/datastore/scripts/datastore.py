#!/usr/bin/env python3
"""Git-friendly structured data: append-only JSONL logs are the truth, SQLite is a rebuildable cache.

A dataset is a folder holding `schema.sql` (CREATE TABLE statements, each with a PRIMARY KEY) and
`log/YYYY-MM.jsonl`. Every write appends one line per row:

    {"at": "...", "table": "jobs", "op": "upsert", "row": {...}}
    {"at": "...", "table": "jobs", "op": "delete", "key": {"key": "..."}}

The cache lives in `<repo>/.datastore/<dataset-slug>.db` (gitignored) and is rebuilt whenever the
logs or schema are newer. Deleting it loses nothing.

  datastore.py init    <dataset>
  datastore.py upsert  <dataset> <table> (--json '{...}' | --file rows.json[l])
  datastore.py delete  <dataset> <table> --json '{"pk": ...}'
  datastore.py query   <dataset> "SELECT ..." [--format table|json|csv]
  datastore.py tables  <dataset>
  datastore.py rebuild <dataset>

Python: from datastore import Dataset; ds = Dataset(path); ds.upsert("t", rows); ds.query(sql)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = "log"
SCHEMA = "schema.sql"


def repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / ".git").exists():
            return parent
    return start


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else value


class Dataset:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).resolve()
        if not (self.path / SCHEMA).exists():
            raise SystemExit(f"{self.path} has no {SCHEMA}; run `datastore.py init` first")
        root = repo_root(self.path)
        slug = re.sub(r"[^a-z0-9]+", "-", str(self.path.relative_to(root)).casefold()).strip("-")
        self.cache = root / ".datastore" / f"{slug}.db"
        self._db: sqlite3.Connection | None = None

    # ---- schema -----------------------------------------------------------------------------
    def columns(self, db: sqlite3.Connection, table: str) -> tuple[list[str], list[str]]:
        info = db.execute(f"PRAGMA table_info({table})").fetchall()
        if not info:
            raise SystemExit(f"unknown table {table!r}; declare it in {SCHEMA}")
        cols = [row[1] for row in info]
        pk = [row[1] for row in sorted(info, key=lambda r: r[5]) if row[5]]
        return cols, pk

    # ---- cache ------------------------------------------------------------------------------
    def logs(self) -> list[Path]:
        return sorted((self.path / LOG_DIR).glob("*.jsonl"))

    def stale(self) -> bool:
        if not self.cache.exists():
            return True
        built = self.cache.stat().st_mtime
        return any(p.stat().st_mtime > built for p in [self.path / SCHEMA, *self.logs()])

    def rebuild(self) -> sqlite3.Connection:
        if self._db:
            self._db.close()
        self.cache.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache.with_suffix(".tmp")
        tmp.unlink(missing_ok=True)
        db = sqlite3.connect(tmp)
        db.executescript((self.path / SCHEMA).read_text())
        for log in self.logs():
            for n, line in enumerate(log.read_text().splitlines(), 1):
                if line.strip():
                    try:
                        self._apply(db, json.loads(line))
                    except (sqlite3.Error, json.JSONDecodeError, KeyError) as exc:
                        raise SystemExit(f"{log.name}:{n}: {exc}") from exc
        db.commit()
        db.close()
        tmp.replace(self.cache)
        self._db = None
        return self.db()

    def db(self) -> sqlite3.Connection:
        if self._db is None:
            if self.stale():
                return self.rebuild()
            self._db = sqlite3.connect(self.cache)
            self._db.row_factory = sqlite3.Row
        return self._db

    def _apply(self, db: sqlite3.Connection, event: dict) -> None:
        table = event["table"]
        cols, pk = self.columns(db, table)
        if event["op"] == "delete":
            key = event["key"]
            db.execute(f"DELETE FROM {table} WHERE " + " AND ".join(f"{c} = ?" for c in pk),
                       [key[c] for c in pk])
            return
        row = {k: encode(v) for k, v in event["row"].items() if k in cols}
        missing = [c for c in pk if row.get(c) is None]
        if missing:
            raise KeyError(f"{table}: primary key {missing} missing")
        names = list(row)
        updates = [c for c in names if c not in pk]
        conflict = (f" ON CONFLICT({', '.join(pk)}) DO UPDATE SET " +
                    ", ".join(f"{c} = excluded.{c}" for c in updates)) if updates else " ON CONFLICT DO NOTHING"
        db.execute(f"INSERT INTO {table} ({', '.join(names)}) VALUES ({', '.join('?' * len(names))}){conflict}",
                   [row[c] for c in names])

    # ---- writes -----------------------------------------------------------------------------
    def _append(self, events: list[dict]) -> None:
        if not events:
            return
        log = self.path / LOG_DIR / f"{datetime.now(timezone.utc):%Y-%m}.jsonl"
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def upsert(self, table: str, rows: list[dict], skip_unchanged: bool = True) -> int:
        """Apply rows to the cache and log them. Unchanged rows are not re-logged."""
        db = self.db()
        cols, pk = self.columns(db, table)
        events = []
        for row in rows:
            clean = {k: v for k, v in row.items() if k in cols}
            if skip_unchanged:
                current = db.execute(f"SELECT * FROM {table} WHERE " + " AND ".join(f"{c} = ?" for c in pk),
                                     [encode(clean.get(c)) for c in pk]).fetchone()
                if current and all(current[k] == encode(v) for k, v in clean.items()):
                    continue
            event = {"at": now(), "table": table, "op": "upsert", "row": clean}
            self._apply(db, event)
            events.append(event)
        db.commit()
        self._append(events)
        self._touch()
        return len(events)

    def delete(self, table: str, key: dict) -> None:
        event = {"at": now(), "table": table, "op": "delete", "key": key}
        db = self.db()
        self._apply(db, event)
        db.commit()
        self._append([event])
        self._touch()

    def _touch(self) -> None:
        # The cache now includes the new log lines; keep it from looking stale.
        self.cache.touch()

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        db = self.db()
        if not re.match(r"\s*(select|with|pragma)\b", sql, re.I):
            raise SystemExit("query is read-only; write through upsert/delete so the log stays the truth")
        return [dict(row) for row in db.execute(sql, params).fetchall()]


def init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    schema = path / SCHEMA
    if not schema.exists():
        schema.write_text("-- One CREATE TABLE per table. Every table needs a PRIMARY KEY.\n"
                          "-- Additive changes only (new tables, new nullable columns); the log replays through this.\n")
    (path / LOG_DIR).mkdir(exist_ok=True)
    print(f"initialized {path}; declare tables in {schema}")


def read_rows(args: argparse.Namespace) -> list[dict]:
    if args.json:
        data = json.loads(args.json)
    else:
        text = Path(args.file).read_text()
        data = [json.loads(l) for l in text.splitlines() if l.strip()] if args.file.endswith(".jsonl") else json.loads(text)
    return data if isinstance(data, list) else [data]


def render(rows: list[dict], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("(no rows)")
        return
    if fmt == "csv":
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return
    cols = list(rows[0])
    cell = lambda v: "" if v is None else str(v).replace("\n", " ")[:60]
    widths = [max(len(c), *(len(cell(r[c])) for r in rows)) for c in cols]
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(cell(r[c]).ljust(w) for c, w in zip(cols, widths)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("init", "tables", "rebuild"):
        sub.add_parser(name).add_argument("dataset")
    up = sub.add_parser("upsert")
    up.add_argument("dataset"); up.add_argument("table")
    src = up.add_mutually_exclusive_group(required=True)
    src.add_argument("--json"); src.add_argument("--file")
    de = sub.add_parser("delete")
    de.add_argument("dataset"); de.add_argument("table"); de.add_argument("--json", required=True)
    q = sub.add_parser("query")
    q.add_argument("dataset"); q.add_argument("sql")
    q.add_argument("--format", choices=["table", "json", "csv"], default="table")
    args = parser.parse_args()
    if args.cmd == "init":
        init(Path(args.dataset))
        return 0
    ds = Dataset(args.dataset)
    if args.cmd == "rebuild":
        ds.rebuild()
        print(f"rebuilt {ds.cache}")
    elif args.cmd == "tables":
        render(ds.query("SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name"), "table")
    elif args.cmd == "upsert":
        print(f"{ds.upsert(args.table, read_rows(args))} row(s) written")
    elif args.cmd == "delete":
        ds.delete(args.table, json.loads(args.json))
        print("deleted")
    elif args.cmd == "query":
        render(ds.query(args.sql), args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
