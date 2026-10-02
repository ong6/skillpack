#!/usr/bin/env python3
"""Editorial check for a Markdown deck in the create-fde-deck format.

Usage: python3 check_deck.py deck.md
Prints one line per finding. Exit 1 when any FLAG is found, 0 when only notes (or nothing) remain.
A density heuristic, not a measured overflow test, and no check of whether a claim is true.
Stdlib only, Python 3.7+.
"""
import re
import sys

LIMITS = {"findings": 6, "architecture": 5, "comparison": 3, "results": 4, "next-steps": 6}
TARGETS = {"findings": 4, "architecture": 4, "comparison": 2, "results": 3, "next-steps": 3}
SHAPES = {"title"} | set(LIMITS)
LABEL = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\*\*(Evidence|Assumption|Proposal)\*\*", re.I)
ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+\S")
COMMENT = re.compile(r"<!--.*?-->", re.S)


def visible_words(text):
    text = COMMENT.sub(" ", text)
    text = re.sub(r"^\s*\|?\s*:?-{3,}.*$", " ", text, flags=re.M)  # table separator rows
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(re.findall(r"[^\W_]+(?:['’.-][^\W_]+)*|\d+(?:[.,]\d+)*%?", text))


def split_slides(source):
    if source.startswith("---\n"):
        end = source.find("\n---\n", 4)
        front, body = (source[4:end], source[end + 5:]) if end != -1 else ("", source)
    else:
        front, body = "", source
    return front, [s for s in re.split(r"^---[ \t]*$", body, flags=re.M) if s.strip()]


def check(path):
    front, slides = split_slides(open(path, encoding="utf-8").read())
    flags, notes = [], []
    for key in ("title", "audience", "decision"):
        if not re.search(r"^%s:\s*\S" % key, front, re.M):
            flags.append("deck: frontmatter needs `%s:`" % key)
    if not 1 <= len(slides) <= 30:
        flags.append("deck: %d slides; keep 1-30 and split into separate decks beyond that" % len(slides))
    actions = 0
    for number, slide in enumerate(slides, 1):
        where = "slide %d" % number
        heading = re.search(r"^#{1,2}\s+(.+)$", slide, re.M)
        shape = re.search(r"<!--\s*shape:\s*([\w-]+)\s*-->", slide)
        shape = shape.group(1).lower() if shape else ("title" if number == 1 else None)
        if not heading:
            flags.append("%s: no takeaway headline (`#` or `##`)" % where)
        else:
            title = heading.group(1).strip()
            if len(title) > 95:
                flags.append("%s: headline is %d chars; keep it under 95" % (where, len(title)))
            elif number == 1 and len(title) > 60:
                notes.append("%s: opening headline is %d chars; aim under 60" % (where, len(title)))
        if shape not in SHAPES:
            flags.append("%s: add `<!-- shape: ... -->` (one of %s)" % (where, ", ".join(sorted(SHAPES))))
            continue
        words = visible_words(slide)
        if words > (65 if shape == "title" else 135):
            flags.append("%s: %d visible words over the %d heuristic; tighten or split" % (
                where, words, 65 if shape == "title" else 135))
        visible = COMMENT.sub("", slide).splitlines()
        slide_source = any(re.match(r"^\s*\*?Source:", line) for line in visible)
        items = [line for line in visible if ITEM.match(line)]
        rows = [line for line in visible if line.lstrip().startswith("|")
                and not re.match(r"^\s*\|?\s*:?-{3,}", line)][1:]
        count = {"comparison": len(re.findall(r"^###\s+\S", slide, re.M)),
                 "results": len(rows) or len(items)}.get(shape, len(items))
        if shape in LIMITS:
            if count == 0:
                flags.append("%s: %s slide has no content" % (where, shape))
            elif count > LIMITS[shape]:
                flags.append("%s: %d %s items; the limit is %d, split the slide" % (
                    where, count, shape, LIMITS[shape]))
            elif count > TARGETS[shape]:
                notes.append("%s: %d %s items; %d or fewer reads better" % (
                    where, count, shape, TARGETS[shape]))
        for line in items:
            label = LABEL.match(line)
            if shape == "findings" and not label:
                flags.append("%s: finding without an Evidence/Assumption/Proposal label: %s" % (
                    where, line.strip()[:60]))
            if label and label.group(1).lower() == "evidence" and "Source:" not in line and not slide_source:
                flags.append("%s: evidence without a source: %s" % (where, line.strip()[:60]))
        if shape == "results":
            for line in rows or items:
                if "Source:" not in line and not slide_source:
                    flags.append("%s: metric without provenance (source, sample, window): %s" % (
                        where, line.strip()[:60]))
        if shape == "next-steps":
            for line in items:
                actions += 1
                if "Owner:" not in line or "Date:" not in line:
                    flags.append("%s: action needs `Owner:` and `Date:`: %s" % (where, line.strip()[:60]))
    if not actions:
        flags.append("deck: no next-steps slide with an explicit action, owner and date")
    for line in flags:
        print("FLAG  " + line)
    for line in notes:
        print("note  " + line)
    print("%d flags, %d notes, %d slides. Heuristic only: render and inspect every slide to claim fit."
          % (len(flags), len(notes), len(slides)))
    return 1 if flags else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip().splitlines()[2])
    sys.exit(check(sys.argv[1]))
