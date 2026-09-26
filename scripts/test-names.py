#!/usr/bin/env python3
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_names", ROOT / "scripts/check-names.py")
names = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(names)


class NamingTests(unittest.TestCase):
    def setUp(self):
        self.policy = names.load_policy(ROOT / "naming.json")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def skill(self, folder, name=None):
        path = self.root / folder
        path.mkdir()
        (path / "SKILL.md").write_text(f"---\nname: {name or folder}\ndescription: Use for a task.\n---\n# Task\n")
        return path

    def test_clear_names_and_technical_objects_pass(self):
        for name in ("write-email", "build-skill", "design-3d", "fetch-youtube-transcript"):
            self.assertIsNone(names.validate_name(name, self.policy))

    def test_vague_noun_first_and_filler_names_fail(self):
        for name in ("refine", "skillsmith", "job-search", "write-an-email", "Write-email", "write--email"):
            with self.subTest(name=name):
                self.assertIsNotNone(names.validate_name(name, self.policy))

    def test_length_limits_fail(self):
        self.assertIsNotNone(names.validate_name("write-one-two-three-four-five", self.policy))
        self.assertIsNotNone(names.validate_name("write-" + "x" * 60, self.policy))

    def test_folder_and_manifest_must_agree(self):
        self.skill("write-email", "write-brief")
        self.assertTrue(any("must match folder" in e for e in names.check_directory(self.root, self.policy)[0]))

    def test_duplicate_alias_is_not_another_canonical_skill(self):
        source = self.skill("write-email")
        (self.root / "old-email").symlink_to(source, target_is_directory=True)
        self.assertTrue(any("duplicate skill identity" in e for e in names.check_directory(self.root, self.policy)[0]))

    def test_empty_incomplete_and_broken_directories_fail(self):
        self.assertTrue(names.check_directory(self.root, self.policy)[0])
        (self.root / "write-email").mkdir()
        (self.root / "write-brief").symlink_to(self.root / "missing")
        errors, _ = names.check_directory(self.root, self.policy)
        self.assertTrue(any("missing SKILL.md" in e for e in errors))
        self.assertTrue(any("broken skill link" in e for e in errors))

    def test_canonical_host_symlink_is_supported(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside)
            (target / "SKILL.md").write_text('---\nname: "write-email"\ndescription: Use for mail.\n---\n')
            (self.root / "write-email").symlink_to(target, target_is_directory=True)
            self.assertEqual(([], 1), names.check_directory(self.root, self.policy))

    def test_duplicate_frontmatter_name_fails(self):
        folder = self.skill("write-email")
        (folder / "SKILL.md").write_text('---\nname: write-email\nname: write-brief\n---\n')
        self.assertTrue(any("exactly one name" in e for e in names.check_directory(self.root, self.policy)[0]))

    def test_default_prompt_cannot_keep_an_old_skill_command(self):
        folder = self.skill("write-email")
        (folder / "agents").mkdir()
        metadata = folder / "agents/openai.yaml"
        metadata.write_text('interface:\n  default_prompt: "Use $write-an-email for this message."\n')
        self.assertTrue(any("default_prompt" in e for e in names.check_directory(self.root, self.policy)[0]))
        metadata.write_text('interface:\n  default_prompt: "Use $write-email for this message."\n')
        self.assertEqual(([], 1), names.check_directory(self.root, self.policy))


if __name__ == "__main__":
    unittest.main()
