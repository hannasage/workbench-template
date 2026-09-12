---
type: log
updated: 2026-09-12
---
# DECISIONS.md

Append-only decision log. Newest entries at the bottom. Entries are never
edited or deleted. A reversal earns a new entry that supersedes the old one by
date.

The main session writes here, when the owner decides something. No role
does. The rule for what belongs here is in `AGENTS.md`.

An entry is warranted when a choice was settled that a future session would
otherwise re-litigate. Routine work does not earn one. An open question does
not either: that belongs in an `open_items` frontmatter block, which the main
session writes.

Format:

```
### YYYY-MM-DD · Short title
**Decided:** what was chosen, in one sentence.
**Instead of:** the alternatives that were on the table.
**Because:** the reasoning, in one or two sentences.
**Affects:** files or systems this changes.
```

---

### 2026-09-11 · The workbench starts from the template
**Decided:** This workbench is a clone of `workbench-template`, and the
template's example roles and skills stand until someone reads and replaces
them.
**Instead of:** writing the structure from scratch, or deleting the examples
before reading them.
**Because:** the shape is worth keeping and the opinions inside the examples
are not yet this workbench's. Keeping them visible makes the difference
findable. `AGENTS.md#workbench-not-specialised` tracks the pass that resolves
it.
**Affects:** `agents/`, `skills/`, `AGENTS.md`, `central-context/AGENTS.md`.

### 2026-09-12 · Harness wiring is tracked in git, not installed
**Decided:** The symlinks and generated files each harness discovers the
workbench through are committed. Each adapter declares them in a
`wiring.json` manifest, `scripts/sync-harness.py` generates the harness-format
copies from `agents/` and `.mcp.json`, and `scripts/check-harness.py` proves
every link and every copy. `.mcp.json` is the one hand-edited source of MCP
servers.
**Instead of:** a per-harness installer that creates untracked symlinks and
hides them in `.git/info/exclude`, which is what `adapters/claude-code/`
shipped until this date; or a neutral `mcp-servers.json` with `.mcp.json`
symlinked to it.
**Because:** a clone works with no step between clone and session, and a
generated file that is committed can be proved current, which an installer's
output cannot. The neutral-core rule is about what the core names, not what
the tree contains, and a harness's own dot-directory is not the core. The
symlinked-source variant depended on a harness following a symlinked MCP
file, which its documentation does not state.
**Affects:** `adapters/`, `scripts/sync-harness.py`, `scripts/check-harness.py`,
`.mcp.json`, every tracked symlink and generated file at the root,
`prompts/setup.md` stage 0.

### 2026-09-12 · The template ships six research roles and no delivery pipeline
**Decided:** The eight delivery roles are cut. Code and design work routes to
the `superpowers` plugin, installed per harness, and `AGENTS.md` says so under
"How work runs".
**Instead of:** keeping all fourteen roles as a harness-neutral fallback for a
harness with no plugin.
**Because:** the practice this template came from measured the roles at up to
33,000 preloaded tokens and cut them on 2026-09-12 after two design rounds
produced no application code. The plugin is on the marketplaces of both
harnesses this template has an adapter for, and a template that ships a
pipeline its source abandoned is a template that misleads.
**Affects:** `agents/`, `agents/README.md`, `AGENTS.md`, `prompts/setup.md`
stage 2, the routing table.
