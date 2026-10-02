#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from datastore import Dataset  # noqa: E402


class DatastoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / ".git").mkdir()
        self.path = root / "life" / "db"
        (self.path / "log").mkdir(parents=True)
        (self.path / "schema.sql").write_text(
            "CREATE TABLE t (id TEXT PRIMARY KEY, n INTEGER, tags TEXT);\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_upsert_logs_and_skips_unchanged(self):
        ds = Dataset(self.path)
        self.assertEqual(ds.upsert("t", [{"id": "a", "n": 1, "tags": ["x"]}]), 1)
        self.assertEqual(ds.upsert("t", [{"id": "a", "n": 1, "tags": ["x"]}]), 0)
        self.assertEqual(ds.upsert("t", [{"id": "a", "n": 2}]), 1)
        self.assertEqual(ds.query("SELECT n, tags FROM t"), [{"n": 2, "tags": '["x"]'}])
        lines = next((self.path / "log").glob("*.jsonl")).read_text().splitlines()
        self.assertEqual(len(lines), 2)

    def test_cache_rebuilds_from_log(self):
        ds = Dataset(self.path)
        ds.upsert("t", [{"id": "a", "n": 1}, {"id": "b", "n": 2}])
        ds.delete("t", {"id": "a"})
        ds.cache.unlink()
        fresh = Dataset(self.path)
        self.assertEqual(fresh.query("SELECT id FROM t"), [{"id": "b"}])

    def test_query_is_read_only(self):
        ds = Dataset(self.path)
        with self.assertRaises(SystemExit):
            ds.query("DELETE FROM t")


if __name__ == "__main__":
    unittest.main()
