#!/usr/bin/env python3
"""Check agent role files and skill files for the frontmatter a harness needs.

A harness is the program that runs the agent loop and reads these files.

Run from the workbench root:

    python3 scripts/check-roles.py

An optional argument checks a different tree, which is what the tests use:

    python3 scripts/check-roles.py /path/to/a/fixture/root

A harness skips a malformed role file in silence, so this is the only thing
that reports one.

Roles, every `agents/*.md` except `README.md`:

1. Frontmatter exists, and `---` is the first line of the file. A harness
   reads frontmatter only then; a leading blank line or a byte order mark turns
   the whole file into body text. A closing `---` at the end of the file with
   no trailing newline is fine.
2. `name` matches the filename and is lowercase letters, digits and single
   hyphens.
3. `description` is not empty. It is what the model routes on.
4. `model`, if named, is in `scripts/model-registry.txt`. A value that is not
   registered is reported as a question, never as an error. See below. No role
   file here names a model, because a model identifier is a harness fact and
   the neutral core holds none. This rule fires for a cloner who pins one.
5. Every skill in `skills:` has a readable `skills/<name>/SKILL.md`. An
   entry of that name that is a directory or a dangling symlink is reported
   as such, not as a missing file.

   `skills:` is written on one line, comma separated. That is the only
   accepted form. Every other form YAML permits for the same field is reported
   and none is read: a block list, a value that runs past its own line in any
   shape, a flow list, and an empty flow list. Declaring one form is a smaller
   promise than parsing several, and a refused form that names itself beats one
   silently dropped.

Skills, every directory directly under `skills/`:

6. A `SKILL.md` that sits deeper than `skills/<dir>/SKILL.md` is reported. A
   skill nested one level too deep is not discovered, and nothing else says so.
7. A directory with no skill file of its own is reported. Dot directories are
   not.
8. `name` matches the directory, unless the directory is in THIRD_PARTY_SKILLS.
   An installed skill may legitimately carry a name that differs from the
   directory it was installed into.
9. `name` is lowercase letters, digits and single hyphens, and at most 64
   characters. Both rules come from the Agent Skills specification and both run
   on exempt skills.
10. `description` is not empty.

The tree itself:

11. `agents/` and `skills/` exist at the checked root. Without this the script
    reports a clean tree when it is looking at the wrong directory, which as a
    commit gate is the worst thing it could do.

Failures and questions both count toward the exit code, which is their total,
capped at 125, so this works as a pre-commit hook with no wrapper. A question
blocks in the same way a failure does, because both are resolved by one edit
and neither should reach a commit unexamined.

Every path that cannot be read is reported as a failure naming the path. The
script never raises on a tree shape.

Standard library only.
"""

import re
import sys
from pathlib import Path

MODEL_REGISTRY = "scripts/model-registry.txt"

# Directories under skills/ holding a skill somebody else wrote, whose `name`
# does not match the directory it was installed into.
#
# This is an exemption from a published standard, not from a house convention.
# The Agent Skills specification, https://agentskills.io/specification, read
# 2026-09-11, states the `name` field "Must match the parent directory name".
# A skill listed here does not conform. A harness invokes an installed skill
# by its directory name, so it still loads, but the file is non-conforming and
# the exemption is a decision to tolerate that in somebody else's file rather
# than a statement that the rule does not apply.
THIRD_PARTY_SKILLS = set()

# Agent Skills specification, https://agentskills.io/specification, read
# 2026-09-11: 1 to 64 characters, lowercase alphanumeric and hyphens, no
# leading or trailing hyphen, no consecutive hyphens. The pattern covers every
# rule except the length, which is checked separately.
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
# The closing fence may end the file, so the trailing newline is optional. A
# file whose last byte is the final `-` is valid and must not be reported.
FRONT_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.S)
SKILL_FILE = "SKILL.md"
BOM = "﻿"


def parse(path, rel, failures):
    """Frontmatter of one file, or None after saying why not.

    Returns (fields, lists, continued). `fields` holds top-level scalars.
    `lists` holds the items of any key written as an indented block list, and
    `continued` names every key followed by an indented line of any shape.

    Neither `lists` nor `continued` exists so a value can be parsed out of
    them. They exist so a caller can refuse a form and say which one it was.
    A key whose value runs past its own line is not read here.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        failures.append(f"{rel}: cannot be read, {type(exc).__name__}")
        return None
    except UnicodeDecodeError:
        failures.append(f"{rel}: is not UTF-8 text")
        return None
    if text.startswith(BOM):
        failures.append(f"{rel}: starts with a byte order mark, so --- is not the first thing in it")
        return None
    match = FRONT_RE.match(text)
    if not match:
        failures.append(f"{rel}: no frontmatter, or --- is not the first line")
        return None
    fields, lists, continued, key = {}, {}, set(), None
    for line in match.group(1).splitlines():
        if not line.strip():
            continue  # a blank line does not end the block it sits inside
        if line.startswith((" ", "\t")):
            if key:
                continued.add(key)
                item = line.strip()
                if item.startswith("- "):
                    lists.setdefault(key, []).append(item[2:].strip().strip('"').strip("'"))
            continue
        if ":" not in line:
            key = None
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        fields[key] = value.strip().strip('"')
    return fields, lists, continued


def named_skills(fields, lists, continued, rel, failures):
    """Skill names from `skills:`. Inline, comma separated, and nothing else.

    YAML also permits a flow list and an indented block list. Supporting all
    three means three parsers and three ways to be subtly wrong, which is how
    this checker accumulated its defects. One form is declared here; the other
    two are reported by name rather than parsed or, worse, silently dropped.
    """
    if "skills" in lists:
        failures.append(
            f"{rel}: skills: is a block list. Write it on one line, comma "
            f"separated: skills: alpha, beta"
        )
        return []
    if "skills" in continued:
        failures.append(
            f"{rel}: skills: runs past its own line. Write it on one line, "
            f"comma separated: skills: alpha, beta"
        )
        return []
    raw = fields.get("skills", "").strip()
    if raw in ("[]", "[ ]"):
        failures.append(f"{rel}: skills: is empty. Delete the line.")
        return []
    if raw.startswith("[") or raw.endswith("]"):
        failures.append(
            f"{rel}: skills: is a flow list. Write it on one line, comma "
            f"separated, with no brackets: skills: alpha, beta"
        )
        return []
    return [n.strip().strip('"').strip("'") for n in raw.split(",") if n.strip()]


def load_models(root, failures):
    """The set of accepted model values, or None if the file cannot be read."""
    path = root / MODEL_REGISTRY
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        failures.append(f"{MODEL_REGISTRY}: missing or unreadable, so no model can be checked")
        return None
    except UnicodeDecodeError:
        failures.append(f"{MODEL_REGISTRY}: is not UTF-8 text, so no model can be checked")
        return None
    values = set()
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            values.add(line)
    return values


def skill_file(directory):
    """Return (path, problem) for the SKILL.md directly inside a directory.

    A name match alone is not enough: the entry may be a directory or a
    dangling symlink, and the caller is about to read it. Absent and present
    but unreadable are different faults and get different messages.
    """
    if not directory.is_dir():
        return None, f"no {SKILL_FILE}"
    named = [e for e in directory.iterdir() if e.name == SKILL_FILE]
    if not named:
        return None, f"no {SKILL_FILE}"
    if not named[0].is_file():
        return None, f"{SKILL_FILE} is not a readable file"
    return named[0], None


def check_agents(root, models, failures, questions):
    agents_dir = root / "agents"
    if not agents_dir.is_dir():
        failures.append("agents: no such directory at the checked root")
        return
    skills_dir = root / "skills"
    for path in sorted(agents_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(root)
        parsed = parse(path, rel, failures)
        if parsed is None:
            continue
        fields, lists, continued = parsed
        name = fields.get("name", "")
        if name != path.stem:
            failures.append(f"{rel}: name '{name}' does not match filename")
        if not NAME_RE.match(name):
            failures.append(f"{rel}: name '{name}' is not lowercase-hyphen")
        if not fields.get("description"):
            failures.append(f"{rel}: no description")
        model = fields.get("model")
        if model and models is not None and model not in models:
            questions.append(
                f"{rel}: model '{model}' is not registered. A typo, or a model "
                f"to add to {MODEL_REGISTRY}?"
            )
        for skill in named_skills(fields, lists, continued, rel, failures):
            skill_path, problem = skill_file(skills_dir / skill)
            if skill_path is None:
                failures.append(f"{rel}: skill '{skill}': skills/{skill}/{problem}")


def check_skills(root, failures):
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        failures.append("skills: no such directory at the checked root")
        return
    for directory in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        if directory.name.startswith("."):
            continue
        rel = directory.relative_to(root)

        # A skill file below skills/<dir>/ is not discovered, whatever it says.
        nested = sorted(
            p for p in directory.rglob(SKILL_FILE)
            if p.name == SKILL_FILE and p.parent != directory
        )
        for path in nested:
            failures.append(
                f"{path.relative_to(root)}: nested below skills/{directory.name}/, "
                f"so this skill is not discovered"
            )

        path, problem = skill_file(directory)
        if path is None:
            if not nested:
                failures.append(f"{rel}: {problem}")
            continue

        rel_file = path.relative_to(root)
        parsed = parse(path, rel_file, failures)
        if parsed is None:
            continue
        fields = parsed[0]
        name = fields.get("name", "")
        if name != directory.name and directory.name not in THIRD_PARTY_SKILLS:
            failures.append(f"{rel_file}: name '{name}' does not match directory")
        if not NAME_RE.match(name):
            failures.append(f"{rel_file}: name '{name}' is not lowercase-hyphen")
        if len(name) > NAME_MAX:
            failures.append(f"{rel_file}: name is {len(name)} characters, over the {NAME_MAX} the spec allows")
        if not fields.get("description"):
            failures.append(f"{rel_file}: no description")


def run(root):
    """Check one tree. Returns (failures, questions), each a list of lines."""
    root = Path(root)
    failures, questions = [], []
    models = load_models(root, failures)
    check_agents(root, models, failures, questions)
    check_skills(root, failures)
    return sorted(failures), sorted(questions)


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    failures, questions = run(root)
    for line in failures:
        print(line)
    if questions:
        if failures:
            print()
        print("Questions. Each one is a typo or a model nobody has registered yet:")
        for line in questions:
            print(line)
        print()
    print(f"{len(failures)} failure(s)")
    if questions:
        print(f"{len(questions)} question(s)")
    return min(len(failures) + len(questions), 125)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
