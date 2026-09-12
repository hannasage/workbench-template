# Claude Code adapter

Claude Code is the one harness in the candidate set that does not read
`AGENTS.md`, so the workbench root carries a symlink for it. This directory
holds the manifest that declares that wiring, and nothing else. Delete the
directory and the workbench still works on every other harness, because the
symlinks it declares are tracked in git and need no installer.

## Getting started on this harness

1. Clone the workbench and run the wiring check from its root:

   ```bash
   python3 scripts/check-harness.py
   ```

   `0 failure(s)` means every symlink this adapter declares is in place. On
   Windows, clone with `git clone -c core.symlinks=true` first, and never use
   a zip download, which flattens a symlink into a text file. The check names
   the fix if it finds one.

2. Optional: install the plugin that carries code and design work. The
   workbench routes that work to `superpowers` in `AGENTS.md` under "How work
   runs". From a shell, at user scope:

   ```bash
   claude plugin install superpowers@claude-plugins-official
   ```

   `claude plugin install` "installs to user scope unless you pass `--scope`"
   and loads "the next time you start Claude Code"
   (`https://code.claude.com/docs/en/discover-plugins`, retrieved 2026-09-12).
   Skip this step if the owner does not build software here.

3. Start a session at the workbench root:

   ```bash
   claude
   ```

   A session must start at the root, or the entrypoint does not load. See
   "The instruction filename and its load order" below.

4. Confirm the three surfaces loaded. `/context` lists `CLAUDE.md` under
   memory files and the six roles under custom agents ("check that agents
   appear in `/context` under Custom Agents",
   `https://code.claude.com/docs/en/plugins`, retrieved 2026-09-12). `/plugin`
   shows the plugin from step 2 if you installed it. The twelve skills load on
   demand when a request matches a description; ask for a wiki lint to see one
   fire.

5. Paste `prompts/setup.md` into the session. It walks the specialisation
   pass and ends by running the checks above again.

## What this adapter declares

`wiring.json` beside this file names three symlinks. `scripts/check-harness.py`
reads it and proves each one exists, points where it says, and reaches every
skill and role.

| Path | What it is | Source | Retrieved |
|---|---|---|---|
| `CLAUDE.md` | Symlink to `AGENTS.md`. The documentation states "Claude Code reads `CLAUDE.md`, not `AGENTS.md`" and gives `ln -s AGENTS.md CLAUDE.md` as the bridge when no harness-specific content is wanted | `https://code.claude.com/docs/en/memory` | 2026-09-11 |
| `.claude/agents` | Symlink to `agents/`. Project subagents are discovered in `.claude/agents/`, scanned recursively, walking up from the working directory | `https://code.claude.com/docs/en/sub-agents` | 2026-09-11 |
| `.claude/skills` | Symlink to `skills/`. Project skills are discovered at `.claude/skills/<skill-name>/SKILL.md` | `https://code.claude.com/docs/en/skills` | 2026-09-11 |

Beside the two symlinks, `.claude/.gitignore` keeps the two files this
harness writes during a session out of every commit: `settings.local.json`,
documented as "You, in this one project only", and `scheduled_tasks.lock`,
which the documentation does not mention
(`https://code.claude.com/docs/en/settings`, retrieved 2026-09-11). It also
ignores `worktrees/`, which the harness creates under `.claude/` for an
isolated session. A nested ignore file can ignore paths inside its own
directory, so the root `.gitignore` in the neutral core stays free of any
harness name.

The neutral role files in `agents/` are valid subagents as they stand: `name`,
`description` and `skills` are all documented frontmatter fields. This adapter
therefore generates nothing and carries no mapping file. A `tools:` or
`model:` value, if the owner wants one, is a decision for this workbench and
goes in the role file, where `scripts/check-roles.py` checks it.

MCP servers come from `.mcp.json` at the workbench root, which this harness
reads directly. It ships empty. Add a server there and every harness whose
adapter generates an MCP block picks it up on the next run of
`scripts/sync-harness.py`.

## Permissions

The template ships no permission rules, here or anywhere else in the tree. Every
prompt you get on a read-only command is your own machine asking you, and
answering it once or writing a rule that stops it asking is yours to decide. The
syntax for `allow`, `ask` and `deny`, and the file each rule belongs in, are at
`https://code.claude.com/docs/en/permissions` ("Configure permissions",
retrieved 2026-09-11). No example rule set appears here, because an example is a
posture with a disclaimer on it.

## The instruction filename and its load order

All of this is from `https://code.claude.com/docs/en/memory`, retrieved
2026-09-11.

The filename is `CLAUDE.md`. Four scopes load, in this order, from the broadest
to the most specific, so the most specific is read last:

1. Managed policy: `/Library/Application Support/ClaudeCode/CLAUDE.md` on
   macOS, `/etc/claude-code/CLAUDE.md` on Linux and WSL,
   `C:\Program Files\ClaudeCode\CLAUDE.md` on Windows.
2. User: `~/.claude/CLAUDE.md`.
3. Project: `./CLAUDE.md` or `./.claude/CLAUDE.md`.
4. Local: `./CLAUDE.local.md`.

Inside the directory tree, every `CLAUDE.md` from the filesystem root down to
the working directory loads at launch, ordered root first, and all of them are
concatenated rather than one overriding another. A `CLAUDE.md` in a
subdirectory below the working directory loads on demand, when the harness
reads a file in that directory. In one directory, `CLAUDE.local.md` is appended
after `CLAUDE.md`.

Two consequences for this workbench. A session must start at the workbench
root, or the root entrypoint does not load. And no file below the root, the
page schema included, is loaded at session start.

## The page schema arrives by reference, not by inclusion

The choice, settled by the owner on 2026-09-11: this adapter does not import
`central-context/AGENTS.md`. Its `CLAUDE.md` is a plain symlink to `AGENTS.md`
and carries nothing else. The session reads the page schema when the routing
row for the wiki's layout matches, which is the same mechanism every other
adapter uses.

The reason: this harness is the only one in the set with a documented import,
and using it would load the whole schema file into every session whether the
session touches the wiki or not. One mechanism across every adapter stops the
template privileging one harness.

The accepted risk: delivery now depends on the session following the routing
row. Nothing enforces it.

The mechanism this adapter declines is real and documented. A `CLAUDE.md` can
import with `@path/to/import`, imported files load into context at launch, and
imports recurse to a maximum depth of four hops
(`https://code.claude.com/docs/en/memory`, retrieved 2026-09-11). The support
matrix value for this adapter's schema column is therefore `reference`.

There is no `central-context/CLAUDE.md`. A per-directory instruction file for
one harness inside the knowledge base is the privilege this adapter exists to
remove. Do not add one.

## Model

Claude models only. Anthropic "doesn't support routing Claude Code to
non-Claude models through any gateway"
(`https://code.claude.com/docs/en/llm-gateway`, retrieved 2026-09-11). The
self-hosted half of the ask belongs to the other adapters.

This adapter ships no configuration file, so it names no model identifier at
all.

## Wiring check

`python3 scripts/check-harness.py` ran clean on this adapter's three symlinks
on 2026-09-12, on the tree this file was committed in. That proves the wiring,
not the behaviour below.

## Acceptance surfaces

No run has happened on this adapter. Every cell below reads `not tested` and
stays that way until one does. A result is recorded from a transcript, never
inferred.

| Surface | What passes | Result |
|---|---|---|
| 1. The entrypoint loads unprompted | The root entrypoint's unique token appears in the first reply, with no tool call before it | not tested |
| 2. One role is dispatched | The probe role writes its file, its contents match exactly, and the main session never read the role file | not tested |
| 3. One skill loads on demand | The probe skill's token appears in the reply, and the main session never read its `SKILL.md` | not tested |
| 4. One real wiki operation | An ingest satisfies all five mechanical conditions: the raw file, the new page's frontmatter, resolving wikilinks, the index line, and the log line | not tested |

| Field | Value |
|---|---|
| Harness name | Claude Code |
| Harness version | not tested |
| Model identifier | not tested |
| Serving stack | not tested |
| Date of run | not tested |
| Tool calls in the transcript | not tested |
| Failed tool calls | not tested |
| Path each surface resolved from | not tested |

A pass another harness's configuration produced is not a pass. This harness's
user-scope files, `~/.claude/CLAUDE.md` and `~/.claude/skills/`, load whatever
the project holds, so a run records the absolute path each surface resolved
from and fails any path outside the workbench.

## Removing the adapter

```bash
git rm CLAUDE.md .claude/agents .claude/skills .claude/.gitignore
git rm -r adapters/claude-code
```

`scripts/check-harness.py` then has no manifest for this harness and checks
nothing for it.
