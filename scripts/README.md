---
type: index
updated: 2026-09-12
---

# scripts

The flat home for everything executable that is not part of a skill or a
project repo.

A harness is the program that runs the agent loop and reads these files. No
script here names one. A path, a filename, or a setting that belongs to one
harness lives in that harness's adapter, under `adapters/`.

`central-context/` holds no code, by rule. When a check there needs to run
rather than be read, it lives here and `central-context/AGENTS.md` names it by
path.

A script that belongs to one skill stays with that skill, under
`skills/<name>/`. A script that belongs to one project stays in that project's
repo. Everything else is here.

| Script | Does | Run from |
|---|---|---|
| `check-roles.py` | Checks agent and skill frontmatter | The workbench root: `python3 scripts/check-roles.py` |
| `model-registry.txt` | Data, not a script. The values `check-roles.py` accepts in a role's `model:` field. It ships with no values in it | Read by `check-roles.py` |
| `check-open-items.py` | Checks the `open_items` frontmatter of the context files | The workbench root: `python3 scripts/check-open-items.py` |
| `open-items-files.txt` | Data, not a script. The context files `check-open-items.py` reads by default | Read by `check-open-items.py` |
| `sync-harness.py` | Generates, per adapter manifest, the role files and the MCP tables a harness reads in its own format, from `agents/` and `.mcp.json` | The workbench root: `python3 scripts/sync-harness.py`, or `--check` to report and write nothing |
| `check-harness.py` | Proves the wiring: every declared symlink, every skill and role reachable through it, every generated file current, no harness named in the neutral core, and the entrypoint under its size cap | The workbench root: `python3 scripts/check-harness.py` |

## check-roles.py

A harness skips a malformed role file in silence, so this is the only thing
that reports one.

`skills:` in a role file is written inline and comma separated. That is the
only form the checker accepts. A flow list or an indented block list is
reported by name and not parsed. One declared form is a smaller promise than
three parsers, and it is the promise a reader can check.

On roles it checks that frontmatter exists with `---` as the first line, that
`name` matches the filename and is lowercase-hyphen, that `description` is not
empty, that `model` is registered, and that every skill named in `skills:`
exists. On skills it checks that a `SKILL.md` sits directly under
`skills/<dir>/` and not deeper, that no skill directory is empty, that `name`
matches the directory and is lowercase-hyphen, and that `description` is not
empty.

Two things it reports separately:

- **A failure** is a defect. Fix the file.
- **A question** is a `model:` value that is not in `model-registry.txt`. The
  script never checks the shape of such a value, because no two harnesses spell
  a model the same way and a pattern would refuse a spelling somebody's harness
  accepts. So the script cannot tell a typo from a model nobody has registered,
  and it asks instead of ruling. Fix the typo, or add a line to the registry.

Both count toward the exit code, which is their total, capped at 125. That
makes it usable as a pre-commit hook with no wrapper. Nothing calls it
automatically yet. Wiring it into one is a decision for this workbench; open
an item in `AGENTS.md` if you want it tracked.

### The model check does not fire on the shipped tree

`model-registry.txt` ships with no values in it, and no role file in `agents/`
names a model. A model identifier is a fact about one harness and one vendor,
so the neutral core holds none. A run that never reports a question about a
model is waiting for a cloner who pins one. It is not broken.

Where an adapter maps each role to a model, that mapping is the better home for
an identifier, and the registry stays empty. When you do add a value, add one
line with a comment saying what the value is and where you confirmed it. A bare
identifier with no provenance is how a registry rots. The top of
`model-registry.txt` states the form and the two shapes worth registering.

### Exempting somebody else's skill

`THIRD_PARTY_SKILLS` in the script exempts an installed skill whose `name`
differs from the directory it was installed into. The set ships empty, so
nothing is exempt today. That is an exemption from a published standard, not
from a house convention: the Agent Skills specification,
`https://agentskills.io/specification`, read 2026-09-11, states the `name`
field "Must match the parent directory name". A listed skill does not conform.
A harness invokes an installed skill by its directory name, so it still loads,
and the exemption is a decision to tolerate a non-conforming file somebody else
wrote. Everything not listed there is checked, so a skill you wrote is never
skipped by forgetting to register it.

The same specification sets the other name rules the script enforces: 1 to 64
characters, lowercase alphanumeric and hyphens, no leading or trailing hyphen,
no consecutive hyphens. It also publishes a validator, `skills-ref validate`,
which checks a single skill and not the roles, the nesting, or the tree shape
this script covers.

## check-open-items.py

An open item is a question nobody has settled, written into the `open_items`
frontmatter of a context file. This script is the one reader of that block.

One written form is accepted. It is the example block in the `Open items schema`
section of `central-context/AGENTS.md`, which is the authority on the six fields
and on what each one holds. `open_items:` sits at column 0 inside frontmatter,
an item opens at two spaces with `- id:`, the five other keys each sit on their
own line at four spaces in the schema's order, and the `item: >` paragraph sits
at six. Every other form is refused by name, never parsed and never guessed at.
A refusal names the path, the line, the shape found, and the edit that fixes it.
A refused item is dropped whole, so no file is ever half-read while it appears
read.

Three things it reports separately:

- **A failure** is a defect. A refused shape, a path it cannot read, or a file
  that declares `open_items:` and yields no item. Reading nothing is never a
  pass.
- **A question** blocks and says nothing about the file being wrong. There are
  two: no file read declares `open_items:` at all, which almost always means the
  paths are wrong, and an `open_items:` at column 0 outside frontmatter and
  outside a fenced code block, which the script does not read and cannot tell
  from a block somebody wrote in the wrong place.
- **A due item** is one whose `checked` date is older than the cutoff. Nobody has
  tested that claim since the date shown. `wiki-verify` re-tests it in a reading
  pass, so a due item never affects the exit code.

The exit code is the failures plus the questions, capped at 125, so it can run
as a pre-commit hook with no wrapper. Nothing calls it automatically yet.

**On a clean tree it reports 0 failures and 0 questions, and it exits 0.** Any
finding on a tree nobody has just edited is worth reading.

The script ignores every line inside a fenced code block. A fenced example is
documentation, never a declaration. A fence that opens and never closes is a
failure naming the line it opened on, because every line below an open fence
is unread.

With no path argument the script reads the file list at
`scripts/open-items-files.txt`, one path per line. **An item in a file that list
does not name is invisible.** When you write an item into a file the list does
not name, add the line in the same commit. A listed path that no longer exists
is a failure. A path argument checks something else instead, and a directory
argument checks every `*.md` file below it. An entry below it that the
filesystem cannot describe, such as a broken symlink, is a failure too, and it
still counts as a file the run found.

Four options:

- `--findings-only` prints the findings and the counts, and holds back the item
  listing. Mechanical check 1 of `skills/wiki-verify/SKILL.md` calls the script
  this way.
- `--stale-days N` sets the due window, in days since `checked`. Default 14.
- `--today YYYY-MM-DD` sets the run date, for a test.
- `--root PATH` sets the path findings print relative to.

## sync-harness.py

Every path, format identifier and harness fact it uses comes from
`adapters/<id>/wiring.json`, so the script names no harness. A manifest's
`roles` block names a registered format, the directory to write into, and a
mapping file of extra per-role values; its `mcp` block names a format, the
source `.mcp.json`, the path to write, and a hand-edited head to put first.
The generated files are committed. Run the script after any edit to `agents/`,
to `.mcp.json`, or to a mapping or head file, and commit what it wrote.

`--check` writes nothing and exits 1 with one line per file that is missing,
differs from its source, or has no source left. Exit 2 is an input the script
cannot use, named on stderr: an unreadable manifest, a role with no
frontmatter, a mapping naming a role that does not exist, a format nobody
registered, or an MCP server the target format cannot express. It refuses
rather than approximates, because a server rendered differently from its
source is a server that works on one harness and silently not the other.

## check-harness.py

The one command that says whether a clone is wired. One line per failure,
then `N failure(s)`, and the exit code is N capped at 125. It reads the same
manifests as `sync-harness.py`, so an adapter is checked the moment its
manifest exists.

The harness-name scan reads `adapters/harness-names.txt`, strips every
`adapters/<id>/...` path token from a line, and reports every remaining match
in the ten permitted paths of the neutral core. Zero on a clean tree is the
right answer: every sentence in the core that reaches an adapter carries a
path and no harness name. A plain file where a symlink should be gets the
Windows fix in its message.

It proves wiring, not behaviour. Whether a harness loads the entrypoint,
dispatches a role, or completes a wiki operation is the acceptance test below,
which does not exist yet.

## Tests

`tests/` holds the tests for every script here, one file per script. Run them
from the workbench root with `python3 -m unittest discover -s scripts/tests`.
What each file covers is described in its script's module docstring and above.

## Not built yet

`harness-acceptance.py` does not exist on disk on 2026-09-12, so this file does
not say what it does. Add its table row when it lands, written from the script
itself.

One thing about the acceptance test is settled and belongs here, because a
reader who runs it will see failures and wonder whether the suite is broken. It
proves a harness by checking four surfaces: the entrypoint loads without being
asked, one role is dispatched, one skill loads on demand, and one wiki
operation completes end to end. Two runs are expected to fail, and both exist
to show that the test can detect a broken tree.

1. Run against a harness identifier with no adapter installed, the test fails
   at the first surface and names the missing adapter.
2. Run with the skill discovery path removed, the test passes surfaces 1, 2 and
   4 and fails surface 3.

The workbench's specification requires both to be stated as expected behaviour
in the test's own documentation.
