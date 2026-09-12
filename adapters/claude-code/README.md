# Claude Code adapter

Claude Code is the one harness in the candidate set that does not read
`AGENTS.md`, so the workbench root carries no file for it. This directory holds
that wiring and nothing else. Delete the directory and the workbench still
works on every other harness.

## Install

Run this from the workbench root:

```bash
bash adapters/claude-code/install.sh
```

The installer prints one line per artifact. Running it twice changes nothing.
Run from any other directory, it writes nothing and exits 1.

## What the installer creates

| Path | What it is | Source | Retrieved |
|---|---|---|---|
| `CLAUDE.md` | Symlink to `AGENTS.md`. The documentation states "Claude Code reads `CLAUDE.md`, not `AGENTS.md`" and gives `ln -s AGENTS.md CLAUDE.md` as the bridge when no harness-specific content is wanted | `https://code.claude.com/docs/en/memory` | 2026-09-11 |
| `.claude/` | The plain directory the next two symlinks live in, created only when it is absent, which is why the installer prints it as a line of its own. It is not a symlink and it holds nothing else | `https://code.claude.com/docs/en/sub-agents` | 2026-09-11 |
| `.claude/agents` | Symlink to `agents/`. Project subagents are discovered in `.claude/agents/`, scanned recursively, walking up from the working directory | `https://code.claude.com/docs/en/sub-agents` | 2026-09-11 |
| `.claude/skills` | Symlink to `skills/`. Project skills are discovered at `.claude/skills/<skill-name>/SKILL.md` | `https://code.claude.com/docs/en/skills` | 2026-09-11 |
| Two lines in `.git/info/exclude` | `/CLAUDE.md` and `/.claude/`, so nothing the installer creates can be committed back into the neutral core. The second pattern also covers the two session-state files the harness writes by itself: `.claude/settings.local.json`, documented as "You, in this one project only", and `.claude/scheduled_tasks.lock`, which the documentation does not mention | `https://code.claude.com/docs/en/settings` | 2026-09-11 |

The installer writes to the per-clone exclude file rather than to the root
`.gitignore`, because a nested `.gitignore` cannot ignore a path at the
repository root and the root `.gitignore` belongs to the neutral core, which
names no harness. The exclude file is per-clone and is never committed, so an
installed workbench still reports a clean tree. The installer asks git for
`--git-common-dir` and not `--git-dir`, because inside a linked worktree the
second one names a per-worktree directory that git does not read ignore
patterns from, and the patterns would be written where they do nothing.

On Windows a symlink needs Administrator rights or Developer Mode. The
documentation gives an import as the alternative there: a hand-written
`CLAUDE.md` holding the line `@AGENTS.md`. The installer does not create that
file (`https://code.claude.com/docs/en/memory`, retrieved 2026-09-11).

## What the installer no longer creates, and what it cost

The table above names three symlinks. The setup before this adapter existed
checked four, and the fourth was `central-context/CLAUDE.md`, a symlink to the
schema file beside it. It was deleted when the workbench root stopped
privileging this harness, and nothing recreates it. Confirmed 2026-09-12 by
running the installer against a fresh clone and reading its output: it creates
the symlinks `CLAUDE.md`, `.claude/agents` and `.claude/skills`, the directory
that holds the last two, and the two exclude lines. There is no fourth
symlink.

What that symlink did is worth stating, because losing it is the one concrete
loss on this harness. A subdirectory instruction file loads on demand when the
harness reads a file in that directory, per the load order above. So a session
that opened anything under `central-context/` used to be handed the page schema
by the harness, with nobody asking for it. Now it is not.

What delivers the schema instead: the routing row in `AGENTS.md` that names
`central-context/AGENTS.md` by path, and each of the five wiki skills naming
that file as a required read before its first write. That is the `reference`
mechanism, and the section below carries the decision behind it and the risk
the owner accepted. This paragraph is the same risk written at the place a
reader counts artifacts.

The decision stands. Do not restore the file and do not add a fourth symlink: a
per-directory instruction file for one harness inside the knowledge base is the
privilege this adapter exists to remove.

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

## Model

Claude models only. Anthropic "doesn't support routing Claude Code to
non-Claude models through any gateway"
(`https://code.claude.com/docs/en/llm-gateway`, retrieved 2026-09-11). The
self-hosted half of the ask belongs to the other adapters.

This adapter ships no configuration file, so it names no model identifier at
all.

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
rm CLAUDE.md .claude/agents .claude/skills
rmdir .claude
```

The two patterns stay in `.git/info/exclude` until they are deleted by hand.
They are per-clone and are never committed.
