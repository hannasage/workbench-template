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
| `check-roles.py` | Checks the frontmatter of every role in `agents/` and every skill in `skills/` | The workbench root: `python3 scripts/check-roles.py` |

`check-roles.py` exits with the number of failures, so it works as a pre-commit
hook without wrapping. Nothing calls it automatically; the root `AGENTS.md`
names it as a manual step before any commit that touches `agents/` or
`skills/`.
