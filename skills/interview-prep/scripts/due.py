#!/usr/bin/env python3
"""Pick the next DSA pattern from bank.md and show which plan element keeps breaking.

Usage: python3 due.py [STATE_DIR] [--today YYYY-MM-DD]
STATE_DIR defaults to $INTERVIEW_PREP_HOME. Stdlib only, Python 3.7+.

Selection order: overdue Tier A (oldest due first), overdue Tier B, never-drilled patterns
(Tier A first, preferring ones that require the most-missed element), then the pattern with the
most failed/half rows in the last 30 days. Never the pattern of the previous bank row.
"""
import argparse
import collections
import datetime
import os
import re
import sys

DAY_BOUNDARY_HOUR = 3  # a rep logged at 1am belongs to the previous day
HERE = os.path.dirname(os.path.abspath(__file__))
PATTERNS = os.path.join(HERE, "..", "references")


def load_patterns():
    """Map pattern id -> (tier, required elements) from the pattern references' frontmatter."""
    patterns = {}
    for name in sorted(os.listdir(PATTERNS)):
        if not (name.startswith("pattern-") and name.endswith(".md")):
            continue
        with open(os.path.join(PATTERNS, name), encoding="utf-8") as handle:
            head = handle.read().split("---")[1]
        fields = dict(re.findall(r"^(\w+):\s*(.+)$", head, re.M))
        elements = [e.strip() for e in fields.get("required_elements", "").strip("[]").split(",")]
        patterns[fields["id"].strip()] = (fields.get("tier", "B").strip(), [e for e in elements if e])
    return patterns


def load_bank(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            cells = [c.strip() for c in line.strip().strip("|").split("|", 5)]
            if len(cells) < 5 or not re.match(r"^\d{4}-\d{2}-\d{2}$", cells[0]):
                continue
            missing = [] if cells[3] in ("", "-") else [m.strip() for m in cells[3].split(",")]
            rows.append({"date": cells[0], "pattern": cells[1], "verdict": cells[2],
                         "missing": missing, "due": cells[4]})
    return rows


def days(a, b):
    return (datetime.date.fromisoformat(a) - datetime.date.fromisoformat(b)).days


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("state_dir", nargs="?", default=os.environ.get("INTERVIEW_PREP_HOME"))
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    args = parser.parse_args()
    if not args.state_dir:
        sys.exit("pass the state folder or set INTERVIEW_PREP_HOME")
    now = datetime.datetime.now() - datetime.timedelta(hours=DAY_BOUNDARY_HOUR)
    today = args.today or now.date().isoformat()
    patterns = load_patterns()
    rows = load_bank(os.path.join(os.path.expanduser(args.state_dir), "bank.md"))

    latest = {}
    for row in rows:  # file order is append order; a later row supersedes an earlier one
        if row["pattern"] not in latest or row["date"] >= latest[row["pattern"]]["date"]:
            latest[row["pattern"]] = row
    previous = rows[-1]["pattern"] if rows else None

    histogram = collections.Counter()
    seen_under = collections.defaultdict(set)
    for row in rows:
        if days(today, row["date"]) <= 60:
            for element in row["missing"]:
                histogram[element] += 1
                seen_under[element].add(row["pattern"])
    top = histogram.most_common(1)[0][0] if histogram else None

    def tier(pid):
        return patterns.get(pid, ("B", []))[0]

    overdue = sorted((r for r in latest.values() if r["due"] <= today),
                     key=lambda r: (tier(r["pattern"]) != "A", r["due"]))
    never = sorted((p for p in patterns if p not in latest),
                   key=lambda p: (tier(p) != "A", top not in patterns[p][1], p))
    weak = collections.Counter(r["pattern"] for r in rows
                               if r["verdict"] in ("failed", "half") and days(today, r["date"]) <= 30)
    order = [r["pattern"] for r in overdue] + never + [p for p, _ in weak.most_common()]
    choice = next((p for p in order if p != previous), None)

    print("today: %s (day boundary %02d:00)" % (today, DAY_BOUNDARY_HOUR))
    print("next: %s%s" % (choice or "nothing due; candidate's choice",
                          "  (skipped %s: previous row)" % previous if order and order[0] == previous else ""))
    if overdue:
        print("due:")
        for r in overdue:
            print("  %-24s tier %s  due %s  %3dd overdue  last %s (%s)" % (
                r["pattern"], tier(r["pattern"]), r["due"], days(today, r["due"]), r["verdict"],
                ", ".join(r["missing"]) or "-"))
    if never:
        print("never drilled: " + ", ".join("%s (%s)" % (p, tier(p)) for p in never))
    if histogram:
        print("missing elements, last 60 days:")
        for element, count in histogram.most_common(5):
            print("  %-18s x%d  under %s" % (element, count, ", ".join(sorted(seen_under[element]))))
        repeat = [e for e in histogram if len(seen_under[e]) >= 3]
        if repeat:
            print("cross-pattern: %s missing on 3+ different patterns; say so once" % ", ".join(repeat))
    unknown = sorted(set(latest) - set(patterns))
    if unknown:
        print("rows with unknown pattern ids: " + ", ".join(unknown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
