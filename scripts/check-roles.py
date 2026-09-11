#!/usr/bin/env python3
"""Check agent role files and skill files for the frontmatter Claude Code needs.

Run from the container root:

    python3 scripts/check-roles.py

Checks, in order:

1. Every agents/*.md has YAML frontmatter with a name that matches the
   filename, is lowercase with hyphens, has a description, and if it names
   a model, the model is a known alias. Every skill it names exists under
   skills/.
2. Every skills/*/SKILL.md has frontmatter with a name that matches its
   directory and a description.

A third-party skill may ship a name that does not match the directory it was
installed into. Add those directory names to THIRD_PARTY_SKILLS below to exempt
them. Everything else is checked, so a skill you wrote never gets skipped by
forgetting to register it.

Exit code is the number of failures, capped at 125.

Claude Code skips a malformed role file silently, so this is the only thing
that tells you a role did not load. Standard library only.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = {"sonnet", "opus", "haiku", "inherit"}

# Directories holding a skill somebody else wrote, whose `name` may not match
# the directory it was installed into. Add one line per installed third-party
# skill. Everything not listed here is checked.
THIRD_PARTY_SKILLS = set()
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def frontmatter(text):
    """Return the frontmatter as a dict of top-level scalar keys, or None."""
    match = FRONT_RE.match(text)
    if not match:
        return None
    fields = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return fields


def check_agents(failures):
    skills_dir = ROOT / "skills"
    for path in sorted((ROOT / "agents").glob("*.md")):
        if path.name == "README.md":
            continue
        fields = frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT)
        if fields is None:
            failures.append(f"{rel}: no frontmatter")
            continue
        name = fields.get("name", "")
        if name != path.stem:
            failures.append(f"{rel}: name '{name}' does not match filename")
        if not NAME_RE.match(name):
            failures.append(f"{rel}: name '{name}' is not lowercase-hyphen")
        if not fields.get("description"):
            failures.append(f"{rel}: no description")
        model = fields.get("model")
        if model and model not in MODELS:
            failures.append(f"{rel}: model '{model}' is not a known alias")
        for skill in filter(None, (s.strip() for s in fields.get("skills", "").split(","))):
            if not (skills_dir / skill / "SKILL.md").is_file():
                failures.append(f"{rel}: skill '{skill}' has no skills/{skill}/SKILL.md")


def check_skills(failures):
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        fields = frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT)
        if fields is None:
            failures.append(f"{rel}: no frontmatter")
            continue
        name = fields.get("name", "")
        if name != path.parent.name and path.parent.name not in THIRD_PARTY_SKILLS:
            failures.append(f"{rel}: name '{name}' does not match directory")
        if not fields.get("description"):
            failures.append(f"{rel}: no description")


def main():
    failures = []
    check_agents(failures)
    check_skills(failures)
    for failure in failures:
        print(failure)
    print(f"{len(failures)} failure(s)")
    return min(len(failures), 125)


if __name__ == "__main__":
    sys.exit(main())
