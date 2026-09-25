#!/usr/bin/env python3
"""Exercise the catalog CLI against disposable repository fixtures."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        self.script = self.root / "scripts/build-catalog.py"
        shutil.copyfile(Path(__file__).with_name("build-catalog.py"), self.script)
        self.skill = self.root / "skills/example/SKILL.md"
        self.skill.parent.mkdir(parents=True)
        self.skill.write_text("---\nname: example\ndescription: A useful skill.\n---\nBody.\n")
        self.catalog = {
            "skill_summaries": {"example": "One line."},
            "categories": [{"key": "tools", "title": "Tools", "blurb": "Useful tools.", "skills": ["example"]}],
        }
        self.readme = self.root / "README.md"
        self.readme.write_text(
            "Owner's introduction.\n<!-- SKILL INDEX START -->\nstale\n<!-- SKILL INDEX END -->\n"
            "Owner's middle.\n<!-- CATALOG START -->\nstale\n<!-- CATALOG END -->\nOwner's ending.\n"
        )
        self.write_catalog()

    def write_catalog(self):
        (self.root / "catalog.yaml").write_text(yaml.safe_dump(self.catalog))

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(self.script), *args], capture_output=True, text=True)

    def assert_rejected_unchanged(self, *args):
        before = self.readme.read_bytes()
        result = self.run_cli(*args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.readme.read_bytes(), before)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def test_check_detects_drift_without_writing(self):
        result = self.assert_rejected_unchanged("--check")
        self.assertIn("drift", result.stderr)

    def test_build_then_check_preserves_owner_text_and_mtime(self):
        self.assertEqual(self.run_cli().returncode, 0)
        text = self.readme.read_text()
        for part in ("introduction", "middle", "ending"):
            self.assertIn(f"Owner's {part}.", text)
        before = self.readme.stat().st_mtime_ns
        self.assertEqual(self.run_cli("--check").returncode, 0)
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.readme.stat().st_mtime_ns, before)

    def test_index_only_change_is_reported_updated(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.catalog["skill_summaries"]["example"] = "Changed summary."
        self.write_catalog()
        self.assert_rejected_unchanged("--check")
        self.assertIn("updated", self.run_cli().stdout)

    def test_duplicate_membership_rejected(self):
        self.catalog["categories"].append({"key": "other", "title": "Other", "blurb": "More.", "skills": ["example"]})
        self.write_catalog()
        self.assertIn("exactly one", self.assert_rejected_unchanged().stderr)

    def test_duplicate_within_category_rejected(self):
        self.catalog["categories"][0]["skills"].append("example")
        self.write_catalog()
        self.assert_rejected_unchanged()

    def test_duplicate_category_keys_rejected(self):
        self.catalog["categories"].append({"key": "tools", "title": "Other", "blurb": "More."})
        self.write_catalog()
        self.assert_rejected_unchanged()

    def test_catalog_disk_drift_rejected(self):
        for field in ("missing_skill", "unlisted_skill", "missing_summary", "extra_summary"):
            with self.subTest(field=field):
                original = yaml.safe_load(yaml.safe_dump(self.catalog))
                if field == "missing_skill":
                    self.catalog["categories"][0]["skills"].append("absent")
                elif field == "unlisted_skill":
                    self.catalog["categories"][0]["skills"] = []
                elif field == "missing_summary":
                    self.catalog["skill_summaries"] = {}
                else:
                    self.catalog["skill_summaries"]["absent"] = "Absent."
                self.write_catalog()
                self.assert_rejected_unchanged()
                self.catalog = original

    def test_invalid_frontmatter_rejected(self):
        for body in ("no frontmatter", "---\n- item\n---\n", "---\nname: example\n---\n",
                     "---\nname: wrong\ndescription: Fine.\n---\n", "---\nname: example\ndescription: false\n---\n"):
            with self.subTest(body=body):
                self.skill.write_text(body)
                self.assert_rejected_unchanged()

    def test_bad_markers_do_not_destroy_owner_text(self):
        original = self.readme.read_text()
        for text in (original.replace("<!-- CATALOG END -->", ""),
                     original + "<!-- SKILL INDEX START -->\n",
                     original.replace("<!-- SKILL INDEX START -->", "<!-- SWAP -->")
                     .replace("<!-- SKILL INDEX END -->", "<!-- SKILL INDEX START -->")
                     .replace("<!-- SWAP -->", "<!-- SKILL INDEX END -->")):
            with self.subTest(text=text):
                self.readme.write_text(text)
                self.assert_rejected_unchanged()

    def test_table_cells_escape_pipes_and_fold_newlines(self):
        self.catalog["skill_summaries"]["example"] = "A | B\nsecond line"
        self.write_catalog()
        self.skill.write_text("---\nname: example\ndescription: A | B\n---\n")
        self.assertEqual(self.run_cli().returncode, 0)
        text = self.readme.read_text()
        self.assertIn("A \\| B second line", text)
        self.assertIn("A \\| B |", text)

    def test_bad_catalog_types_fail_without_traceback(self):
        for data in (None, [], {"categories": {}}, {"categories": [None]},
                     {"categories": [], "skill_summaries": ["example"]}):
            with self.subTest(data=data):
                (self.root / "catalog.yaml").write_text(yaml.safe_dump(data))
                self.assert_rejected_unchanged()

    def test_unknown_flag_rejected_without_writing(self):
        self.assert_rejected_unchanged("--typo")

    def test_duplicate_yaml_mapping_keys_rejected(self):
        path = self.root / "catalog.yaml"
        path.write_text(path.read_text().replace("example: One line.", "example: One line.\n  example: Shadow value."))
        self.assertIn("duplicate mapping key", self.assert_rejected_unchanged().stderr)

    def test_duplicate_frontmatter_keys_rejected(self):
        self.skill.write_text("---\nname: wrong\nname: example\ndescription: Fine.\n---\n")
        self.assertIn("duplicate mapping key", self.assert_rejected_unchanged().stderr)

    def test_incomplete_skill_folder_rejected(self):
        (self.root / "skills/incomplete").mkdir()
        self.assertIn("missing SKILL.md", self.assert_rejected_unchanged().stderr)


if __name__ == "__main__":
    unittest.main()
