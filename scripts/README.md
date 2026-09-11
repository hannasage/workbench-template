---
type: index
updated: 2026-09-11
---

# scripts

The flat home for everything executable that is not part of a skill or a
project repo.

`central-context/` holds no code, by rule. When a check there needs to run
rather than be read, it lives here and `central-context/AGENTS.md` names it by
path.

A script that belongs to one skill stays with that skill, under
`skills/<name>/`. A script that belongs to one project stays in that project's
repo. Everything else is here.

| Script | Does | Run from |
|---|---|---|
| `check-roles.py` | Checks agent and skill frontmatter | The workbench root: `python3 scripts/check-roles.py` |
| `model-registry.txt` | Data, not a script. The values `check-roles.py` accepts in a role's `model:` field | Read by `check-roles.py` |

## check-roles.py

Claude Code skips a malformed role file in silence, so this is the only thing
that reports one.

On roles it checks that frontmatter exists with `---` as the first line, that
`name` matches the filename and is lowercase-hyphen, that `description` is not
empty, that `model` is registered, and that every skill named in `skills:`
exists. On skills it checks that a `SKILL.md` sits directly under
`skills/<dir>/` and not deeper, that no skill directory is empty, that `name`
matches the directory and is lowercase-hyphen, and that `description` is not
empty.

Two things it reports separately:

- **A failure** is a defect. Fix the file.
- **A question** is a `model:` value that is not in `model-registry.txt`.
  Claude Code publishes no grammar for a model ID, so the script cannot tell a
  typo from a model nobody has registered. It asks instead of ruling. Fix the
  typo, or add a line to the registry with its provenance.

Both count toward the exit code, which is their total, capped at 125. That
makes it usable as a pre-commit hook with no wrapper. Nothing calls it
automatically yet. Wiring it into one is a decision for this workbench; open
an item in `AGENTS.md` if you want it tracked.

`THIRD_PARTY_SKILLS` in the script exempts an installed skill whose `name`
differs from the directory it was installed into. That is an exemption from a
published standard, not from a house convention: the Agent Skills
specification, `https://agentskills.io/specification`, read 2026-09-11, states
the `name` field "Must match the parent directory name". A listed skill does
not conform. Claude Code invokes an installed skill by directory name, so it
still loads, and the exemption is a decision to tolerate a non-conforming file
somebody else wrote. Everything not listed there is checked, so a skill you
wrote is never skipped by forgetting to register it.

The same specification sets the other name rules the script enforces: 1 to 64
characters, lowercase alphanumeric and hyphens, no leading or trailing hyphen,
no consecutive hyphens. It also publishes a validator, `skills-ref validate`,
which checks a single skill and not the roles, the nesting, or the tree shape
this script covers.

Tests are at `tests/`, run with `python3 -m unittest discover -s scripts/tests`
from the workbench root. What they cover is described in `check-roles.py`'s own
module docstring and above. This template ships no `SPEC.md`; write one when a
change needs acceptance criteria of its own.

