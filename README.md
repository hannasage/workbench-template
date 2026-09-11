# workbench-template

A starting structure for a Claude Code workbench built around an LLM wiki:
a knowledge base an agent compiles from sources and keeps current, plus the
agent roles and skills that maintain it.

Clone it, run one setup pass, and you have a second brain your agents read
before every task and correct when the world moves.

## What is in here

```
workbench/
  AGENTS.md            the entrypoint. Read at the start of every session
  CLAUDE.md            symlink to AGENTS.md
  DECISIONS.md         append-only decision log
  .gitignore           project repos you nest here stay untracked
  agents/              14 role definitions, all examples
  skills/              12 skills: five that run the wiki, seven that run research
  scripts/             check-roles.py, and anything else executable
  prompts/             setup.md, and prompts you paste in on purpose
  central-context/     the knowledge base
    raw/               sources, immutable, written by a person
    wiki/              pages compiled from raw/, written by the agent
    docs/              research deliverables, outside the wiki pattern
    AGENTS.md          the schema: layout, page types, frontmatter, operations
    index.md           the catalog, one line per page
    log.md             append-only, one line per operation
```

The rule that makes it work: a source enters `raw/` once and is never edited.
An agent reads it and compiles what it says into `wiki/`. Questions are
answered from `wiki/`, with a citation, not from the sources and not from
memory. Knowledge is compiled once instead of re-derived on every question.

The pattern is Andrej Karpathy's LLM wiki, published April 2026. The five
operations, the open-items schema, and the verify pass are this template's own.

## The five wiki operations

| Skill | Runs when |
|---|---|
| `wiki-ingest` | A new file lands in `raw/` |
| `wiki-query` | Someone asks what is known |
| `wiki-lint` | Before a commit. Checks the wiki against itself |
| `wiki-verify` | On a cadence. Checks the wiki against the disk, git, and the calendar |
| `wiki-open-items` | At the start of a task. Surfaces questions nobody has settled |

Lint catches a wiki that is inconsistent. Verify catches a wiki that is merely
old, which is the failure that actually happens.

## Getting started

```bash
git clone https://github.com/hannasage/workbench-template.git my-workbench
cd my-workbench
claude
```

Then paste `prompts/setup.md` into the session. It interviews you, fills in
every placeholder, walks you through which example roles to keep, and ingests
your first real source so you have seen the loop run once.

Setup takes one sitting. Skipping it leaves a workbench that describes someone
else's business.

## The examples are examples

Every file in `agents/` and every research skill in `skills/` came out of one
working practice. The shape transfers. The opinions inside them do not: they
name a writing standard, a buyer segment, and a jurisdiction that are not
yours.

Three sections are left deliberately empty rather than filled with someone
else's answer, because a wrong one reads as settled:

- the buyer segment and the records of authority in `prospect-research`
- the compliance calendar in `quarterly-planning`
- the always-on rules 2, 3 and 9 in `AGENTS.md`

`prompts/setup.md` covers all three. Until they are filled, `AGENTS.md` carries
an open item that says so, and any session that reads the entrypoint will
surface it.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3 for `scripts/check-roles.py`
- Git

No build step, no dependencies, no install.

## Conventions worth knowing before you edit

- A skill is discovered only when its directory sits directly under `skills/`
  with a `SKILL.md` inside. Nesting one level deeper disables it silently.
- `.claude/agents` and `.claude/skills` are symlinks to `agents/` and
  `skills/`. That is what makes the roles available in every project nested
  under the workbench, not just in one repo.
- `central-context/` holds no code, ever. Executables go in `scripts/`.
- Claude Code loads `agents/` when a session starts. A role added mid-session
  is not available until the next one.
- Run `python3 scripts/check-roles.py` before any commit touching `agents/` or
  `skills/`. Claude Code skips a malformed role file and reports nothing.
