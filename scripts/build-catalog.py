#!/usr/bin/env python3
"""Regenerate the catalog tables in README.md from catalog.yaml and each SKILL.md's frontmatter.

Run from anywhere: python3 scripts/build-catalog.py. Use --check to verify without writing.
Exit 1 if metadata is invalid or, in check mode, the generated README has drifted.
"""
import argparse
from collections import Counter
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_START, INDEX_END = "<!-- SKILL INDEX START -->", "<!-- SKILL INDEX END -->"
START, END = "<!-- CATALOG START -->", "<!-- CATALOG END -->"


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        keys = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in keys
                keys.add(key)
            except TypeError:
                raise yaml.constructor.ConstructorError(None, None, "unhashable mapping key", key_node.start_mark)
            if duplicate:
                raise yaml.constructor.ConstructorError(None, None, f"duplicate mapping key: {key!r}", key_node.start_mark)
        return super().construct_mapping(node, deep=deep)


def require_text(value, context):
    if not isinstance(value, str) or not value.strip():
        sys.exit(f"{context}: expected a non-empty string")
    return " ".join(value.split())


def cell(value):
    return " ".join(value.split()).replace("|", "\\|")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{path}: no frontmatter")
    data = yaml.load(m.group(1), Loader=UniqueKeyLoader)
    if not isinstance(data, dict):
        sys.exit(f"{path}: frontmatter must be a mapping")
    name = require_text(data.get("name"), f"{path}: name")
    if name != path.parent.name:
        sys.exit(f"{path}: name must match skill folder {path.parent.name!r}")
    return name, require_text(data.get("description"), f"{path}: description")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on drift without writing README.md")
    args = parser.parse_args()
    cat = yaml.load((ROOT / "catalog.yaml").read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    if not isinstance(cat, dict) or not isinstance(cat.get("categories"), list):
        sys.exit("catalog.yaml: categories must be a list")
    keys = set()
    for c in cat["categories"]:
        if not isinstance(c, dict):
            sys.exit("catalog.yaml: each category must be a mapping")
        for field in ("key", "title", "blurb"):
            require_text(c.get(field), f"category {field}")
        if c["key"] in keys:
            sys.exit(f"duplicate category key: {c['key']}")
        keys.add(c["key"])
        for field in ("skills", "links"):
            if not isinstance(c.get(field, []), list):
                sys.exit(f"category {c['key']}: {field} must be a list")
        for skill in c.get("skills", []):
            if not isinstance(skill, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", skill):
                sys.exit(f"category {c['key']}: invalid skill name {skill!r}")
        for link in c.get("links", []):
            if not isinstance(link, dict):
                sys.exit(f"category {c['key']}: each link must be a mapping")
            for field in ("repo", "note"):
                require_text(link.get(field), f"category {c['key']}: link {field}")
    ordered_skills = [s for c in cat["categories"] for s in c.get("skills", [])]
    duplicates = sorted(s for s, count in Counter(ordered_skills).items() if count > 1)
    if duplicates:
        sys.exit(f"skills must appear in exactly one category: {duplicates}")
    skill_dirs = [p for p in (ROOT / "skills").iterdir() if p.is_dir()]
    incomplete = sorted(p.name for p in skill_dirs if not (p / "SKILL.md").is_file())
    if incomplete:
        sys.exit(f"skill folders missing SKILL.md: {incomplete}")
    on_disk = {p.name for p in skill_dirs}
    listed = set(ordered_skills)
    summaries = cat.get("skill_summaries", {})
    if not isinstance(summaries, dict) or any(not isinstance(s, str) for s in summaries):
        sys.exit("catalog.yaml: skill_summaries must map skill names to strings")
    missing, unlisted = listed - on_disk, on_disk - listed
    summary_missing, summary_extra = on_disk - summaries.keys(), summaries.keys() - on_disk
    if missing or unlisted or summary_missing or summary_extra:
        sys.exit(
            f"catalog drift: missing on disk {sorted(missing)}, not in catalog {sorted(unlisted)}, "
            f"missing summaries {sorted(summary_missing)}, extra summaries {sorted(summary_extra)}"
        )

    for skill, summary in summaries.items():
        require_text(summary, f"summary for {skill}")
    metadata = {s: frontmatter(ROOT / "skills" / s / "SKILL.md") for s in ordered_skills}
    index = ["| Skill | What I use it for |", "|---|---|"]
    for s in ordered_skills:
        name, _ = metadata[s]
        index.append(f"| [`{name}`](skills/{s}/SKILL.md) | {cell(summaries[s])} |")
    index_body = "\n".join(index) + "\n"

    out = []
    for c in cat["categories"]:
        out.append(f"### {c['title']}\n\n_{c['blurb']}_\n")
        if c.get("skills"):
            out.append("| Skill | Does |\n|---|---|")
            for s in c["skills"]:
                name, desc = metadata[s]
                out.append(f"| [`{name}`](skills/{s}/SKILL.md) | {cell(desc)} |")
            out.append("")
        if c.get("links"):
            out.append("Elsewhere:\n")
            for l in c["links"]:
                out.append(f"- [{l['repo']}](https://github.com/{l['repo']}) — {l['note']}")
            out.append("")
    body = "\n".join(out).rstrip() + "\n"

    readme = ROOT / "README.md"
    original = text = readme.read_text(encoding="utf-8")
    markers = (INDEX_START, INDEX_END, START, END)
    if any(text.count(marker) != 1 for marker in markers):
        sys.exit("README.md must contain each generated section marker exactly once")
    positions = [text.index(marker) for marker in markers]
    if positions != sorted(positions):
        sys.exit("README.md generated section markers are out of order")
    head, rest = text.split(INDEX_START, 1)
    _, tail = rest.split(INDEX_END, 1)
    text = f"{head}{INDEX_START}\n{index_body}{INDEX_END}{tail}"
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{body}{END}{tail}"
    changed = new != original
    if args.check and changed:
        sys.exit("README.md catalog drift: run python3 scripts/build-catalog.py")
    if changed:
        readme.write_text(new, encoding="utf-8")
    print(f"catalog: {len(on_disk)} skills, {sum(len(c.get('links', [])) for c in cat['categories'])} links, {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, yaml.YAMLError) as error:
        sys.exit(str(error))
