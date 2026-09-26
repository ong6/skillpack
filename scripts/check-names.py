#!/usr/bin/env python3
"""Validate action-object names in a skill collection or a host's canonical skills."""

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def load_policy(path):
    policy = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or policy.get("version") != 1:
        raise ValueError("naming policy version must be 1")
    for field in ("actions", "filler_tokens"):
        values = policy.get(field)
        if (not isinstance(values, list) or not values
                or any(not isinstance(value, str) or not re.fullmatch(r"[a-z]+", value) for value in values)
                or len(values) != len(set(values))):
            raise ValueError(f"naming policy {field} must contain unique lowercase words")
    for field in ("maximum_tokens", "maximum_characters"):
        if type(policy.get(field)) is not int or policy[field] < 2:
            raise ValueError(f"naming policy {field} must be an integer of at least 2")
    return policy


def validate_name(name, policy):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", name):
        return "use lowercase verb-object kebab-case with at least two words"
    parts = name.split("-")
    if len(name) > policy["maximum_characters"] or len(parts) > policy["maximum_tokens"]:
        return "name exceeds the policy length limit"
    if parts[0] not in policy["actions"]:
        return f"start with a recognized action verb; {parts[0]!r} is not in naming.json"
    if any(part in policy["filler_tokens"] for part in parts[1:]):
        return "remove filler articles (a, an, the)"
    return None


def load_legacy_map(path):
    if path is None or not path.is_file():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    mapping = value.get("legacy_names") if isinstance(value, dict) else None
    if not isinstance(mapping, dict) or any(
        not isinstance(old, str) or not isinstance(new, str) for old, new in mapping.items()
    ):
        raise ValueError("legacy map must contain a legacy_names string mapping")
    return mapping


def legacy_references(text, mapping):
    found = []
    for old, new in mapping.items():
        escaped = re.escape(old)
        patterns = (
            rf"(?<![a-z0-9-])[$/]{escaped}(?![a-z0-9-])",
            rf"(?:\.claude/skills|\.agents/skills|\.claude/shared-skills/skills)/{escaped}(?:/|\b)",
            rf"\.\./{escaped}/SKILL\.md",
            rf"\((?:`)?{escaped}(?:`)?\)",
        )
        if any(re.search(pattern, text) for pattern in patterns):
            found.append((old, new))
    return found


def check_directory(directory, policy, legacy=None):
    if not directory.is_dir():
        return [f"skill directory does not exist: {directory}"], 0
    errors, seen, count = [], {}, 0
    for folder in sorted(directory.iterdir()):
        if folder.name.startswith("."):
            continue
        if folder.is_symlink() and not folder.exists():
            errors.append(f"{folder.name}: broken skill link")
            continue
        if not folder.is_dir():
            continue
        skill = folder / "SKILL.md"
        if not skill.is_file():
            errors.append(f"{folder.name}: missing SKILL.md")
            continue
        count += 1
        text = skill.read_text(encoding="utf-8")
        front = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
        names = re.findall(r"^name:\s*([^\r\n]+)$", front[1], re.M) if front else []
        if len(names) != 1:
            errors.append(f"{folder.name}: frontmatter needs exactly one name")
            continue
        name = names[0].strip().strip("\"'")
        reason = validate_name(name, policy)
        if reason:
            errors.append(f"{folder.name}: {reason}")
        if name != folder.name:
            errors.append(f"{folder.name}: frontmatter name {name!r} must match folder")
        if name in seen:
            errors.append(f"{folder.name}: duplicate skill identity also exposed at {seen[name]}")
        seen[name] = folder.name
        for old, new in legacy_references(text, legacy or {}):
            errors.append(f"{folder.name}: legacy skill reference {old!r}; use {new!r}")
        metadata = folder / "agents" / "openai.yaml"
        if metadata.is_file():
            prompts = re.findall(r"^\s*default_prompt:\s*(.*)$", metadata.read_text(encoding="utf-8"), re.M)
            commands = re.findall(r"\$([a-z0-9]+(?:-[a-z0-9]+)*)", " ".join(prompts))
            if commands and name not in commands:
                errors.append(f"{folder.name}: default_prompt must invoke its own ${name} identifier")
    if count == 0:
        errors.append("no skill manifests found")
    return errors, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, default=ROOT / "skills")
    parser.add_argument("--policy", type=Path, default=ROOT / "naming.json")
    parser.add_argument("--legacy-map", type=Path)
    args = parser.parse_args()
    try:
        errors, count = check_directory(
            args.skills_dir, load_policy(args.policy), load_legacy_map(args.legacy_map)
        )
    except (OSError, ValueError, TypeError) as exc:
        print(f"naming check: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"naming: {count} skills use verb-object identifiers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
