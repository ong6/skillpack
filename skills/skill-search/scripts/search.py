#!/usr/bin/env python3
"""Search every skill tier (core, rarely used, retired) and the catalog's external links.

Usage: python3 search.py WORDS... [--json] [--limit N]

Runs `bin/skills find` from the skills checkout: $SKILLS_HOME when set, else the checkout this
skill folder lives in. Resolving this file's own path is deliberate here: the tool belongs to
the checkout, not to a sibling skill. Stdlib only, Python 3.7+.
"""
import os
import sys


def find_tool():
    candidates = []
    if os.environ.get("SKILLS_HOME"):
        candidates.append(os.path.join(os.environ["SKILLS_HOME"], "bin", "skills"))
    here = os.path.dirname(os.path.realpath(__file__))  # <checkout>/skills/skill-search/scripts
    candidates.append(os.path.join(here, "..", "..", "..", "bin", "skills"))
    for path in candidates:
        if os.path.isfile(path):
            return os.path.normpath(path)
    return None


def main():
    tool = find_tool()
    if not tool:
        sys.stderr.write("skill-search: bin/skills not found; set SKILLS_HOME to the skills checkout\n")
        return 2
    os.execv(sys.executable, [sys.executable, tool, "find"] + sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
