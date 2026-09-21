#!/usr/bin/env python3
"""Regenerate the catalog tables in README.md from catalog.yaml and each SKILL.md's frontmatter.

Run from anywhere: python3 scripts/build-catalog.py. Exit 1 if a listed skill folder is missing
or a skill folder exists that no category lists, so the catalog can't drift from the tree.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_START, INDEX_END = "<!-- SKILL INDEX START -->", "<!-- SKILL INDEX END -->"
START, END = "<!-- CATALOG START -->", "<!-- CATALOG END -->"


def frontmatter(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit(f"{path}: no frontmatter")
    data = yaml.safe_load(m.group(1)) or {}
    return data.get("name", path.parent.name), " ".join(str(data.get("description", "")).split())


def main():
    cat = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    on_disk = {p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()}
    listed = {s for c in cat["categories"] for s in c.get("skills", [])}
    summaries = cat.get("skill_summaries", {})
    missing, unlisted = listed - on_disk, on_disk - listed
    summary_missing, summary_extra = on_disk - summaries.keys(), summaries.keys() - on_disk
    if missing or unlisted or summary_missing or summary_extra:
        sys.exit(
            f"catalog drift: missing on disk {sorted(missing)}, not in catalog {sorted(unlisted)}, "
            f"missing summaries {sorted(summary_missing)}, extra summaries {sorted(summary_extra)}"
        )

    ordered_skills = [s for c in cat["categories"] for s in c.get("skills", [])]
    index = ["| Skill | What I use it for |", "|---|---|"]
    for s in ordered_skills:
        name, _ = frontmatter(ROOT / "skills" / s / "SKILL.md")
        index.append(f"| [`{name}`](skills/{s}/SKILL.md) | {summaries[s]} |")
    index_body = "\n".join(index) + "\n"

    out = []
    for c in cat["categories"]:
        out.append(f"### {c['title']}\n\n_{c['blurb']}_\n")
        if c.get("skills"):
            out.append("| Skill | Does |\n|---|---|")
            for s in c["skills"]:
                name, desc = frontmatter(ROOT / "skills" / s / "SKILL.md")
                out.append(f"| [`{name}`](skills/{s}/SKILL.md) | {desc} |")
            out.append("")
        if c.get("links"):
            out.append("Elsewhere:\n")
            for l in c["links"]:
                out.append(f"- [{l['repo']}](https://github.com/{l['repo']}) — {l['note']}")
            out.append("")
    body = "\n".join(out).rstrip() + "\n"

    readme = ROOT / "README.md"
    text = readme.read_text()
    if INDEX_START not in text or INDEX_END not in text or START not in text or END not in text:
        sys.exit("README.md lacks generated section markers")
    head, rest = text.split(INDEX_START, 1)
    _, tail = rest.split(INDEX_END, 1)
    text = f"{head}{INDEX_START}\n{index_body}{INDEX_END}{tail}"
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{body}{END}{tail}"
    changed = new != text
    readme.write_text(new)
    print(f"catalog: {len(on_disk)} skills, {sum(len(c.get('links', [])) for c in cat['categories'])} links, {'updated' if changed else 'unchanged'}")


if __name__ == "__main__":
    main()
