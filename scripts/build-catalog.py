#!/usr/bin/env python3
"""Regenerate the catalog tables in README.md from catalog.yaml and each SKILL.md's frontmatter.

Skills live in `skills/<name>` (core, linked by bin/skills) or `rarely-used/<name>` (unused for a
month, not linked); both are listed, the second marked. Run from anywhere:
python3 scripts/build-catalog.py. Use --check to verify without writing. Exit 1 if metadata is
invalid or, in check mode, the generated README has drifted.
"""
import argparse
from collections import Counter
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TIERS = ("skills", "rarely-used")
SHELF_NOTE = " _(rarely used)_"
LINK_FIELDS = {"repo", "url", "name", "by", "note", "tags", "from", "from_url"}
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
            context = f"category {c['key']}: link {link.get('name') or link.get('repo') or link.get('url')}"
            unknown = set(link) - LINK_FIELDS
            if unknown:
                sys.exit(f"{context}: unknown field(s) {sorted(unknown)}")
            if bool(link.get("repo")) == bool(link.get("url")):
                sys.exit(f"{context}: give exactly one of repo or url")
            if link.get("repo") and not re.fullmatch(r"[\w.-]+/[\w.-]+", str(link["repo"])):
                sys.exit(f"{context}: repo must be owner/name")
            if link.get("url") and not str(link["url"]).startswith("https://"):
                sys.exit(f"{context}: url must start with https://")
            require_text(link.get("note"), f"{context}: note")
            for field in ("name", "by", "from"):
                if field in link:
                    require_text(link[field], f"{context}: {field}")
            if "from_url" in link and not str(link["from_url"]).startswith("https://"):
                sys.exit(f"{context}: from_url must start with https://")
            if "from_url" in link and "from" not in link:
                sys.exit(f"{context}: from_url needs from")
            tags = link.get("tags", [])
            if not isinstance(tags, list) or any(not isinstance(t, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", t)
                                                 for t in tags):
                sys.exit(f"{context}: tags must be a list of kebab-case words")
    ordered_skills = [s for c in cat["categories"] for s in c.get("skills", [])]
    duplicates = sorted(s for s, count in Counter(ordered_skills).items() if count > 1)
    if duplicates:
        sys.exit(f"skills must appear in exactly one category: {duplicates}")
    tier_of = {}
    for tier in TIERS:
        base = ROOT / tier
        skill_dirs = [p for p in base.iterdir() if p.is_dir()] if base.is_dir() else []
        incomplete = sorted(f"{tier}/{p.name}" for p in skill_dirs if not (p / "SKILL.md").is_file())
        if incomplete:
            sys.exit(f"skill folders missing SKILL.md: {incomplete}")
        for p in skill_dirs:
            if p.name in tier_of:
                sys.exit(f"skill {p.name} is in both skills/ and rarely-used/")
            tier_of[p.name] = tier
    on_disk = set(tier_of)
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
    pinned = cat.get("pinned", [])
    if not isinstance(pinned, list) or any(p not in on_disk for p in pinned):
        sys.exit(f"catalog.yaml: pinned must list skills that exist, got {pinned!r}")
    if any(tier_of[p] != "skills" for p in pinned):
        sys.exit("catalog.yaml: a pinned skill must stay in skills/")
    metadata = {s: frontmatter(ROOT / tier_of[s] / s / "SKILL.md") for s in ordered_skills}

    def entry(s):
        name, _ = metadata[s]
        return f"[`{name}`]({tier_of[s]}/{s}/SKILL.md)" + (SHELF_NOTE if tier_of[s] != "skills" else "")

    index = ["| Skill | What I use it for |", "|---|---|"]
    for s in ordered_skills:
        index.append(f"| {entry(s)} | {cell(summaries[s])} |")
    index_body = "\n".join(index) + "\n"

    out = []
    for c in cat["categories"]:
        out.append(f"### {c['title']}\n\n_{c['blurb']}_\n")
        if c.get("skills"):
            out.append("| Skill | Does |\n|---|---|")
            for s in c["skills"]:
                _, desc = metadata[s]
                out.append(f"| {entry(s)} | {cell(desc)} |")
            out.append("")
        if c.get("links"):
            out.append("Elsewhere:\n")
            for l in c["links"]:
                url = l.get("url") or f"https://github.com/{l['repo']}"
                label = l.get("name") or l.get("repo") or url
                seen = ""
                if l.get("from"):
                    seen = f" Seen in [{l['from']}]({l['from_url']})." if l.get("from_url") else f" Seen in {l['from']}."
                by = f" by {l['by']}" if l.get("by") else ""
                out.append(f"- [{label}]({url}){by} — {' '.join(l['note'].split())}{seen}")
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
